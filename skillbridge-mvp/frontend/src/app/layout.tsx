import type { Metadata } from 'next';
import './globals.css';
import '@/lib/api';

export const metadata: Metadata = {
  title: 'DB Career Navigator',
  description: 'AI-powered Deutsche Bank career readiness and progression planning',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
