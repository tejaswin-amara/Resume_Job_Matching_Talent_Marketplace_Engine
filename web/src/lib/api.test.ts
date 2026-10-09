import { afterEach, expect, test, vi } from 'vitest';
import { api } from './api';

afterEach(() => { vi.unstubAllGlobals(); });

test('parseText encodes text in the backend query parameter', async () => {
  const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ skills: ['python'] }) });
  vi.stubGlobal('fetch', fetchMock);
  const text = 'Python & C++\n東京?';
  expect(await api.parseText(text)).toEqual({ skills: ['python'] });
  const [url, options] = fetchMock.mock.calls[0];
  expect(new URL(url, 'http://localhost').searchParams.get('text')).toBe(text);
  expect(options).toEqual({ method: 'POST' });
});

test('adhocMatch sends candidate and job identifiers', async () => {
  const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ total_score: 85 }) });
  vi.stubGlobal('fetch', fetchMock);
  await api.adhocMatch('candidate-id', 'job-id');
  const [url, options] = fetchMock.mock.calls[0];
  expect(url).toBe('/api/v1/match/adhoc');
  expect(JSON.parse(options.body)).toEqual({ candidate_id: 'candidate-id', job_id: 'job-id' });
});
