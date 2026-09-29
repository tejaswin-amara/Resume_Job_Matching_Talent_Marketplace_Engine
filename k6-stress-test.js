import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 20 },  // Ramp up to 20 VUs
    { duration: '20s', target: 50 },  // Heavy rate-attack benchmark
    { duration: '10s', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests must complete within 500ms
  },
};

export default function () {
  const url = 'http://localhost:8000/api/v1/algorithms/score';
  const payload = JSON.stringify({
    candidate: {
      skills: [{ canonical_skill_id: 'python', years_experience: 5 }],
      embedding_vector: [0.1, 0.2, 0.3],
      raw_text: "experienced senior software engineer python java"
    },
    job: {
      required_skills: [{ canonical_skill_id: 'python', weight: 1.0, hard_constraint: true }],
      embedding_vector: [0.1, 0.2, 0.3],
      raw_text: "seeking senior software engineer python"
    },
    weights: { hard: 0.5, soft: 0.5 }
  });

  const params = {
    headers: { 'Content-Type': 'application/json' },
  };

  const res = http.post(url, payload, params);
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response score present': (r) => r.json().hasOwnProperty('score'),
  });

  sleep(0.1);
}
