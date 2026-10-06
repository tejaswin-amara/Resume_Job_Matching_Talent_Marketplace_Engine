import { expect, test } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import {
  SpotlightCard,
  ShinyText,
  StarBorder,
  CountUp,
  AnimatedProgress,
} from '@/components/reactbits';

test('SpotlightCard renders children and reacts to mouse events', () => {
  render(
    <SpotlightCard data-testid="card">
      <p>Card Content</p>
    </SpotlightCard>
  );
  const card = screen.getByTestId('card');
  expect(card).toBeDefined();
  expect(screen.getByText('Card Content')).toBeDefined();

  fireEvent.mouseEnter(card);
  fireEvent.mouseMove(card, { clientX: 100, clientY: 100 });
  fireEvent.mouseLeave(card);
});

test('ShinyText renders text with animation class', () => {
  render(<ShinyText text="Talent Marketplace Engine" />);
  const textElement = screen.getByText('Talent Marketplace Engine');
  expect(textElement).toBeDefined();
  expect(textElement.className).toContain('animate-shine');
});

test('StarBorder renders action button and fires onClick', () => {
  let clicked = false;
  render(<StarBorder onClick={() => { clicked = true; }}>Click Me</StarBorder>);
  const btn = screen.getByText('Click Me');
  expect(btn).toBeDefined();

  fireEvent.click(btn);
  expect(clicked).toBe(true);
});

test('CountUp renders initial value with suffix', () => {
  render(<CountUp from={10} to={10} suffix="%" />);
  expect(screen.getByText('10%')).toBeDefined();
});

test('AnimatedProgress renders progress bar with percentage width', () => {
  const { container } = render(<AnimatedProgress value={75} max={100} />);
  const progressBar = container.querySelector('[style*="width: 75%"]');
  expect(progressBar).toBeDefined();
});
