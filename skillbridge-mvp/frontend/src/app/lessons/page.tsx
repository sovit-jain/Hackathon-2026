'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import LogoutButton from '@/components/LogoutButton';
import BackButton from '@/components/BackButton';

type Lesson = {
  id: string;
  title: string;
  description: string;
  level: string;
  estimated_minutes: number;
  completed: boolean;
};

export default function LessonsPage() {
  const router = useRouter();
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const hasLoaded = useRef(false);

  useEffect(() => {
    if (hasLoaded.current) {
      return;
    }
    hasLoaded.current = true;

    const token = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_token') : null;
    if (!token) {
      router.replace('/login');
      return;
    }

    api.get('/api/learning/lessons').then((response) => setLessons(response.data));
  }, [router]);

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-10">
      <BackButton />
      <div className="mx-auto max-w-5xl">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm text-slate-500">Your roadmap</p>
            <h1 className="text-3xl font-semibold">Learning path</h1>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <Link href="/dashboard" className="rounded-full border border-slate-300 px-4 py-2 font-semibold text-slate-700">Back to dashboard</Link>
            <LogoutButton />
          </div>
        </div>

        <div className="grid gap-4">
          {lessons.length === 0 ? (
            <div className="rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-sm">
              <h2 className="text-lg font-semibold">No lessons are available right now</h2>
              <p className="mt-2 text-sm text-slate-600">Your learning plan is being prepared. Please refresh in a moment.</p>
            </div>
          ) : (
            lessons.map((lesson) => (
              <div key={lesson.id} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-sm font-semibold uppercase tracking-wide text-indigo-600">{lesson.level}</p>
                    <h2 className="mt-1 text-xl font-semibold">{lesson.title}</h2>
                    <p className="mt-2 text-slate-600">{lesson.description}</p>
                  </div>
                  <div className="rounded-full bg-slate-100 px-3 py-2 text-sm text-slate-600">{lesson.estimated_minutes} min</div>
                </div>
                <div className="mt-4 flex items-center justify-between">
                  <span className={`rounded-full px-3 py-1 text-sm ${lesson.completed ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
                    {lesson.completed ? 'Completed' : 'In progress'}
                  </span>
                  <Link href={`/lessons/${lesson.id}`} className="rounded-full bg-indigo-600 px-4 py-2 font-semibold text-white">Open lesson</Link>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </main>
  );
}
