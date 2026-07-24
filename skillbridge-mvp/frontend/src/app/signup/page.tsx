'use client';

import { FormEvent, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import api from '@/lib/api';
import BackButton from '@/components/BackButton';

export default function SignupPage() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (typeof window !== 'undefined' && window.localStorage.getItem('skillbridge_token')) {
      router.replace('/dashboard');
    }
  }, [router]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');

    try {
      const response = await api.post('/api/auth/register', { name, email, password });
      window.localStorage.setItem('skillbridge_token', response.data.access_token);
      window.localStorage.setItem('skillbridge_user_name', response.data.user.name);
      console.debug('signup stored token', response.data.access_token?.slice(0, 10));
      router.push('/onboarding');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to create account');
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <BackButton />
      <div className="mx-auto flex min-h-screen max-w-6xl items-center justify-center px-4 py-16">
        <div className="grid w-full gap-8 rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-[0_30px_120px_rgba(15,23,42,0.35)] backdrop-blur-xl lg:grid-cols-[0.95fr_1.05fr] lg:p-0">
          <section className="relative overflow-hidden rounded-[2rem] bg-gradient-to-br from-sky-600 via-indigo-700 to-slate-950 p-10 text-white">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(56,189,248,0.35),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(167,139,250,0.18),_transparent_30%)]" />
            <div className="relative space-y-6">
              <span className="inline-flex rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm uppercase tracking-[0.2em] text-sky-100/90">
                Get started
              </span>
              <h1 className="text-4xl font-semibold leading-tight sm:text-5xl">
                Join DB Career Navigator and accelerate your readiness.
              </h1>
              <p className="max-w-xl text-sm leading-6 text-slate-100/85 sm:text-base">
                Create an account to unlock Deutsche Bank role readiness planning, tailored learning, and opportunity matching.
              </p>
              <div className="space-y-3 rounded-3xl border border-white/10 bg-white/5 p-5 text-sm text-slate-100/80 shadow-inner shadow-white/5">
                <p>• Personalized onboarding</p>
                <p>• Role readiness tracking</p>
                <p>• Deutsche Bank opportunity matching</p>
              </div>
            </div>
          </section>

          <section className="rounded-[2rem] bg-slate-950/95 p-10 shadow-2xl shadow-slate-950/20 ring-1 ring-white/10 backdrop-blur-xl">
            <div className="mb-8">
              <h2 className="text-3xl font-semibold">Create your account</h2>
              <p className="mt-2 text-sm text-slate-400">Start your Deutsche Bank career readiness journey with DB Career Navigator.</p>
            </div>
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="mb-3 block text-sm font-medium text-slate-300">Name</label>
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  type="text"
                  required
                  className="w-full rounded-3xl border border-slate-700 bg-slate-900/80 px-4 py-3 text-white shadow-sm outline-none transition focus:border-sky-400 focus:ring-4 focus:ring-sky-500/10"
                />
              </div>
              <div>
                <label className="mb-3 block text-sm font-medium text-slate-300">Email</label>
                <input
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  type="email"
                  required
                  className="w-full rounded-3xl border border-slate-700 bg-slate-900/80 px-4 py-3 text-white shadow-sm outline-none transition focus:border-sky-400 focus:ring-4 focus:ring-sky-500/10"
                />
              </div>
              <div>
                <label className="mb-3 block text-sm font-medium text-slate-300">Password</label>
                <input
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  type="password"
                  required
                  className="w-full rounded-3xl border border-slate-700 bg-slate-900/80 px-4 py-3 text-white shadow-sm outline-none transition focus:border-sky-400 focus:ring-4 focus:ring-sky-500/10"
                />
              </div>
              {error ? <p className="text-sm text-rose-400">{error}</p> : null}
              <button
                type="submit"
                className="w-full rounded-3xl bg-gradient-to-r from-sky-500 via-indigo-500 to-fuchsia-500 px-5 py-3 text-base font-semibold text-white shadow-lg shadow-sky-500/20 transition hover:scale-[1.01]"
              >
                Create account
              </button>
            </form>
            <p className="mt-6 text-sm text-slate-500">
              Already have an account? <Link href="/login" className="font-semibold text-white">Log in</Link>
            </p>
          </section>
        </div>
      </div>
    </main>
  );
}
