'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import api from '@/lib/api';
import BackButton from '@/components/BackButton';
import LogoutButton from '@/components/LogoutButton';

type LessonDetail = {
  id: string;
  title: string;
  description: string;
  category: string;
  level: string;
  estimated_minutes: number;
  lesson_order: number;
  completed: boolean;
  generated_content: string | null;
};

type ParsedLessonContent = {
  learnPoints: string[];
  introduction: string[];
  keyConcepts: Array<{ name: string; explanation: string; example: string }>;
  scenario: string;
  takeaways: string[];
  quickCheck: string[];
};

const parseGeneratedContent = (content: string): ParsedLessonContent | null => {
  if (!content) {
    return null;
  }

  const normalized = content
    .replace(/\r/g, '')
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/`/g, '')
    .replace(/^#{1,6}\s*/gm, '');
  const sectionRegex = /^(WHAT YOU WILL LEARN:|INTRODUCTION:|KEY CONCEPTS:|REAL WORLD SCENARIO:|KEY TAKEAWAYS:|QUICK CHECK:)$/gm;
  const headings = [...normalized.matchAll(sectionRegex)].map((match) => ({ title: match[1], index: match.index ?? 0 }));
  if (headings.length === 0) {
    return null;
  }

  const sections: Record<string, string> = {};
  for (let idx = 0; idx < headings.length; idx += 1) {
    const current = headings[idx];
    const next = headings[idx + 1];
    const start = current.index + current.title.length + 1;
    const end = next ? next.index : normalized.length;
    sections[current.title] = normalized.substring(start, end).trim();
  }

  const parseList = (text: string) =>
    text
      .split('\n')
      .map((line) => line.trim())
      .filter((line) => line.startsWith('- '))
      .map((line) => line.replace(/^-\s*/, '').trim());

  const parseQuickCheck = (text: string) =>
    text
      .split('\n')
      .map((line) => line.trim())
      .filter((line) => /^[0-9]+\.\s+/.test(line))
      .map((line) => line.replace(/^[0-9]+\.\s*/, '').trim());

  const parseKeyConcepts = (text: string) => {
    const lines = text.split('\n').map((line) => line.trim()).filter(Boolean);
    const concepts: Array<{ name: string; explanation: string; example: string }> = [];
    let current: { name: string; explanation: string; example: string } | null = null;

    for (const line of lines) {
      const headingMatch = line.match(/^[0-9]+\.\s*(.+)$/);
      const exampleMatch = line.match(/^Example:\s*(.+)$/i);
      if (headingMatch) {
        if (current) {
          concepts.push(current);
        }
        current = { name: headingMatch[1].trim(), explanation: '', example: '' };
        continue;
      }
      if (exampleMatch && current) {
        current.example = exampleMatch[1].trim();
        continue;
      }
      if (current) {
        const existing = current.explanation ? `${current.explanation} ${line}` : line;
        current.explanation = existing.trim();
      }
    }
    if (current) {
      concepts.push(current);
    }
    return concepts;
  };

  const learnPoints = parseList(sections['WHAT YOU WILL LEARN:'] || '');
  const takeaways = parseList(sections['KEY TAKEAWAYS:'] || '');
  const introduction = (sections['INTRODUCTION:'] || '')
    .split(/\n\s*\n/)
    .map((paragraph) => paragraph.trim())
    .filter(Boolean);
  const scenario = (sections['REAL WORLD SCENARIO:'] || '').trim();
  const quickCheck = parseQuickCheck(sections['QUICK CHECK:'] || '');
  const keyConcepts = parseKeyConcepts(sections['KEY CONCEPTS:'] || '');

  if (!learnPoints.length || !introduction.length || !keyConcepts.length || !scenario || !takeaways.length) {
    return null;
  }

  return {
    learnPoints,
    introduction,
    keyConcepts,
    scenario,
    takeaways,
    quickCheck,
  };
};

export default function LessonDetailPage() {
  const router = useRouter();
  const params = useParams();
  const lessonId = params?.id as string;
  const [lesson, setLesson] = useState<LessonDetail | null>(null);
  const [allLessons, setAllLessons] = useState<LessonDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showNextButton, setShowNextButton] = useState(false);

  useEffect(() => {
    if (!lessonId) {
      return;
    }

    const loadLesson = async () => {
      setLoading(true);
      setError(null);

      try {
        const [lessonRes, listRes] = await Promise.all([
          api.get(`/api/learning/lessons/${lessonId}`),
          api.get('/api/learning/lessons'),
        ]);
        setLesson(lessonRes.data);
        setAllLessons(listRes.data || []);
      } catch {
        setError('Unable to load the lesson. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    loadLesson();
  }, [lessonId]);

  const parsedContent = useMemo(() => {
    if (!lesson?.generated_content) {
      return null;
    }
    return parseGeneratedContent(lesson.generated_content);
  }, [lesson]);

  const isGeneratingContent = lesson?.generated_content === null;
  const isFallbackContent = lesson?.generated_content === 'Content is being prepared. Please try again in a moment.';

  const nextLessonId = useMemo(() => {
    if (!lesson || allLessons.length === 0) {
      return null;
    }
    const sorted = [...allLessons].sort((a, b) => a.lesson_order - b.lesson_order);
    const currentIndex = sorted.findIndex((item) => item.id === lesson.id);
    if (currentIndex === -1 || currentIndex + 1 >= sorted.length) {
      return null;
    }
    return sorted[currentIndex + 1].id;
  }, [lesson, allLessons]);

  const handleComplete = async () => {
    if (!lesson) {
      return;
    }
    setSaving(true);
    setError(null);

    try {
      await api.post(`/api/learning/lessons/${lesson.id}/complete`);
      setLesson({ ...lesson, completed: true });

      // Check if this was the last lesson (lesson 5 of 5)
      if (lesson.lesson_order === 5 || allLessons.filter((l) => !l.completed).length <= 1) {
        // Redirect to completion page after a brief delay for visual feedback
        setTimeout(() => {
          router.push('/onboarding/path-completion');
        }, 1000);
      } else {
        setShowNextButton(true);
      }
    } catch {
      setError('Unable to mark the lesson complete. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <main className="flex min-h-screen items-center justify-center bg-slate-100 text-lg">Loading lesson…</main>;
  }

  if (!lesson) {
    return (
      <main className="min-h-screen bg-slate-100 px-4 py-10">
        <div className="mx-auto max-w-4xl rounded-3xl bg-white p-10 shadow-sm">Lesson not found.</div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-10">
      <div className="mx-auto max-w-6xl space-y-8">
        <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm text-slate-500">SkillBridge EU</p>
              <h1 className="text-2xl font-semibold text-slate-900">Lesson player</h1>
            </div>
            <div className="flex items-center gap-3">
              <span className="rounded-full bg-indigo-50 px-4 py-2 text-sm font-semibold text-indigo-700">
                {lesson.category.replace(/-/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase())}
              </span>
              <LogoutButton />
            </div>
          </div>
        </div>

        <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <Link href="/dashboard" className="rounded-full border border-slate-300 px-4 py-2 font-semibold text-slate-700">
              ← Back to dashboard
            </Link>
            <div className="rounded-full bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-700">
              Lesson {lesson.lesson_order} of 5
            </div>
          </div>

          <div className="mt-8 space-y-6">
            <div>
              <h2 className="text-4xl font-semibold text-slate-900">{lesson.title}</h2>
              <p className="mt-4 max-w-3xl text-lg leading-8 text-slate-600">{lesson.description}</p>
            </div>

            <div className="flex flex-wrap gap-3">
              <span className="rounded-full bg-indigo-50 px-4 py-2 text-sm font-semibold text-indigo-700">
                Role: {lesson.category.replace(/-/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase())}
              </span>
              <span className="rounded-full bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-700">
                Difficulty: {lesson.level}
              </span>
              <span className="rounded-full bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-700">
                Estimated time: {lesson.estimated_minutes} min read
              </span>
            </div>
          </div>
        </div>

        <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
          {isGeneratingContent ? (
            <div className="rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-10 text-center text-slate-600">
              <p className="text-lg font-semibold">Generating your personalized lesson...</p>
              <p className="mt-3 text-sm">This may take a moment while we prepare the content for you.</p>
            </div>
          ) : error ? (
            <div className="rounded-3xl border border-red-200 bg-red-50 p-8 text-red-700">
              <p className="font-semibold">{error}</p>
            </div>
          ) : parsedContent ? (
            <div className="space-y-10">
              <section>
                <div className="flex items-center gap-3 text-xl font-semibold text-slate-900">
                  <span>📌</span>
                  <span>WHAT YOU WILL LEARN</span>
                </div>
                <ul className="mt-4 space-y-2">
                  {parsedContent.learnPoints.map((point, index) => (
                    <li key={index} className="flex gap-3 text-slate-600">
                      <span className="mt-1 text-indigo-600">•</span>
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </section>

              <section>
                <div className="flex items-center gap-3 text-xl font-semibold text-slate-900">
                  <span>📖</span>
                  <span>INTRODUCTION</span>
                </div>
                <div className="mt-4 space-y-4 text-slate-600">
                  {parsedContent.introduction.map((paragraph, index) => (
                    <p key={index}>{paragraph}</p>
                  ))}
                </div>
              </section>

              <section>
                <div className="flex items-center gap-3 text-xl font-semibold text-slate-900">
                  <span>🔑</span>
                  <span>KEY CONCEPTS</span>
                </div>
                <div className="mt-6 space-y-6">
                  {parsedContent.keyConcepts.map((concept, index) => (
                    <div key={index} className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                      <h3 className="text-lg font-semibold text-slate-900">{concept.name}</h3>
                      <p className="mt-2 text-slate-600">{concept.explanation}</p>
                      <p className="mt-3 text-slate-700"><span className="font-semibold">Example:</span> {concept.example}</p>
                    </div>
                  ))}
                </div>
              </section>

              <section>
                <div className="flex items-center gap-3 text-xl font-semibold text-slate-900">
                  <span>💡</span>
                  <span>REAL WORLD SCENARIO</span>
                </div>
                <p className="mt-4 text-slate-600">{parsedContent.scenario}</p>
              </section>

              <section>
                <div className="flex items-center gap-3 text-xl font-semibold text-slate-900">
                  <span>✅</span>
                  <span>KEY TAKEAWAYS</span>
                </div>
                <ul className="mt-4 space-y-2">
                  {parsedContent.takeaways.map((takeaway, index) => (
                    <li key={index} className="flex gap-3 text-slate-600">
                      <span className="mt-1 text-indigo-600">•</span>
                      <span>{takeaway}</span>
                    </li>
                  ))}
                </ul>
              </section>

              <section>
                <div className="flex items-center gap-3 text-xl font-semibold text-slate-900">
                  <span>🎯</span>
                  <span>QUICK CHECK</span>
                </div>
                <ol className="mt-4 space-y-2 list-decimal pl-5 text-slate-600">
                  {parsedContent.quickCheck.map((question, index) => (
                    <li key={index}>{question}</li>
                  ))}
                </ol>
              </section>
            </div>
          ) : isFallbackContent ? (
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-8 text-slate-700">
              <div className="space-y-4">
                <p className="font-semibold text-slate-900">Content is being prepared.</p>
                <p>Please try again in a moment.</p>
              </div>
            </div>
          ) : (
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-8 text-slate-700">
              <div className="space-y-4">
                <p className="font-semibold text-slate-900">Lesson content is ready.</p>
                <pre className="whitespace-pre-wrap text-sm">{lesson.generated_content}</pre>
              </div>
            </div>
          )}
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3 rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
          <Link href="/dashboard" className="rounded-full border border-slate-300 px-5 py-3 font-semibold text-slate-700">
            ← Back to Dashboard
          </Link>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={handleComplete}
              disabled={lesson.completed || saving}
              className="rounded-full bg-indigo-600 px-5 py-3 font-semibold text-white transition disabled:cursor-not-allowed disabled:bg-slate-300"
            >
              {lesson.completed ? 'Completed ✓' : 'Mark as Complete ✓'}
            </button>
            {showNextButton && nextLessonId ? (
              <Link href={`/lessons/${nextLessonId}`} className="rounded-full bg-slate-900 px-5 py-3 font-semibold text-white">
                Next Lesson →
              </Link>
            ) : null}
          </div>
        </div>
      </div>
    </main>
  );
}
