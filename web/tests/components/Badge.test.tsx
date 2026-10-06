import { expect, test } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AnimatedBadge } from '@/components/reactbits';

test('AnimatedBadge renders default variant with child text', () => {
  render(<AnimatedBadge>Default Badge</AnimatedBadge>);
  const badge = screen.getByText('Default Badge');
  expect(badge).toBeDefined();
  expect(badge.className).toContain('bg-gray-800');
});

test('AnimatedBadge renders success variant styling', () => {
  render(<AnimatedBadge variant="success">Skill Matched</AnimatedBadge>);
  const badge = screen.getByText('Skill Matched');
  expect(badge).toBeDefined();
  expect(badge.className).toContain('text-green-400');
});

test('AnimatedBadge renders danger and outline variants', () => {
  const { rerender } = render(<AnimatedBadge variant="danger">Skill Gap</AnimatedBadge>);
  let badge = screen.getByText('Skill Gap');
  expect(badge.className).toContain('text-red-400');

  rerender(<AnimatedBadge variant="outline">Remote</AnimatedBadge>);
  badge = screen.getByText('Remote');
  expect(badge.className).toContain('border-gray-700');
});
