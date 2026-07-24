'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import LogoutButton from '@/components/LogoutButton';
import BackButton from '@/components/BackButton';

type Job = {
  id: string;
  title: string;
  company: string;
  company_logo_url?: string | null;
  location: string;
  work_type: string;
  level: string;
  salary_min?: number | null;
  salary_max?: number | null;
  currency: string;
  salary: string;
  description: string;
  description_short: string;
  description_full: string;
  required_skills: string[];
  role: string;
  date_posted?: string | null;
  application_url?: string | null;
  match_score: number;
  reasons: string;
  saved: boolean;
  matched_skills: string[];
  missing_skills: string[];
};

type UserProfile = {
  target_role?: string;
  current_level?: string;
  user_path?: string;
  jobs_unlocked?: boolean;
  score_type?: string;
};

const roleLabelMap: Record<string, string> = {
  'tech-support': 'Tech Support',
  'data-analyst': 'Data Analyst',
  'business-analyst': 'Business Analyst',
  'python-developer': 'Python Developer',
  'data-engineer': 'Data Engineer',
  'ml-engineer': 'ML Engineer',
};

const levelLabelMap: Record<string, string> = {
  beginner: 'Beginner',
  intermediate: 'Intermediate',
  advanced: 'Advanced',
};

export default function JobsPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [savedJobs, setSavedJobs] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [userName, setUserName] = useState('Learner');
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [matchFilter, setMatchFilter] = useState('all');
  const [levelFilter, setLevelFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [sortBy, setSortBy] = useState('best-match');
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [applyJob, setApplyJob] = useState<Job | null>(null);
  const [appliedJobIds, setAppliedJobIds] = useState<string[]>([]);
  const [successJob, setSuccessJob] = useState<Job | null>(null);

  useEffect(() => {
    const token = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_token') : null;
    if (!token) {
      router.replace('/login');
      return;
    }

    const loadData = async () => {
      try {
        setLoading(true);
        const [meRes, profileRes, jobsRes, savedRes] = await Promise.allSettled([
          api.get('/api/auth/me'),
          api.get('/api/user/profile'),
          api.get('/api/jobs'),
          api.get('/api/jobs/saved'),
        ]);

        if (meRes.status === 'fulfilled') {
          setUserName(meRes.value.data?.name || 'Learner');
        }
        if (profileRes.status === 'fulfilled') {
          setProfile(profileRes.value.data?.profile || null);
        }
        if (jobsRes.status === 'fulfilled') {
          setJobs(jobsRes.value.data || []);
        }
        if (savedRes.status === 'fulfilled') {
          setSavedJobs(savedRes.value.data || []);
        }
      } catch {
        setJobs([]);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [router]);

  const filteredJobs = useMemo(() => {
    const normalized = jobs.filter((job) => {
      const matchPass = matchFilter === 'all' || (matchFilter === '80' && job.match_score >= 80) || (matchFilter === '60' && job.match_score >= 60) || (matchFilter === '40' && job.match_score >= 40);
      const levelPass = levelFilter === 'all' || job.level.toLowerCase() === levelFilter.toLowerCase();
      const typePass = typeFilter === 'all' || job.work_type.toLowerCase() === typeFilter.toLowerCase();
      return matchPass && levelPass && typePass;
    });

    const sorted = [...normalized];
    sorted.sort((a, b) => {
      if (sortBy === 'salary') {
        return (b.salary_max || 0) - (a.salary_max || 0);
      }
      if (sortBy === 'latest') {
        return (b.match_score - a.match_score);
      }
      return b.match_score - a.match_score;
    });

    return sorted;
  }, [jobs, matchFilter, levelFilter, typeFilter, sortBy]);

  const roleName = profile?.target_role ? roleLabelMap[profile.target_role] || profile.target_role.replace(/-/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase()) : 'Your role';
  const skillLevel = profile?.current_level ? levelLabelMap[profile.current_level] || profile.current_level : 'Intermediate';
  const topMissingSkills = useMemo(() => {
    const topJobs = [...jobs].sort((a, b) => b.match_score - a.match_score).slice(0, 3);
    const missing = topJobs.flatMap((job) => job.missing_skills.slice(0, 2));
    return Array.from(new Set(missing)).slice(0, 2);
  }, [jobs]);

  const handleToggleSave = async (job: Job) => {
    try {
      if (savedJobs.includes(job.id)) {
        await api.delete(`/api/jobs/${job.id}/save`);
        setSavedJobs((current) => current.filter((id) => id !== job.id));
      } else {
        await api.post(`/api/jobs/${job.id}/save`);
        setSavedJobs((current) => [...current, job.id]);
      }
    } catch {
      // keep UI stable even if save fails
    }
  };

  const handleApplyNow = (job: Job) => {
    if (appliedJobIds.includes(job.id)) {
      return;
    }

    setAppliedJobIds((current) => [...current, job.id]);
    setSelectedJob(null);
    setSuccessJob(job);
    setApplyJob(null);
  };

  const confirmApply = () => {
    if (applyJob?.application_url) {
      window.open(applyJob.application_url, '_blank', 'noopener,noreferrer');
    }
    if (applyJob) {
      handleApplyNow(applyJob);
    }
    setApplyJob(null);
  };

  const closeSuccessModal = () => {
    setSuccessJob(null);
  };

  const handleViewMoreJobs = () => {
    setSuccessJob(null);
  };

  const handleBackToDashboard = () => {
    setSuccessJob(null);
    router.push('/dashboard');
  };

  if (loading) {
    return <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900 text-lg text-white">Loading jobs…</main>;
  }

  // Path C: jobs locked until score threshold reached
  const isPathC = profile?.user_path === 'C';
  const jobsLocked = isPathC && profile?.jobs_unlocked === false;
  const scoreLabel = profile?.score_type || (profile?.user_path === 'C' ? 'Employability Score' : 'DB Career Score');

  if (jobsLocked) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-[#001F4D] via-[#003080] to-[#001F4D] px-4 py-10 text-slate-100 flex items-center justify-center">
        <div className="max-w-lg text-center space-y-6">
          <div className="text-6xl">🔒</div>
          <h1 className="text-3xl font-semibold text-white">Deutsche Bank Jobs Locked</h1>
          <p className="text-slate-300">Your <strong className="text-[#FFD700]">Employability Score</strong> unlocks Deutsche Bank jobs automatically when it reaches <strong>60</strong> — either through assessment or lesson completion.</p>
          <p className="text-slate-400 text-sm">No action needed. Keep learning!</p>
          <Link href="/dashboard" className="inline-block rounded-xl bg-[#FFD700] px-6 py-3 font-semibold text-[#001F4D]">Go to my Learning Path →</Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900 px-4 py-10 text-slate-100">
      <BackButton />
      <div className="mx-auto max-w-6xl space-y-8">
        <div className="rounded-[2rem] border border-white/10 bg-white/10 p-8 shadow-[0_30px_80px_rgba(15,23,42,0.45)] backdrop-blur-xl">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm text-slate-300">DB Career Navigator</p>
              <h1 className="text-3xl font-semibold text-white">Hi {userName}!</h1>
            </div>
            <div className="flex items-center gap-3">
              <span className="rounded-full border border-[#0018A8]/30 bg-[#0018A8]/10 px-4 py-2 text-sm font-semibold text-blue-100">
                {roleName} • {skillLevel}
              </span>
              <LogoutButton />
            </div>
          </div>
        </div>

        <div className="rounded-[2rem] border border-slate-700/50 bg-slate-800/30 p-8">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <h2 className="text-3xl font-semibold text-white">
                {profile?.user_path === 'A' ? `Deutsche Bank vacancies matching your target ${roleName} role` : profile?.user_path === 'B' ? `Deutsche Bank openings for external candidates like you` : `Deutsche Bank roles suited to your Employability Score`}
              </h2>
              <p className="mt-2 text-slate-300">{filteredJobs.length} Deutsche Bank opportunities match your skills and experience</p>
              <p className="mt-2 text-sm text-slate-400">{profile?.user_path === 'A' ? 'Best matches by level and department' : profile?.user_path === 'B' ? 'Readiness % shows your fit to each role' : 'Match % based on your current Employability Score'}</p>
              {(profile?.user_path === 'A' || profile?.user_path === 'B') && (
                <p className="mt-1 text-xs text-slate-400">Jobs are always available. Higher score = better match percentage.</p>
              )}
            </div>
            <Link href="/onboarding/path-completion" className="rounded-full border border-slate-600 px-5 py-3 font-semibold text-slate-100">← Back to Completion</Link>
          </div>

          <div className="mt-8 flex flex-wrap gap-3">
            <label className="flex items-center gap-2 rounded-full border border-slate-700 bg-slate-900/30 px-4 py-2 text-sm text-slate-200">
              <span>Match %</span>
              <select value={matchFilter} onChange={(event) => setMatchFilter(event.target.value)} className="bg-transparent outline-none">
                <option value="all">All</option>
                <option value="80">80%+</option>
                <option value="60">60%+</option>
                <option value="40">40%+</option>
              </select>
            </label>
            <label className="flex items-center gap-2 rounded-full border border-slate-700 bg-slate-900/30 px-4 py-2 text-sm text-slate-200">
              <span>Level</span>
              <select value={levelFilter} onChange={(event) => setLevelFilter(event.target.value)} className="bg-transparent outline-none">
                <option value="all">All</option>
                <option value="Analyst">Analyst</option>
                <option value="Associate">Associate</option>
                <option value="AVP">AVP</option>
                <option value="VP">VP</option>
                <option value="Managing Director">Managing Director</option>
                <option value="junior">Junior</option>
                <option value="mid-level">Mid-level</option>
                <option value="senior">Senior</option>
              </select>
            </label>
            <label className="flex items-center gap-2 rounded-full border border-slate-700 bg-slate-900/30 px-4 py-2 text-sm text-slate-200">
              <span>Type</span>
              <select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)} className="bg-transparent outline-none">
                <option value="all">All</option>
                <option value="remote">Remote</option>
                <option value="hybrid">Hybrid</option>
                <option value="on-site">On-site</option>
              </select>
            </label>
            <label className="flex items-center gap-2 rounded-full border border-slate-700 bg-slate-900/30 px-4 py-2 text-sm text-slate-200">
              <span>Sort by</span>
              <select value={sortBy} onChange={(event) => setSortBy(event.target.value)} className="bg-transparent outline-none">
                <option value="best-match">Best Match</option>
                <option value="salary">Salary</option>
                <option value="latest">Latest</option>
              </select>
            </label>
          </div>

          <div className="mt-8 space-y-4">
            {filteredJobs.length === 0 ? (
              <div className="rounded-3xl border border-dashed border-slate-600 bg-slate-900/20 p-10 text-center text-slate-300">
                <p className="text-lg font-semibold">No jobs match this filter.</p>
                <p className="mt-2">Try adjusting your filters or check back soon for more roles.</p>
              </div>
            ) : (
              filteredJobs.map((job) => (
                <div key={job.id} className="rounded-[1.5rem] border border-slate-700/50 bg-slate-900/40 p-6 shadow-sm">
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                      <div className="flex flex-wrap items-center gap-3">
                        <h3 className="text-xl font-semibold text-white">{job.title} @ {job.company}</h3>
                        <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-emerald-300">
                          {job.match_score}% match
                        </span>
                      </div>
                      <p className="mt-3 text-sm text-slate-400">📍 {job.location} • {job.work_type.replace(/-/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase())}</p>
                    </div>
                    <div className="rounded-2xl border border-slate-700 bg-slate-800/50 px-4 py-3 text-sm text-slate-300">
                      <div>Level: {job.level.replace(/-/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase())}</div>
                      <div className="mt-1">Salary: {job.salary}</div>
                    </div>
                  </div>

                  <p className="mt-4 max-w-3xl text-slate-300">{job.description_short}</p>

                  <div className="mt-4 flex flex-wrap gap-2">
                    {job.required_skills.map((skill) => {
                      const matched = job.matched_skills.includes(skill) || job.matched_skills.some((candidate) => candidate.toLowerCase() === skill.toLowerCase());
                      return (
                        <span key={skill} className={`rounded-full px-3 py-1 text-sm font-semibold ${matched ? 'bg-emerald-500/15 text-emerald-300' : 'bg-rose-500/15 text-rose-300'}`}>
                          {matched ? '✅' : '❌'} {skill}
                        </span>
                      );
                    })}
                  </div>

                  <div className="mt-6 flex flex-wrap gap-3">
                    <button type="button" onClick={() => setSelectedJob(job)} className="rounded-full bg-[#0018A8] px-5 py-3 font-semibold text-white">View Details</button>
                    <button type="button" onClick={() => handleToggleSave(job)} className={`rounded-full px-5 py-3 font-semibold ${savedJobs.includes(job.id) ? 'bg-emerald-600 text-white' : 'border border-slate-600 text-slate-100'}`}>
                      {savedJobs.includes(job.id) ? 'Saved ✓' : 'Save Job'}
                    </button>
                    <button type="button" onClick={() => handleApplyNow(job)} disabled={appliedJobIds.includes(job.id)} className={`rounded-full px-5 py-3 font-semibold ${appliedJobIds.includes(job.id) ? 'cursor-default bg-emerald-600 text-white' : 'border border-slate-600 text-slate-100'}`}>
                      {appliedJobIds.includes(job.id) ? 'Applied ✓' : 'Apply at Deutsche Bank'}
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="rounded-[2rem] border border-amber-500/30 bg-gradient-to-br from-amber-500/10 to-amber-500/5 p-8">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <h3 className="text-2xl font-semibold text-white">Want better job matches?</h3>
              <p className="mt-2 text-slate-300">
                {topMissingSkills.length > 0 ? `You are missing ${topMissingSkills.join(' and ')} skills to qualify for more senior roles.` : 'Keep building your profile to unlock more roles.'}
              </p>
            </div>
            <Link href="/dashboard" className="rounded-full bg-amber-500 px-5 py-3 font-semibold text-slate-950">Go to Dashboard</Link>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-4 rounded-[2rem] border border-slate-700/50 bg-slate-800/30 p-6">
          <Link href="/onboarding/path-completion" className="font-semibold text-slate-300">← Back to Completion Page</Link>
          <Link href="/dashboard" className="font-semibold text-slate-300">Go to Dashboard →</Link>
        </div>
      </div>

      {selectedJob ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4">
          <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-[2rem] border border-slate-700 bg-slate-900 p-8 text-slate-100 shadow-2xl">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-indigo-300">Job Details</p>
                <h3 className="mt-2 text-2xl font-semibold text-white">{selectedJob.title} @ {selectedJob.company}</h3>
              </div>
              <button type="button" onClick={() => setSelectedJob(null)} className="rounded-full border border-slate-600 px-3 py-2 text-sm font-semibold text-slate-200">Close</button>
            </div>
            <div className="mt-6 space-y-4 text-sm text-slate-300">
              <p>{selectedJob.description_full}</p>
              <div className="rounded-2xl border border-slate-700 bg-slate-800/50 p-4">
                <div className="grid gap-3 md:grid-cols-2">
                  <div><span className="font-semibold text-white">Location:</span> {selectedJob.location}</div>
                  <div><span className="font-semibold text-white">Work type:</span> {selectedJob.work_type.replace(/-/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase())}</div>
                  <div><span className="font-semibold text-white">Salary:</span> {selectedJob.salary}</div>
                  <div><span className="font-semibold text-white">Experience:</span> {selectedJob.level.replace(/-/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase())}</div>
                </div>
              </div>
              <div>
                <p className="font-semibold text-white">Required Skills</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {selectedJob.required_skills.map((skill) => (
                    <span key={skill} className={`rounded-full px-3 py-1 text-sm font-semibold ${selectedJob.matched_skills.includes(skill) ? 'bg-emerald-500/15 text-emerald-300' : 'bg-rose-500/15 text-rose-300'}`}>
                      {selectedJob.matched_skills.includes(skill) ? '✅' : '❌'} {skill}
                    </span>
                  ))}
                </div>
              </div>
            </div>
            <div className="mt-8 flex flex-wrap gap-3">
              <button type="button" onClick={() => handleApplyNow(selectedJob)} disabled={appliedJobIds.includes(selectedJob.id)} className={`rounded-full px-5 py-3 font-semibold ${appliedJobIds.includes(selectedJob.id) ? 'cursor-default bg-emerald-600 text-white' : 'bg-[#0018A8] text-white'}`}>
                {appliedJobIds.includes(selectedJob.id) ? 'Applied ✓' : 'Apply at Deutsche Bank'}
              </button>
              <button type="button" onClick={() => handleToggleSave(selectedJob)} className={`rounded-full px-5 py-3 font-semibold ${savedJobs.includes(selectedJob.id) ? 'bg-emerald-600 text-white' : 'border border-slate-600 text-slate-100'}`}>
                {savedJobs.includes(selectedJob.id) ? 'Saved ✓' : 'Save Job'}
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {applyJob ? (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-slate-950/70 px-4">
          <div className="w-full max-w-md rounded-[2rem] border border-slate-700 bg-slate-900 p-8 text-slate-100 shadow-2xl">
            <h3 className="text-xl font-semibold text-white">Apply for {applyJob.title}?</h3>
            <p className="mt-3 text-sm text-slate-300">You are about to apply for {applyJob.title} at {applyJob.company}. This will open the external application page.</p>
            <div className="mt-6 flex flex-wrap gap-3">
              <button type="button" onClick={confirmApply} className="rounded-full bg-indigo-600 px-5 py-3 font-semibold text-white">Confirm</button>
              <button type="button" onClick={() => setApplyJob(null)} className="rounded-full border border-slate-600 px-5 py-3 font-semibold text-slate-100">Cancel</button>
            </div>
          </div>
        </div>
      ) : null}

      {successJob ? (
        <div className="fixed inset-0 z-[70] flex items-center justify-center bg-slate-950/80 px-4 py-6">
          <div className="modal-fade-in w-full max-w-2xl rounded-[2rem] border border-emerald-500/20 bg-slate-900/95 p-8 text-slate-100 shadow-2xl">
            <div className="flex items-start justify-end">
              <button type="button" onClick={closeSuccessModal} className="text-sm font-semibold text-slate-400 transition hover:text-white">
                Close
              </button>
            </div>

            <div className="mt-2 flex flex-col items-center text-center">
              <div className="check-pop flex h-16 w-16 items-center justify-center rounded-full bg-emerald-500/15 text-4xl text-emerald-400">
                ✓
              </div>
              <h3 className="mt-6 text-3xl font-semibold text-white">Application Submitted Successfully!</h3>
              <p className="mt-3 text-lg text-slate-300">You've applied for:</p>
              <p className="mt-2 text-xl font-semibold text-emerald-300">{successJob.title} @ {successJob.company}</p>

              <div className="mt-6 w-full rounded-2xl border border-slate-700 bg-slate-800/70 px-4 py-3 text-sm text-slate-300">
                <div className="flex flex-wrap items-center justify-center gap-2">
                  <span>📍 {successJob.location}</span>
                  <span className="text-slate-500">|</span>
                  <span>{successJob.work_type.replace(/-/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase())}</span>
                  <span className="text-slate-500">|</span>
                  <span>{successJob.salary}</span>
                </div>
              </div>

              <div className="mt-8 w-full rounded-2xl border border-slate-700 bg-slate-800/40 p-5 text-left">
                <p className="text-lg font-semibold text-white">What happens next:</p>
                <ul className="mt-3 space-y-2 text-sm text-slate-300">
                  <li>• Your profile has been shared with the employer</li>
                  <li>• Expect a response within 5–7 business days</li>
                  <li>• Check your email for confirmation</li>
                </ul>
              </div>

              <div className="mt-6 w-full rounded-2xl border border-amber-500/30 bg-amber-500/10 p-5 text-left">
                <p className="text-sm font-semibold text-amber-200">💡 Keep Learning</p>
                <p className="mt-2 text-sm text-amber-100/80">You applied for {successJob.title} at Deutsche Bank. Your current score: {profile?.skill_score ?? 0}/100. Keep learning to strengthen your profile for future Deutsche Bank roles.</p>
              </div>

              <div className="mt-8 flex flex-wrap justify-center gap-3">
                <button type="button" onClick={handleViewMoreJobs} className="rounded-full border border-slate-600 px-5 py-3 font-semibold text-slate-100 transition hover:border-slate-500 hover:bg-slate-800/70">
                  View More Jobs
                </button>
                <button type="button" onClick={handleBackToDashboard} className="rounded-full bg-indigo-600 px-5 py-3 font-semibold text-white transition hover:bg-indigo-700">
                  Back to Dashboard
                </button>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </main>
  );
}
