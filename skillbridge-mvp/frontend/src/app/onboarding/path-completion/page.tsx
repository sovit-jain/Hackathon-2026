'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import BackButton from '@/components/BackButton';
import LogoutButton from '@/components/LogoutButton';

type LearningPathData = {
  path_name: string;
  role: string;
  level: string;
  lessons: Array<{
    id: string;
    title: string;
    category: string;
    level: string;
    completed: boolean;
    lesson_order: number;
  }>;
  completed_lessons: number;
  total_lessons: number;
};

type DashboardData = {
  full_name: string;
  target_role: string;
  skill_level: string;
  skill_score: number;
  completed_lessons: number;
  total_lessons: number;
  completion_percent: number;
  learning_path: string;
};

const SKILLS_GAINED: Record<string, string[]> = {
  'tech-support': [
    'Troubleshooting complex technical issues with confidence',
    'Clear communication in high-pressure situations',
    'Systematic documentation of solutions',
    'Time management for multiple support tickets',
  ],
  'data-analyst': [
    'SQL query writing and data extraction',
    'Data visualization and storytelling',
    'Statistical analysis fundamentals',
    'Business insight generation from data',
  ],
  'business-analyst': [
    'Requirement gathering and documentation',
    'Process improvement identification',
    'Stakeholder communication skills',
    'Data-driven decision making',
  ],
  'python-developer': [
    'Python syntax and core programming concepts',
    'Object-oriented programming principles',
    'API development and integration',
    'Debugging and problem-solving techniques',
  ],
  'data-engineer': [
    'Data pipeline architecture and design',
    'Cloud-based data processing',
    'ETL workflow optimization',
    'Data quality and governance practices',
  ],
  'ml-engineer': [
    'Machine learning model fundamentals',
    'Data preprocessing and feature engineering',
    'Model evaluation and optimization',
    'Production deployment considerations',
  ],
};

export default function PathCompletionPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [learningPath, setLearningPath] = useState<LearningPathData | null>(null);
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [isAllCompleted, setIsAllCompleted] = useState(false);

  useEffect(() => {
    const token = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_token') : null;
    if (!token) {
      router.replace('/login');
      return;
    }

    const loadData = async () => {
      try {
        setLoading(true);
        const [pathRes, dashboardRes] = await Promise.allSettled([
          api.get('/api/learning/path'),
          api.get('/api/progress/dashboard'),
        ]);

        let pathData: LearningPathData | null = null;
        let dashboardData: DashboardData | null = null;

        if (pathRes.status === 'fulfilled') {
          pathData = pathRes.value.data;
          setLearningPath(pathData);
        }

        if (dashboardRes.status === 'fulfilled') {
          dashboardData = dashboardRes.value.data;
          setDashboard(dashboardData);
        }

        // Check if all lessons are completed
        if (pathData && pathData.completed_lessons === pathData.total_lessons && pathData.total_lessons === 5) {
          setIsAllCompleted(true);
        } else if (dashboardData && dashboardData.completed_lessons === 5 && dashboardData.total_lessons === 5) {
          setIsAllCompleted(true);
        } else {
          // Redirect back to dashboard if not all lessons are completed
          router.replace('/dashboard');
          return;
        }
      } catch (err) {
        console.error('Error loading completion data:', err);
        setError('Unable to load completion data. Redirecting to dashboard.');
        setTimeout(() => router.replace('/dashboard'), 2000);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [router]);

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900">
        <div className="text-center">
          <div className="text-2xl font-semibold text-white">Loading your completion…</div>
          <div className="mt-2 text-slate-400">This is exciting!</div>
        </div>
      </main>
    );
  }

  if (error || !isAllCompleted) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900 px-4">
        <div className="rounded-[2rem] border border-red-200/30 bg-red-500/10 p-8 text-center">
          <p className="text-lg font-semibold text-red-100">{error || 'Unable to display completion page'}</p>
          <Link href="/dashboard" className="mt-4 inline-block rounded-full bg-indigo-600 px-6 py-3 font-semibold text-white">
            Back to Dashboard
          </Link>
        </div>
      </main>
    );
  }

  const pathName = learningPath?.path_name || dashboard?.learning_path || 'Learning Path';
  const userName = dashboard?.full_name || 'Learner';
  const role = learningPath?.role || dashboard?.target_role || 'data-analyst';
  const score = dashboard?.skill_score || 0;
  const skillsGained = SKILLS_GAINED[role] || SKILLS_GAINED['data-analyst'];

  const completedLessons = learningPath?.lessons || [];

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900 px-4 py-10 text-slate-100">
      <BackButton />
      <div className="mx-auto max-w-4xl space-y-8">
        {/* Header */}
        <div className="rounded-[2rem] border border-white/10 bg-white/10 p-6 shadow-[0_30px_80px_rgba(15,23,42,0.45)] backdrop-blur-xl">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm text-slate-300">SkillBridge EU</p>
              <h1 className="text-2xl font-semibold text-white">Your Learning Journey</h1>
            </div>
            <LogoutButton />
          </div>
        </div>

        {/* Hero Celebration Section */}
        <div className="rounded-[2rem] border border-emerald-500/30 bg-gradient-to-br from-emerald-500/10 to-emerald-500/5 p-8 shadow-[0_30px_80px_rgba(15,23,42,0.45)] text-center">
          <div className="mb-4 text-6xl">🎉</div>
          <h2 className="text-4xl font-bold text-emerald-100">You completed your learning path!</h2>
          <p className="mt-4 text-xl text-emerald-200/80">
            {userName}, you've successfully finished the <span className="font-semibold">{pathName}</span>
          </p>

          {/* Completion Stats */}
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-4">
              <div className="text-sm font-semibold uppercase tracking-[0.15em] text-emerald-200">Lessons Completed</div>
              <div className="mt-2 text-3xl font-bold text-emerald-100">5/5</div>
            </div>
            <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-4">
              <div className="text-sm font-semibold uppercase tracking-[0.15em] text-emerald-200">Progress</div>
              <div className="mt-2 text-3xl font-bold text-emerald-100">100%</div>
            </div>
            <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-4">
              <div className="text-sm font-semibold uppercase tracking-[0.15em] text-emerald-200">Your Score</div>
              <div className="mt-2 text-3xl font-bold text-emerald-100">{score}/100</div>
            </div>
          </div>
        </div>

        {/* Path Summary Section */}
        <div className="rounded-[2rem] border border-slate-700/50 bg-slate-800/30 p-8">
          <h3 className="text-2xl font-semibold text-white">Your Completed Path</h3>
          <p className="mt-2 text-slate-300">{pathName}</p>

          <div className="mt-8 space-y-3">
            {completedLessons.map((lesson, index) => (
              <div key={lesson.id} className="flex items-start gap-4 rounded-lg border border-slate-700/50 bg-slate-900/30 p-4">
                <div className="mt-1 text-2xl text-emerald-400">✓</div>
                <div className="flex-1">
                  <div className="font-semibold text-white">{lesson.title}</div>
                  <div className="mt-1 flex flex-wrap gap-2">
                    <span className="rounded-full bg-slate-700/50 px-3 py-1 text-xs font-semibold capitalize text-slate-300">
                      {lesson.level}
                    </span>
                    <span className="rounded-full bg-slate-700/50 px-3 py-1 text-xs font-semibold text-slate-300">
                      Lesson {index + 1} of 5
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* What You Gained Section */}
        <div className="rounded-[2rem] border border-indigo-500/30 bg-gradient-to-br from-indigo-500/10 to-indigo-500/5 p-8">
          <h3 className="text-2xl font-semibold text-white">What You Gained</h3>
          <p className="mt-2 text-slate-300">Key skills and capabilities you've developed on this path:</p>

          <ul className="mt-6 space-y-3">
            {skillsGained.map((skill, index) => (
              <li key={index} className="flex gap-3 text-slate-100">
                <span className="mt-1 flex-shrink-0 text-indigo-400">⭐</span>
                <span>{skill}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Next Steps Section */}
        <div className="rounded-[2rem] border border-amber-500/30 bg-gradient-to-br from-amber-500/10 to-amber-500/5 p-8">
          <h3 className="text-2xl font-semibold text-white">What's Next?</h3>
          <p className="mt-2 text-slate-300">You've built a strong foundation. Here's what you can do next:</p>

          <div className="mt-8 space-y-4">
            <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-4">
              <p className="font-semibold text-amber-100">Continue Learning</p>
              <p className="mt-1 text-sm text-amber-200/70">
                Explore the next learning path to deepen your expertise and unlock more advanced roles.
              </p>
            </div>
            <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-4">
              <p className="font-semibold text-amber-100">View Job Matches</p>
              <p className="mt-1 text-sm text-amber-200/70">
                See which positions align with your new skills and experience level.
              </p>
            </div>
            <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-4">
              <p className="font-semibold text-amber-100">Back to Dashboard</p>
              <p className="mt-1 text-sm text-amber-200/70">
                Review your progress, check your score, and explore other areas.
              </p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-4 rounded-[2rem] border border-slate-700/50 bg-slate-800/30 p-8">
          <Link
            href="/dashboard"
            className="flex-1 rounded-full bg-indigo-600 px-6 py-4 text-center font-semibold text-white transition hover:bg-indigo-700"
          >
            Continue Learning
          </Link>
          <Link
            href="/jobs"
            className="flex-1 rounded-full border border-slate-600 px-6 py-4 text-center font-semibold text-slate-100 transition hover:border-slate-500 hover:bg-slate-800/50"
          >
            View All Jobs
          </Link>
          <Link
            href="/dashboard"
            className="flex-1 rounded-full border border-slate-600 px-6 py-4 text-center font-semibold text-slate-100 transition hover:border-slate-500 hover:bg-slate-800/50"
          >
            Back to Dashboard
          </Link>
        </div>
      </div>
    </main>
  );
}
