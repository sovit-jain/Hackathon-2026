'use client';

import { FormEvent, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import api from '@/lib/api';
import BackButton from '@/components/BackButton';

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

type RoleOption = {
  id: string;
  name: string;
  salary: string;
  job_market: string;
  requiredSkills: string[];
  minScore: number;
  matchPercent: number;
  tag: string;
  hint: string;
};

const normalizeSkill = (skill: string) => {
  const normalized = skill.trim().toLowerCase();
  if (normalized.includes('excel')) return 'ms excel';
  if (normalized.includes('powerpoint') || normalized.includes('ppt')) return 'powerpoint';
  if (normalized.includes('data analysis') || normalized.includes('analysis')) return 'data analysis';
  if (normalized.includes('ml')) return 'ml';
  if (normalized.includes('cloud')) return 'cloud';
  return normalized;
};

const buildRoleCatalog = (selectedSkills: string[], score: number): RoleOption[] => {
  const normalizedSelectedSkills = new Set(
    selectedSkills
      .filter((skill) => !!skill && !skill.includes(':None') && skill !== 'None')
      .map((skill) => normalizeSkill(skill))
  );

  const roles: Omit<RoleOption, 'matchPercent' | 'tag' | 'hint'>[] = [
    {
      id: 'tech-support',
      name: 'Tech Support',
      salary: '€22,000 - €32,000/year',
      job_market: '6,700 open positions',
      requiredSkills: ['MS Excel', 'English', 'MS Word'],
      minScore: 20,
    },
    {
      id: 'data-analyst',
      name: 'Data Analyst',
      salary: '€25,000 - €35,000/year',
      job_market: '2,300 open positions',
      requiredSkills: ['SQL', 'Data Analysis', 'MS Excel'],
      minScore: 30,
    },
    {
      id: 'business-analyst',
      name: 'Business Analyst',
      salary: '€30,000 - €45,000/year',
      job_market: '5,100 open positions',
      requiredSkills: ['Data Analysis', 'MS Excel', 'PowerPoint'],
      minScore: 40,
    },
    {
      id: 'python-developer',
      name: 'Python Developer',
      salary: '€35,000 - €55,000/year',
      job_market: '8,900 open positions',
      requiredSkills: ['Python', 'SQL'],
      minScore: 50,
    },
    {
      id: 'data-engineer',
      name: 'Data Engineer',
      salary: '€40,000 - €60,000/year',
      job_market: '3,200 open positions',
      requiredSkills: ['Python', 'SQL', 'Cloud'],
      minScore: 65,
    },
    {
      id: 'ml-engineer',
      name: 'ML Engineer',
      salary: '€55,000 - €85,000/year',
      job_market: '1,800 open positions',
      requiredSkills: ['ML', 'Python', 'Cloud'],
      minScore: 80,
    },
  ];

  return roles
    .map((role) => {
      const matchedSkills = role.requiredSkills.filter((skill) => normalizedSelectedSkills.has(normalizeSkill(skill))).length;
      const matchPercent = Math.round((matchedSkills / role.requiredSkills.length) * 100);
      const tag = matchPercent >= 60 ? '🎯 Best Match' : matchPercent >= 30 ? '✅ Good Fit' : '📈 Stretch Goal';
      const hint = matchPercent >= 60
        ? 'Strong fit for your current foundation.'
        : matchPercent >= 30
          ? 'A good next step if you keep building.'
          : 'A stretch goal that can unlock with more practice.';

      return {
        ...role,
        matchPercent,
        tag,
        hint,
      };
    })
    .sort((a, b) => b.matchPercent - a.matchPercent);
};

export default function OnboardingPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [skillGroups, setSkillGroups] = useState<SkillGroup[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState<'profile' | 'assessment' | 'dream-job'>('profile');
  const [name, setName] = useState('');
  const [age, setAge] = useState<number | ''>('');
  const [employmentStatus, setEmploymentStatus] = useState('unemployed');
  const [assessmentResult, setAssessmentResult] = useState<AssessmentResult | null>(null);
  const [scoreCalculated, setScoreCalculated] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDreamJob, setSelectedDreamJob] = useState('data-analyst');
  const [weeklyHours, setWeeklyHours] = useState(5);
  const [roleOptions, setRoleOptions] = useState<RoleOption[]>(() => buildRoleCatalog([], 0));

  useEffect(() => {
    const token = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_token') : null;
    if (!token) {
      router.replace('/login');
      return;
    }

    // Check for step parameter in URL
    const stepParam = searchParams.get('step');
    if (stepParam === 'dream-job') {
      setStep('dream-job');
    }

    const storedName = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_user_name') : '';
    if (storedName) {
      setName(storedName);
    }

    const storedAssessment = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_assessment_result') : null;
    if (storedAssessment) {
      try {
        setAssessmentResult(JSON.parse(storedAssessment));
      } catch {
        // Ignore invalid cached assessment data.
      }
    }

    const storedSelectedSkills = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_selected_skills') : null;
    if (storedSelectedSkills) {
      try {
        setSelectedSkills(JSON.parse(storedSelectedSkills));
      } catch {
        // Ignore invalid cached skills.
      }
    }

    const storedTargetRole = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_target_role') : null;
    if (storedTargetRole) {
      setSelectedDreamJob(storedTargetRole);
    }

    const loadProfileSelection = async () => {
      try {
        const response = await api.get('/api/user/profile');
        const profileRole = response.data?.profile?.target_role;
        if (profileRole) {
          setSelectedDreamJob(profileRole);
          if (typeof window !== 'undefined') {
            window.localStorage.setItem('skillbridge_target_role', profileRole);
          }
        }
      } catch {
        // Ignore profile fetch issues and fall back to local storage.
      }
    };

    const loadSkills = async () => {
      try {
        const response = await api.get('/api/assessment/skills');
        setSkillGroups(response.data);
      } catch {
        setSkillGroups([]);
      }
    };

    loadProfileSelection();
    loadSkills();
    if (!stepParam) {
      setStep('profile');
    }
  }, [router, searchParams]);

  useEffect(() => {
    const filteredRoles = buildRoleCatalog(selectedSkills, assessmentResult?.score ?? 0).filter((role) => {
      if (!searchTerm.trim()) {
        return true;
      }
      const haystack = `${role.name} ${role.job_market}`.toLowerCase();
      return haystack.includes(searchTerm.trim().toLowerCase());
    });

    setRoleOptions(filteredRoles);
  }, [searchTerm, selectedSkills, assessmentResult?.score]);

  const handleRoleSelect = (roleId: string) => {
    setSelectedDreamJob(roleId);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('skillbridge_target_role', roleId);
    }
  };

  const toggleSkill = (skill: string, category?: string) => {
    // Create unique key for skills by combining category and skill name
    const skillKey = category && skill === 'None' ? `${category}:${skill}` : skill;
    
    setSelectedSkills((prev) => 
      prev.includes(skillKey) 
        ? prev.filter((item) => item !== skillKey) 
        : [...prev, skillKey]
    );
    setScoreCalculated(false);
    setAssessmentResult(null);
  };

  const handleAssessmentSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');
    
    // Filter out "None" selections and strip category prefix
    const skillsToSubmit = selectedSkills
      .filter(skill => !skill.includes(':None') && skill !== 'None')
      .map(skill => skill); // Keep regular skills as-is
    
    if (!skillsToSubmit.length) {
      setError('Select at least one skill to continue.');
      return;
    }

    const token = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_token') : null;
    if (!token) {
      router.replace('/login');
      return;
    }

    setLoading(true);
    try {
      const response = await api.post('/api/assessment/submit-skills', {
        skills: skillsToSubmit,
        employment_status: employmentStatus,
      });
      
      // Store assessment result and selected skills in localStorage
      if (typeof window !== 'undefined') {
        window.localStorage.setItem('skillbridge_assessment_result', JSON.stringify(response.data));
        window.localStorage.setItem('skillbridge_selected_skills', JSON.stringify(skillsToSubmit));
      }
      
      // Navigate to assessment complete page with data
      const dataStr = encodeURIComponent(JSON.stringify(response.data));
      router.push(`/onboarding/assessment-complete?data=${dataStr}`);
    } catch (err: any) {
      let errorMsg = 'Unable to calculate your assessment';
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        errorMsg = detail.map((e: any) => e.msg || JSON.stringify(e)).join('; ');
      } else if (typeof detail === 'string') {
        errorMsg = detail;
      }
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleProfileSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');
    const token = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_token') : null;
    if (!token) return router.replace('/login');
    setLoading(true);
    try {
      await api.post('/api/user/profile', {
        name,
        age: age || null,
        employment_status: employmentStatus,
      });
      if (typeof window !== 'undefined') {
        window.localStorage.setItem('skillbridge_user_name', name);
      }
      setStep('assessment');
    } catch (err: any) {
      let errorMsg = 'Unable to save profile';
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        errorMsg = detail.map((e: any) => e.msg || JSON.stringify(e)).join('; ');
      } else if (typeof detail === 'string') {
        errorMsg = detail;
      }
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleDreamJobContinue = async () => {
    const token = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_token') : null;
    if (!token) {
      router.replace('/login');
      return;
    }

    if (!selectedDreamJob) {
      setError('Please select a role before continuing.');
      return;
    }

    setLoading(true);
    try {
      await api.post('/api/user/profile', {
        target_role: selectedDreamJob,
        weekly_hours: weeklyHours,
        current_level: assessmentResult?.level || 'beginner',
      });
      if (typeof window !== 'undefined') {
        window.localStorage.setItem('skillbridge_target_role', selectedDreamJob);
        window.localStorage.setItem('skillbridge_weekly_hours', String(weeklyHours));
        window.localStorage.setItem('skillbridge_user_name', name);
      }
      router.push('/onboarding/ai-learning-path');
    } catch (err: any) {
      let errorMsg = 'Unable to save your dream job';
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        errorMsg = detail.map((e: any) => e.msg || JSON.stringify(e)).join('; ');
      } else if (typeof detail === 'string') {
        errorMsg = detail;
      }
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <main className="flex min-h-screen items-center justify-center text-lg">Loading…</main>;
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900 px-4 py-10 text-slate-100">
      <BackButton />
      <div className="mx-auto grid max-w-6xl gap-10 lg:grid-cols-[0.9fr_0.7fr]">
        <section className="rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-[0_30px_80px_rgba(15,23,42,0.5)] backdrop-blur-xl">
          <div className="space-y-5">
            <div className="inline-flex items-center gap-3 rounded-full bg-indigo-500/10 px-4 py-2 text-sm font-semibold text-indigo-100 ring-1 ring-indigo-500/20">
              <span>{step === 'profile' ? 'Step 1' : step === 'assessment' ? 'Step 3' : 'Step 4'}</span>
              <span className="text-slate-300">Onboarding</span>
            </div>
            <h1 className="text-4xl font-semibold text-white">Tell us what you already know</h1>
            <p className="max-w-2xl text-slate-300">
              We use your current skills and your next career goal to shape a practical learning path.
            </p>
            <div className="grid gap-4 rounded-3xl border border-slate-800 bg-slate-950/80 p-5 text-slate-300 shadow-inner">
              <div className="flex items-start gap-3">
                <span className="mt-1 inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-indigo-500 text-white">1</span>
                <div>
                  <p className="font-semibold text-white">Profile details</p>
                  <p className="text-sm text-slate-400">Your name and work status help us tailor the experience.</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="mt-1 inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-sky-500 text-white">2</span>
                <div>
                  <p className="font-semibold text-white">Skill snapshot</p>
                  <p className="text-sm text-slate-400">Choose the skills you already use so we can score your current level.</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="rounded-[2rem] border border-white/10 bg-white p-10 shadow-[0_40px_120px_rgba(15,23,42,0.35)]">
          {step === 'profile' ? (
            <>
              <h1 className="text-3xl font-semibold text-slate-900">📋 LET&apos;S GET TO KNOW YOU</h1>
              <form onSubmit={handleProfileSubmit} className="mt-6 space-y-6">
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">Your name?</label>
                  <input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Raj Kumar"
                    className="w-full rounded-3xl border border-slate-300 bg-slate-50 px-4 py-3 text-slate-900 shadow-sm transition focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                  />
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="mb-2 block text-sm font-medium text-slate-700">Your age?</label>
                    <input
                      value={age as number | string}
                      onChange={(e) => setAge(e.target.value ? Number(e.target.value) : '')}
                      type="number"
                      placeholder="28"
                      className="w-full rounded-3xl border border-slate-300 bg-slate-50 px-4 py-3 text-slate-900 shadow-sm transition focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                    />
                  </div>
                  <div>
                    <label className="mb-2 block text-sm font-medium text-slate-700">Current job status</label>
                    <div className="space-y-3 rounded-3xl border border-slate-200 bg-white/90 p-4 shadow-sm">
                      <label className="flex items-center gap-3 text-sm font-medium text-slate-700">
                        <input type="radio" name="job" checked={employmentStatus === 'unemployed'} onChange={() => setEmploymentStatus('unemployed')} className="h-4 w-4 text-indigo-600" />
                        Unemployed
                      </label>
                      <label className="flex items-center gap-3 text-sm font-medium text-slate-700">
                        <input type="radio" name="job" checked={employmentStatus === 'employed'} onChange={() => setEmploymentStatus('employed')} className="h-4 w-4 text-indigo-600" />
                        Employed
                      </label>
                      <label className="flex items-center gap-3 text-sm font-medium text-slate-700">
                        <input type="radio" name="job" checked={employmentStatus === 'student'} onChange={() => setEmploymentStatus('student')} className="h-4 w-4 text-indigo-600" />
                        Student
                      </label>
                    </div>
                  </div>
                </div>
                {error ? <p className="text-sm text-rose-600">{error}</p> : null}
                <button type="submit" className="rounded-xl bg-indigo-600 px-4 py-3 font-semibold text-white">Next</button>
              </form>
            </>
          ) : step === 'assessment' ? (
            <form onSubmit={handleAssessmentSubmit} className="space-y-6">
              <div className="space-y-2">
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-indigo-600">Step 3</p>
                <h1 className="text-3xl font-semibold text-slate-900">What skills do you already have?</h1>
                <p className="text-slate-600">
                  Select the skills you already have. We will group them by category and calculate your current level with AI.
                </p>
              </div>

              <div className="space-y-4">
                {skillGroups.length === 0 ? (
                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                    Loading skill categories...
                  </div>
                ) : (
                  skillGroups.map((group) => (
                    <div key={group.category} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
                      <div className="flex items-center justify-between gap-2">
                        <div>
                          <h2 className="text-lg font-semibold text-slate-900">{group.category}</h2>
                          <p className="text-sm text-slate-500">Weight: {group.weight}</p>
                        </div>
                      </div>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {group.skills.map((skill) => {
                          const skillKey = skill === 'None' ? `${group.category}:${skill}` : skill;
                          const checked = selectedSkills.includes(skillKey);
                          return (
                            <button
                              key={skillKey}
                              type="button"
                              onClick={() => toggleSkill(skill, group.category)}
                              className={`rounded-full border px-3 py-2 text-sm font-medium transition ${checked ? 'border-indigo-500 bg-indigo-50 text-indigo-700' : 'border-slate-200 bg-white text-slate-700 hover:border-indigo-300 hover:bg-slate-50'}`}
                            >
                              {checked ? '✓ ' : ''}
                              {skill}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))
                )}
              </div>

              <div className="rounded-2xl border border-indigo-200 bg-indigo-50 p-4 text-sm text-slate-700">
                <p className="font-semibold text-slate-900">AI score</p>
                <p className="mt-1">Choose your current skills first. Then click "Calculate score" to see your assessment and next steps.</p>
              </div>

              {error ? <p className="text-sm text-rose-600">{error}</p> : null}
              <button type="submit" className="w-full rounded-xl bg-indigo-600 px-4 py-3 font-semibold text-white disabled:cursor-not-allowed disabled:bg-indigo-300" disabled={loading || selectedSkills.filter(s => !s.includes(':None')).length === 0}>
                {loading ? 'Calculating…' : 'Calculate score →'}
              </button>
            </form>
          ) : (
            <div className="space-y-6">
              <div className="space-y-2">
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-indigo-600">Step 4</p>
                <h1 className="text-3xl font-semibold text-slate-900">What is your dream job?</h1>
                <p className="text-slate-600">Search your target role, select it, and choose how many hours you can study each week.</p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <label className="mb-2 block text-sm font-medium text-slate-700">Search your target role</label>
                <input
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Try data analyst"
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-slate-900 shadow-sm"
                />
                <div className="mt-3 rounded-2xl border border-indigo-200 bg-indigo-50 p-4 text-sm text-slate-700">
                  <p className="font-semibold text-slate-900">Personalized match preview</p>
                  <p className="mt-1">Score: {assessmentResult?.score ?? 0}/100 • Skills: {selectedSkills.filter((skill) => !!skill && !skill.includes(':None') && skill !== 'None').join(', ') || 'No skills selected yet'}</p>
                </div>
                <div className="mt-3 space-y-3">
                  {roleOptions.map((role) => (
                    <div key={role.id} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
                      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                        <div>
                          <div className="flex flex-wrap items-center gap-2">
                            <h2 className="text-lg font-semibold text-slate-900">{role.name}</h2>
                            <span className="rounded-full bg-indigo-100 px-2 py-1 text-xs font-semibold text-indigo-700">{role.tag}</span>
                          </div>
                          <p className="mt-1 text-sm text-slate-600">Match: {role.matchPercent}%</p>
                          <p className="mt-1 text-sm text-slate-600">Salary: {role.salary}</p>
                          <p className="text-sm text-slate-600">EU job market: {role.job_market}</p>
                          <p className="mt-2 text-sm text-slate-500">Required skills: {role.requiredSkills.join(', ')}</p>
                          <p className="text-sm text-slate-500">{role.hint}</p>
                        </div>
                        <button
                          type="button"
                          onClick={() => handleRoleSelect(role.id)}
                          className={`rounded-xl px-4 py-2 text-sm font-semibold ${selectedDreamJob === role.id ? 'bg-indigo-600 text-white' : 'border border-slate-300 bg-white text-slate-700'}`}
                        >
                          {selectedDreamJob === role.id ? 'Selected' : 'Select This Role'}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
                <label className="mb-2 block text-sm font-medium text-slate-700">Weekly hours available</label>
                <select value={weeklyHours} onChange={(e) => setWeeklyHours(Number(e.target.value))} className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-slate-900 shadow-sm">
                  <option value={5}>5 hours/week</option>
                  <option value={8}>8 hours/week</option>
                  <option value={10}>10 hours/week</option>
                  <option value={12}>12 hours/week</option>
                </select>
              </div>

              {error ? <p className="text-sm text-rose-600">{error}</p> : null}
              <button onClick={handleDreamJobContinue} className="w-full rounded-xl bg-indigo-600 px-4 py-3 font-semibold text-white disabled:cursor-not-allowed disabled:bg-indigo-300" disabled={loading || !selectedDreamJob}>
                {loading ? 'Saving…' : 'Save and continue to dashboard'}
              </button>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
