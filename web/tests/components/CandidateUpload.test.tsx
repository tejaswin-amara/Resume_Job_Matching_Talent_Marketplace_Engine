import React from 'react';
import { afterEach, expect, test, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import CandidatePortal from '@/app/candidates/page';
import { UploadDropzone } from '@/components/reactbits/UploadDropzone';

afterEach(() => { cleanup(); vi.unstubAllGlobals(); vi.restoreAllMocks(); });

test('upload displays extracted skills and matches with the stored candidate ID', async () => {
  vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(null);
  const fetchMock = vi.fn().mockImplementation(async (url: string) => ({
    ok: true,
    json: async () => url.endsWith('/upload')
      ? { id: 'candidate-id', skills_extracted: ['Python'] }
      : url.endsWith('/jobs')
        ? [{ id: 'job-id', title: 'Engineer', description: 'Build APIs', requirements: 'Python' }]
        : { candidate_id: 'candidate-id', job_id: 'job-id', total_score: 85.4,
            semantic_score: 0.9, skill_score: 0.8, experience_score: 0.7, education_score: 1,
            matched_skills: [], missing_skills: [], suggestions: [] },
  }));
  vi.stubGlobal('fetch', fetchMock);
  const { container } = render(<CandidatePortal />);
  const file = new File(['Python'], 'resume.txt', { type: 'text/plain' });
  fireEvent.change(container.querySelector('input[type="file"]')!, { target: { files: [file] } });
  expect(await screen.findByText('Python')).toBeDefined();
  await waitFor(() => expect(fetchMock).toHaveBeenCalledWith('/api/v1/match/adhoc', expect.objectContaining({
    body: JSON.stringify({ candidate_id: 'candidate-id', job_id: 'job-id' }),
  })));
  expect(screen.queryByText('0 roles found')).toBeNull();
  await waitFor(() => expect(container.querySelector('[style*="width: 85%"]')).not.toBeNull());
  expect(container.querySelector('[style*="width: 90%"]')).not.toBeNull();
});

test('drop prevents navigation and uploads only the first file; empty drops do nothing', () => {
  const onUpload = vi.fn();
  const { container } = render(<UploadDropzone onUpload={onUpload} />);
  const target = container.firstChild!;
  const file = new File(['Python'], 'resume.txt');
  expect(fireEvent.dragOver(target)).toBe(false);
  expect(fireEvent.drop(target, { dataTransfer: { files: [file, new File([], 'other.txt')] } })).toBe(false);
  expect(onUpload).toHaveBeenCalledWith(file);
  fireEvent.drop(target, { dataTransfer: { files: [] } });
  expect(onUpload).toHaveBeenCalledTimes(1);
});
