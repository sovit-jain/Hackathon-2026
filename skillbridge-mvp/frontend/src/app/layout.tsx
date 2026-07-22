import type { Metadata } from 'next';
import './globals.css';
import '@/lib/api';

export const metadata: Metadata = {
  title: 'SkillBridge',
  description: 'AI-powered personalized learning for career growth',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
