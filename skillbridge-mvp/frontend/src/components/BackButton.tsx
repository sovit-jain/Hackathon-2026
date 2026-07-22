'use client';

import { useRouter } from 'next/navigation';

export default function BackButton() {
  const router = useRouter();

  const handleBack = () => {
    if (typeof window !== 'undefined' && window.history.length > 1) {
      router.back();
      return;
    }
    router.push('/');
  };

  return (
    <button
      type="button"
      onClick={handleBack}
      className="fixed left-4 top-4 z-50 inline-flex items-center gap-2 rounded-full border border-white/20 bg-slate-950/80 px-3 py-2 text-sm font-semibold text-white shadow-lg backdrop-blur transition hover:bg-slate-900"
    >
      <span aria-hidden="true">←</span>
      <span>Previous</span>
    </button>
  );
}
