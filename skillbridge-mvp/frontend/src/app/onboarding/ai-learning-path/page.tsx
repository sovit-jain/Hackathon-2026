'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import BackButton from '@/components/BackButton';

type PathLesson = {
  id: string;
  title: string;
  description: string;
  level: string;
  estimated_minutes: number;
  lesson_order: number;
  completed: boolean;
};

type LearningPathData = {
  path_name: string;
  role: string;
  target_role: string;
  level: string;
  score: number;
  explanation: string;
  lessons: PathLesson[];
};

export default function LearningPathTransitionPage() {
  const router = useRouter();
  const [progress, setProgress] = useState(12);
  const [status, setStatus] = useState('Preparing your personal learning path…');
  const [pathData, setPathData] = useState<LearningPathData | null>(null);

  useEffect(() => {
    const token = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_token') : null;
    if (!token) {
      router.replace('/login');
      return;
    }

    const messages = [
      'Reviewing your assessment and goals…',
      'Matching you with a tailored learning path…',
      'Preparing your dashboard experience…',
    ];

    const messageTimer = window.setInterval(() => {
      setStatus((current) => {
        const currentIndex = messages.indexOf(current);
        const nextIndex = (currentIndex + 1) % messages.length;
        return messages[nextIndex];
      });
    }, 900);

    const progressTimer = window.setInterval(() => {
      setProgress((current) => (current >= 100 ? 100 : current + 10));
    }, 220);

    const loadPath = async () => {
      try {
        const storedAssessment = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_assessment_result') : null;
        const storedRole = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_target_role') : null;
        const storedHours = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_weekly_hours') : null;
        const storedName = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_user_name') : null;
        const parsedAssessment = storedAssessment ? JSON.parse(storedAssessment) : null;

        const profilePayload = {
          name: storedName || '',
          target_role: storedRole || 'data-analyst',
          weekly_hours: storedHours ? Number(storedHours) : 5,
          current_level: parsedAssessment?.level || 'beginner',
        };

        const [profileResponse, pathResponse] = await Promise.all([
          api.post('/api/user/profile', profilePayload),
          api.get('/api/learning/path'),
        ]);

        const data = pathResponse.data as LearningPathData;
        setPathData(data);
        setStatus('All set — opening your dashboard now.');
        setProgress(100);
        if (typeof window !== 'undefined') {
          window.localStorage.setItem('skillbridge_learning_path', JSON.stringify(data));
          window.localStorage.setItem('skillbridge_target_role', profilePayload.target_role);
          window.localStorage.setItem('skillbridge_weekly_hours', String(profilePayload.weekly_hours));
          window.localStorage.setItem('skillbridge_user_name', storedName || profileResponse.data?.profile?.name || 'Raj');
        }
        window.setTimeout(() => router.replace('/dashboard'), 900);
      } catch {
        setStatus('We hit a snag while building your path, but you can continue to the dashboard.');
        setProgress(100);
        window.setTimeout(() => router.replace('/dashboard'), 1200);
      }
    };

    loadPath();

    return () => {
      window.clearInterval(messageTimer);
      window.clearInterval(progressTimer);
    };
  }, [router]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900 px-4 py-10 text-slate-100">
      <BackButton />
      <div className="w-full max-w-3xl rounded-[2rem] border border-white/10 bg-white/10 p-8 shadow-[0_30px_80px_rgba(15,23,42,0.45)] backdrop-blur-xl">
        <div className="inline-flex items-center gap-2 rounded-full bg-indigo-500/15 px-4 py-2 text-sm font-semibold text-indigo-100 ring-1 ring-indigo-400/20">
          <span>Step 5</span>
          <span className="text-slate-300">AI learning path</span>
        </div>

        <h1 className="mt-5 text-3xl font-semibold text-white">Creating your next learning path</h1>
        <p className="mt-3 max-w-2xl text-slate-300">
          We are using your assessment score, your dream role, and your current level to build a path that feels practical and motivating.
        </p>

        <div className="mt-8">
          <div className="mb-3 flex items-center justify-between text-sm text-slate-300">
            <span>{status}</span>
            <span>{progress}%</span>
          </div>
          <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-800">
            <div className="h-full rounded-full bg-gradient-to-r from-indigo-500 via-sky-400 to-cyan-300 transition-all duration-300" style={{ width: `${progress}%` }} />
          </div>
        </div>

        {pathData ? (
          <div className="mt-8 rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-indigo-200">Your path</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">{pathData.path_name}</h2>
            <p className="mt-3 text-slate-300">{pathData.explanation}</p>
            <div className="mt-4 flex flex-wrap gap-2 text-sm text-slate-300">
              <span className="rounded-full bg-white/10 px-3 py-1">Score: {pathData.score}%</span>
              <span className="rounded-full bg-white/10 px-3 py-1">Level: {pathData.level}</span>
              <span className="rounded-full bg-white/10 px-3 py-1">Role: {pathData.role}</span>
            </div>
          </div>
        ) : null}
      </div>
    </main>
  );
}
