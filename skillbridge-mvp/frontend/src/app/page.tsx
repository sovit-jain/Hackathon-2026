'use client';

import Link from 'next/link';
import BackButton from '@/components/BackButton';

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900 text-white">
      <BackButton />
      <section className="mx-auto flex max-w-6xl flex-col gap-10 px-6 py-20 lg:px-8">
        <nav className="flex items-center justify-between rounded-full border border-white/10 bg-white/10 px-6 py-3 backdrop-blur">
          <div className="text-xl font-semibold">DB Career Navigator</div>
          <div className="flex gap-3">
            <Link href="/login" className="rounded-full border border-white/20 px-4 py-2 text-sm">Login</Link>
            <Link href="/signup" className="rounded-full bg-[#0018A8] px-4 py-2 text-sm font-semibold text-white">Sign up</Link>
          </div>
        </nav>

        <div className="grid items-center gap-12 lg:grid-cols-[1.15fr_0.85fr]">
          <div className="space-y-6">
            <span className="inline-flex rounded-full border border-[#0018A8]/40 bg-[#0018A8]/10 px-3 py-1 text-sm text-blue-100">
              🎯 Deutsche Bank readiness · 💡 Role-specific gap analysis · 🚀 AI career navigator
            </span>
            <h1 className="text-4xl font-semibold leading-tight sm:text-6xl">
              Build your Deutsche Bank career path
            </h1>
            <p className="max-w-2xl text-lg text-slate-300">
              DB Career Navigator personalizes your Deutsche Bank Readiness Plan, compares your current skills against target roles, and recommends the next best skills and opportunities to move your career forward.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link href="/signup" className="rounded-full bg-[#0018A8] px-6 py-3 font-semibold text-white hover:bg-[#00118a] transition">START YOUR JOURNEY</Link>
              <Link href="/dashboard" className="rounded-full border border-white/20 px-6 py-3 font-semibold text-slate-100 hover:bg-white/5 transition">View demo</Link>
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/10 p-8 shadow-2xl">
            <h2 className="text-2xl font-semibold">What the platform does</h2>
            <ul className="mt-6 space-y-4 text-slate-300">
              <li>• Deutsche Bank role readiness scoring</li>
              <li>• AI gap analysis for target roles</li>
              <li>• Personalized DB Readiness Plan</li>
              <li>• Deutsche Bank opportunities matched to your profile</li>
            </ul>
          </div>
        </div>
      </section>
    </main>
  );
}
