'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import BackButton from '@/components/BackButton';

type AssessmentResult = {
  score: number;
  level: string;
  label?: string;
  summary?: string;
  top_skill?: string;
  missing_key_skill?: string;
  explanation?: string;
};

export default function AssessmentCompletePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [assessmentData, setAssessmentData] = useState<AssessmentResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_token') : null;
    if (!token) {
      router.replace('/login');
      return;
    }

    // Parse assessment data from URL params (or from local storage if passed via state)
    const dataStr = searchParams.get('data');
    if (dataStr) {
      try {
        const data = JSON.parse(decodeURIComponent(dataStr));
        setAssessmentData(data);
      } catch (error) {
        console.error('Failed to parse assessment data:', error);
      }
    } else {
      // Try to get from localStorage as fallback
      const stored = typeof window !== 'undefined' ? window.localStorage.getItem('skillbridge_assessment_result') : null;
      if (stored) {
        try {
          setAssessmentData(JSON.parse(stored));
        } catch (error) {
          console.error('Failed to parse stored assessment data:', error);
        }
      }
    }
    setLoading(false);
  }, [searchParams, router]);

  const handleContinue = () => {
    router.push('/onboarding?step=dream-job');
  };

  if (loading) {
    return <main className="flex min-h-screen items-center justify-center text-lg">Loading…</main>;
  }

  if (!assessmentData) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900 px-4 py-10 text-slate-100 flex items-center justify-center">
        <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-8 text-center">
          <h1 className="text-2xl font-semibold text-red-200">Assessment Data Not Found</h1>
          <p className="mt-2 text-red-100/80">Please go back and complete your assessment again.</p>
          <button
            onClick={() => router.push('/onboarding')}
            className="mt-4 rounded-xl bg-red-600 px-6 py-2 font-semibold text-white hover:bg-red-700"
          >
            Go Back
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900 px-4 py-10 text-slate-100">
      <BackButton />
      <div className="mx-auto max-w-2xl">
        <section className="rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-[0_30px_80px_rgba(15,23,42,0.5)] backdrop-blur-xl">
          {/* Success Header */}
          <div className="mb-8 text-center">
            <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full bg-emerald-500/20">
              <span className="text-3xl">✅</span>
            </div>
            <h1 className="text-3xl font-bold text-white">Assessment Complete!</h1>
            <p className="mt-2 text-slate-300">We've analyzed your current skill level</p>
          </div>

          {/* Score Card */}
          <div className="mb-8 rounded-2xl border border-indigo-500/30 bg-gradient-to-br from-indigo-500/10 to-indigo-500/5 p-6">
            <div className="grid grid-cols-2 gap-6">
              {/* Score */}
              <div className="text-center">
                <div className="mb-2 text-sm font-semibold uppercase tracking-[0.15em] text-indigo-200">
                  Your Score
                </div>
                <div className="flex items-baseline justify-center gap-1">
                  <span className="text-5xl font-bold text-white">{assessmentData.score}</span>
                  <span className="text-2xl text-slate-400">/100</span>
                </div>
              </div>

              {/* Level */}
              <div className="text-center">
                <div className="mb-2 text-sm font-semibold uppercase tracking-[0.15em] text-indigo-200">
                  Your Level
                </div>
                <div className="flex flex-col items-center justify-center gap-1">
                  <div className="text-2xl font-bold text-white capitalize">
                    {assessmentData.label || assessmentData.level}
                  </div>
                  <div className="text-sm text-slate-400">
                    {assessmentData.score >= 70 ? 'Level 10/10' : assessmentData.score >= 40 ? 'Level 5-7/10' : 'Level 2/10'}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Assessment Summary */}
          <div className="mb-8 space-y-4 rounded-2xl border border-slate-700/50 bg-slate-800/30 p-6">
            <div>
              <h2 className="mb-2 text-sm font-semibold uppercase tracking-[0.15em] text-slate-300">
                Your Assessment
              </h2>
              <p className="text-base leading-relaxed text-slate-100">
                {assessmentData.summary || assessmentData.explanation}
              </p>
            </div>
          </div>

          {/* Skills Highlights */}
          <div className="mb-8 grid gap-4 md:grid-cols-2">
            {/* Top Skill */}
            <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4">
              <div className="mb-2 text-xs font-semibold uppercase tracking-[0.15em] text-emerald-200">
                ⭐ Your Strength
              </div>
              <p className="text-lg font-semibold text-emerald-100">
                {assessmentData.top_skill || 'N/A'}
              </p>
              <p className="mt-1 text-sm text-emerald-200/70">
                Your strongest skill to build upon
              </p>
            </div>

            {/* Next Step */}
            <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4">
              <div className="mb-2 text-xs font-semibold uppercase tracking-[0.15em] text-amber-200">
                🎯 Next Step
              </div>
              <p className="text-lg font-semibold text-amber-100">
                Choose your target role
              </p>
              <p className="mt-1 text-sm text-amber-200/70">
                Your next step will shape the learning path and focus areas for you.
              </p>
            </div>
          </div>

          {/* Learning Path */}
          <div className="mb-8 rounded-2xl border border-blue-500/30 bg-blue-500/10 p-6">
            <div className="flex items-start gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-500/20 text-blue-200">
                📚
              </div>
              <div>
                <h3 className="mb-2 font-semibold text-blue-100">Your Learning Path</h3>
                <p className="text-sm leading-relaxed text-blue-200/80">
                  Your assessment score helps us shape the next lessons, and your selected role will refine the path once you continue.
                </p>
              </div>
            </div>
          </div>

          {/* Continue Button */}
          <button
            onClick={handleContinue}
            className="w-full rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 px-6 py-4 font-semibold text-white shadow-lg transition hover:from-indigo-700 hover:to-blue-700"
          >
            Continue to Your Goal →
          </button>

          {/* Back Button */}
          <button
            onClick={() => router.push('/onboarding')}
            className="mt-3 w-full rounded-xl border border-slate-500 px-6 py-2 font-semibold text-slate-200 transition hover:border-slate-400 hover:bg-slate-800/50"
          >
            Back to Assessment
          </button>
        </section>
      </div>
    </main>
  );
}
