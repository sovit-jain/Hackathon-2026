import { Suspense } from 'react';
import AssessmentCompleteClient from './AssessmentCompleteClient';

export default function Page() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <AssessmentCompleteClient />
    </Suspense>
  );
}
