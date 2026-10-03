import { expect, test } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Badge } from '@/components/ui/badge';

test('Badge renders default variant with child text', () => {
  render(<Badge>Default Badge</Badge>);
  const badge = screen.getByText('Default Badge');
  expect(badge).toBeDefined();
  expect(badge.className).toContain('bg-gray-800');
});

test('Badge renders success variant styling', () => {
  render(<Badge variant="success">Skill Matched</Badge>);
  const badge = screen.getByText('Skill Matched');
  expect(badge).toBeDefined();
  expect(badge.className).toContain('text-green-400');
});

test('Badge renders danger and outline variants', () => {
  const { rerender } = render(<Badge variant="danger">Skill Gap</Badge>);
  let badge = screen.getByText('Skill Gap');
  expect(badge.className).toContain('text-red-400');

  rerender(<Badge variant="outline">Remote</Badge>);
  badge = screen.getByText('Remote');
  expect(badge.className).toContain('border-gray-700');
});
