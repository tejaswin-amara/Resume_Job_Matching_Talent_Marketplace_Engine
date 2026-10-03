import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Rate } from 'k6/metrics';

const matchLatency = new Trend('match_engine_p95_latency', true);
const successRate = new Rate('match_engine_success_rate');

export const options = {
  vus: 10,
  duration: '10s',
  thresholds: {
    http_req_duration: ['p(95)<500'], // p95 latency under 500ms
    http_req_failed: ['rate<0.01'],    // error rate under 1%
    match_engine_success_rate: ['rate>0.99'],
  },
};

export default function () {
  const targetUrl = __ENV.TARGET_URL || 'http://localhost:8000/api/v1/marketplace/match';

  const payload = JSON.stringify({
    job_id: 'req-backend-lead',
    title: 'Senior Backend Engineer',
    required_skills: ['Python', 'FastAPI', 'PostgreSQL', 'pgvector'],
    min_experience: 5,
    candidate_limit: 10,
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const res = http.post(targetUrl, payload, params);

  const passed = check(res, {
    'status is 200': (r) => r.status === 200,
    'has matches array': (r) => {
      try {
        const body = JSON.parse(r.body);
        return Array.isArray(body.matches) && body.status === 'success';
      } catch (e) {
        return false;
      }
    },
  });

  successRate.add(passed);
  matchLatency.add(res.timings.duration);
  sleep(0.5);
}
