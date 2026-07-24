'use client';

import { FormEvent, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

type SkillGroup = {
  category: string;
  weight: string;
  skills: string[];
};

type AssessmentResult = {
  score: number;
  level: string;
  label?: string;
  summary?: string;
  top_skill?: string;
  missing_key_skill?: string;
  explanation?: string;
  score_source?: string;
};

type DBRoleOption = {
  id: string;
  name: string;
  department: string;
  salary: string;
  levels: string[];
  requiredSkills: string[];
  matchPercent: number;
  tag: string;
};

const DB_ROLES: Omit<DBRoleOption, 'matchPercent' | 'tag'>[] = [
  { id: 'db-risk', name: 'Risk Management', department: 'Risk', salary: '€48k–200k/year', levels: ['Analyst','Associate','AVP','VP','MD'], requiredSkills: ['Risk Management', 'Python', 'Excel', 'SQL', 'Financial Modelling'] },
  { id: 'db-technology', name: 'Technology & Engineering', department: 'Technology', salary: '€48k–180k/year', levels: ['Analyst','Associate','AVP','VP','MD'], requiredSkills: ['Python', 'SQL', 'API Development', 'Agile', 'Cloud'] },
  { id: 'db-compliance', name: 'Compliance & Regulatory', department: 'Compliance', salary: '€44k–160k/year', levels: ['Analyst','Associate','AVP','VP','MD'], requiredSkills: ['AML', 'KYC', 'Regulatory Compliance', 'Risk Assessment', 'Excel'] },
  { id: 'db-quant', name: 'Quantitative Finance', department: 'Quant', salary: '£55k–220k/year', levels: ['Analyst','Associate','AVP','VP','MD'], requiredSkills: ['Python', 'Statistics', 'Derivatives Pricing', 'Monte Carlo', 'Machine Learning'] },
  { id: 'db-product', name: 'Product Management', department: 'Product', salary: '€46k–170k/year', levels: ['Analyst','Associate','AVP','VP','MD'], requiredSkills: ['Product Management', 'Agile', 'Stakeholder Management', 'Analytics', 'Roadmapping'] },
  { id: 'db-cloud', name: 'Cloud Engineering', department: 'Cloud', salary: '€52k–190k/year', levels: ['Analyst','Associate','AVP','VP','MD'], requiredSkills: ['AWS', 'Azure', 'Terraform', 'Kubernetes', 'Python'] },
  { id: 'db-ml', name: 'Machine Learning & AI', department: 'ML', salary: '£55k–210k/year', levels: ['Analyst','Associate','AVP','VP','MD'], requiredSkills: ['Python', 'Machine Learning', 'TensorFlow', 'Statistics', 'MLOps'] },
  { id: 'db-data', name: 'Data Engineering & Analytics', department: 'Data', salary: '€46k–210k/year', levels: ['Analyst','Associate','AVP','VP','MD'], requiredSkills: ['SQL', 'Python', 'ETL', 'Data Pipeline', 'Apache Spark'] },
];

const buildDBRoleCatalog = (selectedSkills: string[]): DBRoleOption[] => {
  const normalizedSelected = new Set(
    selectedSkills.filter(s => s && !s.includes(':None') && s !== 'None').map(s => s.toLowerCase())
  );
  return DB_ROLES.map(role => {
    const matched = role.requiredSkills.filter(s =>
      normalizedSelected.has(s.toLowerCase()) ||
      [...normalizedSelected].some(u => u.includes(s.toLowerCase().split(' ')[0]))
    ).length;
    const matchPercent = Math.round((matched / role.requiredSkills.length) * 100);
    const tag = matchPercent >= 60 ? '🎯 Best Match' : matchPercent >= 30 ? '✅ Good Fit' : '📈 Stretch Goal';
    return { ...role, matchPercent, tag };
  }).sort((a, b) => b.matchPercent - a.matchPercent);
};


export default function OnboardingClient() {
  const router = useRouter();
  const [step, setStep] = useState<'path-select' | 'path-details' | 'skills' | 'career-paths'>('path-select');
  const [selectedPath, setSelectedPath] = useState<'A' | 'B' | 'C' | null>(null);
  const [name, setName] = useState('');
  const [skillGroups, setSkillGroups] = useState<SkillGroup[]>([]);
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  // Path A
  const [currentDbPosition, setCurrentDbPosition] = useState('');
  const [currentDbDepartment, setCurrentDbDepartment] = useState('');
  const [currentDesignation, setCurrentDesignation] = useState('analyst');
  // Path B
  const [currentCompany, setCurrentCompany] = useState('');
  const [currentExternalRole, setCurrentExternalRole] = useState('');
  // Path C
  const [education, setEducation] = useState('');
  const [certifications, setCertifications] = useState('');
  const [experienceYears, setExperienceYears] = useState<number | ''>('');
  // Shared
  const [targetDbRole, setTargetDbRole] = useState('db-technology');
  const [assessmentResult, setAssessmentResult] = useState<AssessmentResult | null>(null);
  const [careerPaths, setCareerPaths] = useState<DBRoleOption[]>([]);
  const [selectedCareerPath, setSelectedCareerPath] = useState('');
  const [weeklyHours, setWeeklyHours] = useState(5);

  useEffect(() => {
    const token = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_token') : null;
    if (!token) { router.replace('/login'); return; }
    const storedName = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_user_name') : '';
    if (storedName) setName(storedName);
    api.get('/api/assessment/skills').then(r => setSkillGroups(r.data)).catch(() => setSkillGroups([]));
  }, [router]);

  const toggleSkill = (skill: string, category?: string) => {
    const key = category && skill === 'None' ? `${category}:${skill}` : skill;
    setSelectedSkills(prev => prev.includes(key) ? prev.filter(s => s !== key) : [...prev, key]);
  };

  const handlePathSelect = (path: 'A' | 'B' | 'C') => {
    setSelectedPath(path);
    setStep('path-details');
  };

  const handlePathDetailsSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    if (!name.trim()) { setError('Please enter your name.'); return; }
    setLoading(true);
    try {
      const employment = selectedPath === 'A' ? 'db-employee' : selectedPath === 'B' ? 'external' : 'unemployed';
      await api.post('/api/user/profile', {
        name,
        employment_status: employment,
        user_path: selectedPath,
        target_role: selectedPath === 'C' ? 'db-technology' : targetDbRole,
        current_db_position: currentDbPosition || null,
        current_db_department: currentDbDepartment || null,
        current_designation: currentDesignation || null,
        current_company: currentCompany || null,
        current_external_role: currentExternalRole || null,
        education: education || null,
        certifications: certifications || null,
        experience_years: experienceYears || null,
      });
      if (typeof window !== 'undefined') window.localStorage.setItem('skillbridge_user_name', name);
      setStep('skills');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to save profile');
    } finally {
      setLoading(false);
    }
  };

  const handleSkillsSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    const skillsToSubmit = selectedSkills.filter(s => !s.includes(':None') && s !== 'None');
    if (!skillsToSubmit.length) { setError('Select at least one skill to continue.'); return; }
    setLoading(true);
    try {
      const goal = selectedPath === 'C' ? 'db-technology' : targetDbRole;
      const employment = selectedPath === 'A' ? 'db-employee' : selectedPath === 'B' ? 'external' : 'unemployed';
      const response = await api.post('/api/assessment/submit-skills', { skills: skillsToSubmit, goal, employment_status: employment });
      const result = response.data;
      setAssessmentResult(result);
      if (typeof window !== 'undefined') {
        window.localStorage.setItem('skillbridge_assessment_result', JSON.stringify(result));
        window.localStorage.setItem('skillbridge_selected_skills', JSON.stringify(skillsToSubmit));
        window.localStorage.setItem('skillbridge_target_role', goal);
      }
      if (selectedPath === 'C') {
        const catalog = buildDBRoleCatalog(skillsToSubmit);
        setCareerPaths(catalog.slice(0, 5));
        setSelectedCareerPath(catalog[0]?.id || 'db-technology');
        setStep('career-paths');
      } else {
        const dataStr = encodeURIComponent(JSON.stringify(result));
        router.push(`/onboarding/assessment-complete?data=${dataStr}`);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to calculate your score');
    } finally {
      setLoading(false);
    }
  };

  const handleCareerPathContinue = async () => {
    if (!selectedCareerPath) { setError('Select a career path to continue.'); return; }
    setLoading(true);
    try {
      await api.post('/api/user/profile', {
        target_role: selectedCareerPath,
        weekly_hours: weeklyHours,
        current_level: assessmentResult?.level || 'beginner',
      });
      if (typeof window !== 'undefined') window.localStorage.setItem('skillbridge_target_role', selectedCareerPath);
      router.push('/onboarding/ai-learning-path');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to save your career path');
    } finally {
      setLoading(false);
    }
  };

  const scoreLabel = selectedPath === 'A' ? 'DB Career Score' : selectedPath === 'B' ? 'DB Career Score' : 'Employability Score';
  const pathLabel = selectedPath === 'A' ? 'DB Employee — Internal Mobility' : selectedPath === 'B' ? 'External Candidate — Join Deutsche Bank' : 'Job Seeker — Start Your DB Journey';

  if (loading && step !== 'skills') {
    return <main className="flex min-h-screen items-center justify-center bg-[#001F4D] text-lg text-white">Processing…</main>;
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#001F4D] via-[#003080] to-[#001F4D] px-4 py-10 text-slate-100">
      <div className="mx-auto max-w-4xl space-y-6">
        {/* DB header */}
        <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-6 py-4 backdrop-blur">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#FFD700] text-[#001F4D] font-bold text-lg">DB</div>
            <span className="font-semibold text-white">DB AI Career Navigator</span>
          </div>
          {selectedPath && (
            <span className="rounded-full border border-[#FFD700]/30 bg-[#FFD700]/10 px-3 py-1 text-xs font-semibold text-[#FFD700]">{pathLabel}</span>
          )}
        </div>

        {/* STEP 1: PATH SELECT */}
        {step === 'path-select' && (
          <div className="space-y-6">
            <div className="rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur">
              <h1 className="text-3xl font-semibold text-white">Welcome to Deutsche Bank AI Career Navigator</h1>
              <p className="mt-3 text-slate-300">Tell us where you are today. We will build a personalised Deutsche Bank readiness plan for your situation.</p>
            </div>
            <div className="grid gap-4 md:grid-cols-3">
              <button type="button" onClick={() => handlePathSelect('A')} className="group rounded-3xl border border-[#0066CC]/40 bg-[#0066CC]/10 p-6 text-left transition hover:border-[#0066CC] hover:bg-[#0066CC]/20">
                <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-[#0066CC] text-white text-xl font-bold">A</div>
                <h2 className="text-lg font-semibold text-white">I work at Deutsche Bank</h2>
                <p className="mt-2 text-sm text-slate-300">Grow your career inside Deutsche Bank — plan your next internal move</p>
                <ul className="mt-4 space-y-1 text-xs text-slate-400"><li>• DB Career Score</li><li>• Skill gap vs target role</li><li>• Internal advancement paths</li></ul>
              </button>
              <button type="button" onClick={() => handlePathSelect('B')} className="group rounded-3xl border border-emerald-500/40 bg-emerald-500/10 p-6 text-left transition hover:border-emerald-500 hover:bg-emerald-500/20">
                <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-600 text-white text-xl font-bold">B</div>
                <h2 className="text-lg font-semibold text-white">I want to join Deutsche Bank</h2>
                <p className="mt-2 text-sm text-slate-300">Plan your transition into Deutsche Bank from your current company</p>
                <ul className="mt-4 space-y-1 text-xs text-slate-400"><li>• DB Career Score</li><li>• Skill comparison vs DB roles</li><li>• DB openings with match %</li></ul>
              </button>
              <button type="button" onClick={() => handlePathSelect('C')} className="group rounded-3xl border border-[#FFD700]/40 bg-[#FFD700]/10 p-6 text-left transition hover:border-[#FFD700] hover:bg-[#FFD700]/20">
                <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-[#FFD700] text-[#001F4D] text-xl font-bold">C</div>
                <h2 className="text-lg font-semibold text-white">I am looking for opportunities</h2>
                <p className="mt-2 text-sm text-slate-300">Start your journey — build skills and unlock Deutsche Bank opportunities</p>
                <ul className="mt-4 space-y-1 text-xs text-slate-400"><li>• Employability Score</li><li>• Tailored career paths</li><li>• Jobs unlock at score ≥ 60</li></ul>
              </button>
            </div>
          </div>
        )}

        {/* STEP 2: PATH DETAILS */}
        {step === 'path-details' && selectedPath && (
          <div className="rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur">
            <div className="mb-4 flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 p-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-widest text-slate-400">Your Path</p>
                <p className="mt-1 text-base font-semibold text-white">
                  {selectedPath === 'A' ? '🏢 Working at Deutsche Bank' : selectedPath === 'B' ? '🌍 Joining Deutsche Bank' : '🚀 Looking for Opportunities'}
                </p>
              </div>
              <button type="button" onClick={() => setStep('path-select')} className="text-sm font-medium text-slate-400 hover:text-slate-300">Change</button>
            </div>
            <p className="text-sm font-semibold uppercase tracking-widest text-[#FFD700]">Step 2 — Your Background</p>
            <h1 className="mt-2 text-3xl font-semibold text-white">
              {selectedPath === 'A' ? 'Tell us about your DB role' : selectedPath === 'B' ? 'Tell us about your background' : 'Tell us about your experience'}
            </h1>
            <form onSubmit={handlePathDetailsSubmit} className="mt-6 space-y-5">
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-300">Your full name</label>
                <input value={name} onChange={e => setName(e.target.value)} placeholder="Anna Schmidt" className="w-full rounded-xl border border-white/20 bg-white/5 px-4 py-3 text-white placeholder-slate-500 focus:border-[#0066CC] focus:outline-none" />
              </div>
              {selectedPath === 'A' && (
                <>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <label className="mb-1 block text-sm font-medium text-slate-300">Current DB position</label>
                      <input value={currentDbPosition} onChange={e => setCurrentDbPosition(e.target.value)} placeholder="e.g. Risk Analyst" className="w-full rounded-xl border border-white/20 bg-white/5 px-4 py-3 text-white placeholder-slate-500 focus:border-[#0066CC] focus:outline-none" />
                    </div>
                    <div>
                      <label className="mb-1 block text-sm font-medium text-slate-300">Current DB department</label>
                      <input value={currentDbDepartment} onChange={e => setCurrentDbDepartment(e.target.value)} placeholder="e.g. Risk, Technology" className="w-full rounded-xl border border-white/20 bg-white/5 px-4 py-3 text-white placeholder-slate-500 focus:border-[#0066CC] focus:outline-none" />
                    </div>
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-slate-300">Your current designation level</label>
                    <select value={currentDesignation} onChange={e => setCurrentDesignation(e.target.value)} className="w-full rounded-xl border border-white/20 bg-[#001F4D] px-4 py-3 text-white focus:border-[#0066CC] focus:outline-none">
                      <option value="analyst">Analyst (Entry level)</option>
                      <option value="associate">Associate (3-6 years)</option>
                      <option value="avp">AVP - Assistant Vice President (6-15 years)</option>
                      <option value="vp">VP - Vice President (15-25 years)</option>
                      <option value="director">Director / MD (25+ years)</option>
                    </select>
                    <p className="mt-2 text-xs text-slate-400">Deutsche Bank career progression: Analyst → Associate → AVP → VP → Director</p>
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-slate-300">Target DB role</label>
                    <select value={targetDbRole} onChange={e => setTargetDbRole(e.target.value)} className="w-full rounded-xl border border-white/20 bg-[#001F4D] px-4 py-3 text-white focus:border-[#0066CC] focus:outline-none">
                      {DB_ROLES.map(r => <option key={r.id} value={r.id}>{r.name} ({r.department})</option>)}
                    </select>
                  </div>
                </>
              )}
              {selectedPath === 'B' && (
                <>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <label className="mb-1 block text-sm font-medium text-slate-300">Current employer</label>
                      <input value={currentCompany} onChange={e => setCurrentCompany(e.target.value)} placeholder="e.g. HSBC, Barclays" className="w-full rounded-xl border border-white/20 bg-white/5 px-4 py-3 text-white placeholder-slate-500 focus:border-[#0066CC] focus:outline-none" />
                    </div>
                    <div>
                      <label className="mb-1 block text-sm font-medium text-slate-300">Current role</label>
                      <input value={currentExternalRole} onChange={e => setCurrentExternalRole(e.target.value)} placeholder="e.g. Senior Analyst" className="w-full rounded-xl border border-white/20 bg-white/5 px-4 py-3 text-white placeholder-slate-500 focus:border-[#0066CC] focus:outline-none" />
                    </div>
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-slate-300">Your current designation level</label>
                    <select value={currentDesignation} onChange={e => setCurrentDesignation(e.target.value)} className="w-full rounded-xl border border-white/20 bg-[#001F4D] px-4 py-3 text-white focus:border-[#0066CC] focus:outline-none">
                      <option value="analyst">Analyst (Entry level)</option>
                      <option value="associate">Associate (3-6 years)</option>
                      <option value="avp">AVP - Assistant Vice President (6-15 years)</option>
                      <option value="vp">VP - Vice President (15-25 years)</option>
                      <option value="director">Director / MD (25+ years)</option>
                    </select>
                    <p className="mt-2 text-xs text-slate-400">Deutsche Bank career progression: Analyst → Associate → AVP → VP → Director</p>
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-slate-300">Target Deutsche Bank role</label>
                    <select value={targetDbRole} onChange={e => setTargetDbRole(e.target.value)} className="w-full rounded-xl border border-white/20 bg-[#001F4D] px-4 py-3 text-white focus:border-[#0066CC] focus:outline-none">
                      {DB_ROLES.map(r => <option key={r.id} value={r.id}>{r.name} ({r.department})</option>)}
                    </select>
                  </div>
                </>
              )}
              {selectedPath === 'C' && (
                <>
                  <div className="rounded-2xl border border-[#FFD700]/30 bg-[#FFD700]/10 p-4">
                    <p className="text-sm text-slate-300"><span className="font-semibold text-[#FFD700]">💡 How it works:</span> Based on your experience, we'll determine your starting designation and show you relevant Deutsche Bank jobs.</p>
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-slate-300">Years of experience</label>
                    <input value={experienceYears as number | string} onChange={e => setExperienceYears(e.target.value ? Number(e.target.value) : '')} type="number" min="0" max="40" placeholder="0" className="w-full rounded-xl border border-white/20 bg-white/5 px-4 py-3 text-white placeholder-slate-500 focus:border-[#0066CC] focus:outline-none" />
                    <p className="mt-2 text-xs text-slate-400">
                      {experienceYears && !isNaN(Number(experienceYears)) ? (
                        <>
                          {Number(experienceYears) < 3 && `📊 Your level: Analyst — Perfect for entry-level DB opportunities`}
                          {Number(experienceYears) >= 3 && Number(experienceYears) < 6 && `📊 Your level: Associate — Ready for mid-level DB roles`}
                          {Number(experienceYears) >= 6 && Number(experienceYears) < 15 && `📊 Your level: AVP — Eligible for senior DB positions`}
                          {Number(experienceYears) >= 15 && Number(experienceYears) < 25 && `📊 Your level: VP — Ready for VP-level DB roles`}
                          {Number(experienceYears) >= 25 && `📊 Your level: Director — Executive-level DB opportunities`}
                        </>
                      ) : (
                        <>0-3 years → Analyst | 3-6 years → Associate | 6-15 years → AVP | 15-25 years → VP | 25+ years → Director</>
                      )}
                    </p>
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-slate-300">Education (highest qualification)</label>
                    <input value={education} onChange={e => setEducation(e.target.value)} placeholder="e.g. BSc Computer Science, MSc Finance" className="w-full rounded-xl border border-white/20 bg-white/5 px-4 py-3 text-white placeholder-slate-500 focus:border-[#0066CC] focus:outline-none" />
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-slate-300">Certifications (optional)</label>
                    <input value={certifications} onChange={e => setCertifications(e.target.value)} placeholder="e.g. CFA Level 1, AWS Solutions Architect" className="w-full rounded-xl border border-white/20 bg-white/5 px-4 py-3 text-white placeholder-slate-500 focus:border-[#0066CC] focus:outline-none" />
                  </div>
                </>
              )}
              {error && <p className="text-sm text-rose-400">{error}</p>}
              <div className="flex gap-3">
                <button type="button" onClick={() => setStep('path-select')} className="rounded-xl border border-white/20 px-5 py-3 text-sm font-semibold text-slate-300">← Back</button>
                <button type="submit" disabled={loading} className="flex-1 rounded-xl bg-[#0066CC] px-5 py-3 font-semibold text-white disabled:opacity-50">{loading ? 'Saving…' : 'Continue to skill snapshot →'}</button>
              </div>
            </form>
          </div>
        )}

        {/* STEP 3: SKILLS */}
        {step === 'skills' && (
          <div className="rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur">
            <p className="text-sm font-semibold uppercase tracking-widest text-[#FFD700]">Step 3 — Skill Snapshot</p>
            <h1 className="mt-2 text-3xl font-semibold text-white">What skills do you already have?</h1>
            <p className="mt-2 text-slate-300">Select your current skills. AI will compute your {scoreLabel} and identify gaps against Deutsche Bank requirements.</p>
            <form onSubmit={handleSkillsSubmit} className="mt-6 space-y-4">
              {skillGroups.length === 0 ? (
                <div className="rounded-xl border border-white/10 bg-white/5 p-4 text-sm text-slate-400">Loading skill categories…</div>
              ) : (
                skillGroups.map(group => (
                  <div key={group.category} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-white">{group.category}</h3>
                      <span className="rounded-full bg-white/10 px-2 py-1 text-xs text-slate-400">{group.weight}</span>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {group.skills.map(skill => {
                        const key = skill === 'None' ? `${group.category}:${skill}` : skill;
                        const checked = selectedSkills.includes(key);
                        return (
                          <button key={key} type="button" onClick={() => toggleSkill(skill, group.category)}
                            className={`rounded-full border px-3 py-1 text-sm font-medium transition ${checked ? 'border-[#0066CC] bg-[#0066CC]/20 text-[#66B2FF]' : 'border-white/20 bg-white/5 text-slate-300 hover:border-white/40'}`}>
                            {checked ? '✓ ' : ''}{skill}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ))
              )}
              {error && <p className="text-sm text-rose-400">{error}</p>}
              <div className="flex gap-3">
                <button type="button" onClick={() => setStep('path-details')} className="rounded-xl border border-white/20 px-5 py-3 text-sm font-semibold text-slate-300">← Back</button>
                <button type="submit" disabled={loading || selectedSkills.filter(s => !s.includes(':None')).length === 0}
                  className="flex-1 rounded-xl bg-[#0066CC] px-5 py-3 font-semibold text-white disabled:opacity-50">
                  {loading ? 'Calculating your score…' : `Calculate ${scoreLabel} →`}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* STEP 4: CAREER PATHS (Path C only) */}
        {step === 'career-paths' && selectedPath === 'C' && (
          <div className="rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur">
            <p className="text-sm font-semibold uppercase tracking-widest text-[#FFD700]">Step 4 — Choose Your DB Career Path</p>
            <h1 className="mt-2 text-3xl font-semibold text-white">Your AI-Generated DB Career Paths</h1>
            <div className="mt-3 flex items-center gap-3 rounded-2xl border border-[#FFD700]/20 bg-[#FFD700]/10 px-4 py-3">
              <span className="text-3xl font-bold text-[#FFD700]">{assessmentResult?.score ?? 0}</span>
              <div>
                <p className="text-sm font-semibold text-white">Employability Score</p>
                <p className="text-xs text-slate-400">
                  {(assessmentResult?.score ?? 0) >= 60 ? '✅ Job search unlocked!' : `Reach 60 to unlock Deutsche Bank job applications (${60 - (assessmentResult?.score ?? 0)} points away)`}
                </p>
              </div>
            </div>
            <p className="mt-4 text-slate-300">Based on your skills, here are the best-matched Deutsche Bank career paths. Select one to build your personalised DB learning roadmap.</p>
            <div className="mt-5 space-y-3">
              {careerPaths.map(path => (
                <button key={path.id} type="button" onClick={() => setSelectedCareerPath(path.id)}
                  className={`w-full rounded-2xl border p-4 text-left transition ${selectedCareerPath === path.id ? 'border-[#0066CC] bg-[#0066CC]/20' : 'border-white/10 bg-white/5 hover:border-white/30'}`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-white">{path.name}</span>
                        <span className="rounded-full bg-white/10 px-2 py-0.5 text-xs text-slate-300">{path.department}</span>
                        <span className="text-xs font-semibold text-[#FFD700]">{path.tag}</span>
                      </div>
                      <p className="mt-1 text-sm text-slate-400">{path.salary} • {path.levels.join(' → ')}</p>
                      <p className="mt-1 text-xs text-slate-500">Key skills: {path.requiredSkills.slice(0, 3).join(', ')}</p>
                    </div>
                    <div className="ml-4 text-right">
                      <p className="text-2xl font-bold text-white">{path.matchPercent}%</p>
                      <p className="text-xs text-slate-400">match</p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
            <div className="mt-5">
              <label className="mb-1 block text-sm font-medium text-slate-300">Weekly hours available for learning</label>
              <select value={weeklyHours} onChange={e => setWeeklyHours(Number(e.target.value))} className="w-full rounded-xl border border-white/20 bg-[#001F4D] px-4 py-3 text-white focus:border-[#0066CC] focus:outline-none">
                <option value={5}>5 hours/week</option>
                <option value={8}>8 hours/week</option>
                <option value={10}>10 hours/week</option>
                <option value={15}>15 hours/week</option>
              </select>
            </div>
            {error && <p className="mt-3 text-sm text-rose-400">{error}</p>}
            <button onClick={handleCareerPathContinue} disabled={loading || !selectedCareerPath}
              className="mt-5 w-full rounded-xl bg-[#FFD700] px-5 py-3 font-semibold text-[#001F4D] disabled:opacity-50">
              {loading ? 'Building your DB roadmap…' : 'Build my Deutsche Bank Learning Roadmap →'}
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
