'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import LogoutButton from '@/components/LogoutButton';
import BackButton from '@/components/BackButton';

type DashboardData = {
  full_name: string;
  target_role: string;
  current_level: string;
  completed_lessons: number;
  total_lessons: number;
  completion_rate: number;
  latest_score: number;
  risk_level: string;
  next_lesson: string;
  skill_score: number;
  skill_level: string;
  lessons_completed: number;
  completion_percent: number;
  avg_quiz_score?: number | null;
  learning_path: string;
  ai_path_explanation: string;
  weekly_hours?: number;
  next_focus_skill?: string | null;
  next_move_priority?: string;
  next_move?: string | null;
  user_path?: string | null;
  score_type?: string | null;
  jobs_locked?: boolean;
};

type LearningPathData = {
  path_name: string;
  role: string;
  target_role: string;
  level: string;
  score: number;
  explanation: string;
  lessons: Array<{
    id: string;
    title: string;
    description: string;
    level: string;
    estimated_minutes: number;
    lesson_order: number;
    completed: boolean;
    status?: string;
    locked?: boolean;
  }>;
};

type JobMatch = {
  id: string;
  title: string;
  company: string;
  role: string;
  match_score: number;
  description: string;
};

const formatRoleLabel = (role?: string) => {
  const normalized = (role || 'data-analyst').toLowerCase().replace(/\s+/g, '-');
  const roleMap: Record<string, string> = {
    'tech-support': 'Tech Support',
    'data-analyst': 'Data Analyst',
    'business-analyst': 'Business Analyst',
    'python-developer': 'Python Developer',
    'data-engineer': 'Data Engineer',
    'ml-engineer': 'ML Engineer',
  };
  return roleMap[normalized] || normalized.replace(/-/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase());
};

const getTopSkill = (selectedSkills: string[], role: string) => {
  const normalizedSkills = selectedSkills
    .filter((skill) => !!skill && !skill.includes(':None') && skill !== 'None')
    .map((skill) => skill.toLowerCase());

  if (normalizedSkills.length) {
    return normalizedSkills[0].replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase());
  }

  const roleMap: Record<string, string[]> = {
    'tech-support': ['Excel', 'English', 'Word'],
    'data-analyst': ['SQL', 'Excel', 'Data Analysis'],
    'business-analyst': ['Data Analysis', 'PowerPoint', 'Excel'],
    'python-developer': ['Python', 'SQL', 'Automation'],
    'data-engineer': ['Python', 'Cloud', 'SQL'],
    'ml-engineer': ['Python', 'ML', 'Cloud'],
  };

  return roleMap[role]?.[0] || 'Consistency';
};

const getNextSkill = (selectedSkills: string[], role: string) => {
  const normalizedSkills = new Set(
    selectedSkills
      .filter((skill) => !!skill && !skill.includes(':None') && skill !== 'None')
      .map((skill) => skill.toLowerCase())
  );

  const roleMap: Record<string, string[]> = {
    'tech-support': ['Excel', 'English', 'Word'],
    'data-analyst': ['SQL', 'Excel', 'Data Analysis'],
    'business-analyst': ['Data Analysis', 'PowerPoint', 'Excel'],
    'python-developer': ['Python', 'SQL', 'Automation'],
    'data-engineer': ['Python', 'Cloud', 'SQL'],
    'ml-engineer': ['Python', 'ML', 'Cloud'],
  };

  const requiredSkills = roleMap[role] || roleMap['data-analyst'];
  const nextSkill = requiredSkills.find((skill) => !Array.from(normalizedSkills).some((candidate) => candidate.includes(skill.toLowerCase())));
  return nextSkill || 'Consistency';
};

export default function DashboardPage() {
  const router = useRouter();
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [learningPath, setLearningPath] = useState<LearningPathData | null>(null);
  const [risk, setRisk] = useState<{ risk_level: string; message: string; days_since_login?: number } | null>(null);
  const [jobs, setJobs] = useState<JobMatch[]>([]);
  const [userName, setUserName] = useState('Raj');
  const [loading, setLoading] = useState(true);
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [activeRole, setActiveRole] = useState('data-analyst');

  useEffect(() => {
    const token = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_token') : null;
    if (!token) {
      router.replace('/login');
      return;
    }

    const loadDashboard = async () => {
      try {
        const storedName = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_user_name') : null;
        const storedSkills = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_selected_skills') : null;
        const storedRole = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_target_role') : null;

        if (storedName) {
          setUserName(storedName);
        }
        if (storedSkills) {
          try {
            setSelectedSkills(JSON.parse(storedSkills));
          } catch {
            setSelectedSkills([]);
          }
        }
        if (storedRole) {
          setActiveRole(storedRole);
        }

        const [userRes, dashboardRes, pathRes, riskRes, jobsRes] = await Promise.allSettled([
          api.get('/api/auth/me'),
          api.get('/api/progress/dashboard'),
          api.get('/api/learning/path'),
          api.get('/api/risk/status'),
          api.get('/api/jobs/matches'),
        ]);

        if (userRes.status === 'fulfilled') {
          const nextName = userRes.value.data?.name || storedName || 'Raj';
          setUserName(nextName);
          if (typeof window !== 'undefined') {
            window.localStorage.setItem('skillbridge_user_name', nextName);
          }
        }

        if (dashboardRes.status === 'fulfilled') {
          setDashboard(dashboardRes.value.data);
        }

        if (pathRes.status === 'fulfilled') {
          const nextPath = pathRes.value.data as LearningPathData;
          setLearningPath(nextPath);
          if (nextPath?.role) {
            setActiveRole(nextPath.role);
          }
          if (typeof window !== 'undefined') {
            window.localStorage.setItem('skillbridge_target_role', nextPath.role || storedRole || 'data-analyst');
          }

          // Check if all lessons are completed - redirect to completion page
          if (nextPath?.lessons) {
            const completedLessons = nextPath.lessons.filter((l) => l.completed).length;
            const totalLessons = nextPath.lessons.length;
            if (completedLessons === totalLessons && totalLessons === 5) {
              router.replace('/onboarding/path-completion');
              return;
            }
          }
        }

        if (riskRes.status === 'fulfilled') {
          setRisk(riskRes.value.data);
        }

        if (jobsRes.status === 'fulfilled') {
          setJobs(jobsRes.value.data || []);
        }

        // Check dashboard data as backup for completion check
        if (dashboardRes.status === 'fulfilled') {
          const dashData = dashboardRes.value.data;
          if (dashData?.completed_lessons === 5 && dashData?.total_lessons === 5) {
            setTimeout(() => router.replace('/onboarding/path-completion'), 100);
            return;
          }
        }
      } catch {
        // fail silently and let the page fall back to basic placeholders
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, [router]);

  if (loading) {
    return <main className="flex min-h-screen items-center justify-center text-lg">Loading dashboard…</main>;
  }

  const roleLabel = formatRoleLabel(activeRole || learningPath?.role || dashboard?.target_role);
  const pathTitle = learningPath?.path_name || dashboard?.learning_path || `${roleLabel} Path`;
  const pathExplanation = learningPath?.explanation || dashboard?.ai_path_explanation || 'Your personalized path is ready and will guide you step by step.';
  const topJob = jobs[0];
  const nextSkill = dashboard?.next_focus_skill || getNextSkill(selectedSkills, activeRole || learningPath?.role || 'data-analyst');
  const topSkill = getTopSkill(selectedSkills, activeRole || learningPath?.role || 'data-analyst');
  const weeklyHours = dashboard?.weekly_hours ?? 5;
  const nextMove = dashboard?.next_move || learningPath?.lessons?.find((lesson) => !lesson.completed)?.title || dashboard?.next_lesson || `Start with ${nextSkill} to strengthen your ${roleLabel.toLowerCase()} plan.`;
  const nextReadyLesson = learningPath?.lessons?.find((lesson) => lesson.status !== 'locked' && !lesson.completed && !lesson.id.startsWith('role-'));
  const firstAvailableLessonId = nextReadyLesson?.id || learningPath?.lessons?.[0]?.id;
  const firstLessonLink = firstAvailableLessonId && !firstAvailableLessonId.startsWith('role-') ? `/lessons/${firstAvailableLessonId}` : '/lessons';

  const getLessonStatus = (lesson: LearningPathData['lessons'][number], index: number, lessons: LearningPathData['lessons']) => {
    if (lesson.completed) {
      return 'completed';
    }
    if (lesson.locked || lesson.status === 'locked') {
      return 'locked';
    }
    if (index === 0 || lesson.lesson_order === 1) {
      return 'ready';
    }

    let previousCompleted = true;
    for (let previousIndex = 0; previousIndex < index; previousIndex += 1) {
      const previousLesson = lessons[previousIndex];
      if (previousLesson?.completed) {
        continue;
      }
      previousCompleted = false;
      break;
    }

    return previousCompleted ? 'ready' : 'locked';
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900 px-4 py-10 text-slate-100">
      <BackButton />
      <div className="mx-auto max-w-6xl space-y-6">
        <div className="rounded-[2rem] border border-white/10 bg-white/10 p-8 shadow-[0_30px_80px_rgba(15,23,42,0.45)] backdrop-blur-xl">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm text-slate-300">DB Career Navigator</p>
              <h1 className="text-3xl font-semibold text-white">Hi {userName}! 👋</h1>
            </div>
            <div className="flex items-center gap-3">
              <div className="rounded-full bg-[#0018A8]/20 px-4 py-2 text-sm font-medium text-blue-100">
                {roleLabel} • {dashboard?.current_level || 'beginner'}
              </div>
              <LogoutButton />
            </div>
          </div>

          <div className="mt-8 rounded-[1.5rem] border border-white/10 bg-slate-950/70 p-6">
            <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.2em] text-blue-200">
              <span>🤖</span>
              <span>Your Deutsche Bank Readiness Plan</span>
            </div>
            <p className="mt-3 text-lg text-slate-200">{pathExplanation}</p>
          </div>
        </div>

        <div className="rounded-[2rem] border border-white/10 bg-white/10 p-8 shadow-[0_30px_80px_rgba(15,23,42,0.35)] backdrop-blur-xl">
          <h2 className="text-xl font-semibold text-white">Your progress</h2>
          <div className="mt-5 grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
              <p className="text-sm text-slate-400">{dashboard?.score_type || (dashboard?.user_path === 'C' ? 'Employability Score' : 'DB Career Score')}</p>
              <p className="mt-2 text-3xl font-semibold text-white">{dashboard?.skill_score ?? dashboard?.latest_score ?? 0}/100</p>
              <p className="text-xs text-slate-500 mt-1">Score is 0–100. Higher score = closer to your DB career goal.</p>
              <p className="mt-3 text-sm text-slate-300">{topSkill} • {dashboard?.skill_level || dashboard?.current_level || 'beginner'}</p>
              {dashboard?.user_path === 'C' && dashboard?.jobs_locked && (
                <p className="mt-3 text-xs text-amber-400">🔒 Your current score: {dashboard?.skill_score ?? 0}. Jobs unlock at 60. Complete {Math.max(0, 60 - (dashboard?.skill_score ?? 0))} more points of lessons to get there.</p>
              )}
              {dashboard?.user_path === 'C' && !dashboard?.jobs_locked && (
                <p className="mt-3 text-xs text-emerald-400">✅ Jobs unlocked!</p>
              )}
              {(dashboard?.user_path === 'A' || dashboard?.user_path === 'B') && (
                <p className="mt-3 text-xs text-slate-400">Your score updates as you complete lessons.</p>
              )}
            </div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
              <p className="text-sm text-slate-400">Career progression</p>
              <p className="mt-2 text-3xl font-semibold text-white">Analyst → AVP → VP</p>
              <p className="mt-2 text-sm text-slate-300">Role progression traced for your target Deutsche Bank path</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
              <p className="text-sm text-slate-400">Top matching Deutsche Bank vacancy</p>
              <p className="mt-2 text-3xl font-semibold text-white">{topJob?.title || 'Role fit'}</p>
              <p className="mt-2 text-sm text-slate-300">{topJob ? `${topJob.match_score}% Readiness Match` : 'Complete more lessons to surface stronger job fit.'}</p>
            </div>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-[2rem] border border-white/10 bg-white p-8 text-slate-900 shadow-[0_30px_80px_rgba(15,23,42,0.25)]">
            <h2 className="text-xl font-semibold">Your learning path: {pathTitle}</h2>
            <div className="mt-5 space-y-3">
              {(learningPath?.lessons || []).slice(0, 5).map((lesson, index) => {
                const lessonStatus = getLessonStatus(lesson, index, learningPath?.lessons || []);
                const lessonLink = lessonStatus !== 'locked' && lesson.id && !lesson.id.startsWith('role-') ? `/lessons/${lesson.id}` : undefined;

                return (
                  <div key={lesson.id} className="flex items-center justify-between rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                    <div>
                      {lessonLink ? (
                        <Link href={lessonLink} className="font-semibold text-slate-900 hover:text-indigo-700">
                          {index + 1}. {lesson.title}
                        </Link>
                      ) : (
                        <p className="font-semibold text-slate-900">{index + 1}. {lesson.title}</p>
                      )}
                      <p className="text-sm text-slate-500">{lesson.description}</p>
                    </div>
                    <div className="text-right">
                      {lessonStatus === 'completed' ? (
                        <span className="inline-block rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">✓ Completed</span>
                      ) : lessonStatus === 'locked' ? (
                        <span className="inline-block rounded-full bg-slate-200 px-3 py-1 text-xs font-semibold text-slate-600">🔒 Locked</span>
                      ) : (
                        <span className="inline-block rounded-full bg-indigo-100 px-3 py-1 text-xs font-semibold text-indigo-700">✓ Ready</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-[2rem] border border-white/10 bg-white p-8 text-slate-900 shadow-[0_30px_80px_rgba(15,23,42,0.25)]">
              <h2 className="text-xl font-semibold">Top job match</h2>
              {topJob ? (
                <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <p className="font-semibold text-slate-900">{topJob.title} @ {topJob.company}</p>
                  <p className="mt-1 text-sm text-slate-600">Match: {topJob.match_score}%</p>
                  <p className="mt-2 text-sm text-slate-500">{topJob.description}</p>
                </div>
              ) : (
                <p className="mt-4 text-sm text-slate-500">Complete a few lessons to unlock better matches.</p>
              )}
            </div>

            <div className="rounded-[2rem] border border-white/10 bg-white p-8 text-slate-900 shadow-[0_30px_80px_rgba(15,23,42,0.25)]">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">Your next move</h2>
                <span className="rounded-full bg-indigo-100 px-3 py-1 text-sm font-semibold text-indigo-700">{dashboard?.next_move_priority || risk?.risk_level || 'LOW'}</span>
              </div>
              <p className="mt-4 text-sm text-slate-600">{nextMove}</p>
              <div className="mt-6 flex flex-wrap gap-3">
                <Link href={firstLessonLink} className="rounded-full bg-indigo-600 px-5 py-3 font-semibold text-white">📚 Go to lessons</Link>
                <Link href="/jobs" className="rounded-full border border-slate-300 px-5 py-3 font-semibold text-slate-700">💼 View all jobs</Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
