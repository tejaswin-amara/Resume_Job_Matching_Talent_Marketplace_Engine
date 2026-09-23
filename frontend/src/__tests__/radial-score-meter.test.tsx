import {
  RadialScoreMeter,
  calculateCircumference,
  calculateStrokeDashoffset,
  getScoreCategory,
  getScoreColor,
} from '@/components/feedback/radial-score-meter';
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

describe('RadialScoreMeter Component & Mathematical Calibration', () => {
  it('correctly calculates circle circumference and strokeDashoffset', () => {
    const radius = 54;
    const circumference = 2 * Math.PI * radius; // ~339.292
    expect(calculateCircumference(radius)).toBeCloseTo(circumference, 3);

    // 0% score -> offset = circumference
    expect(calculateStrokeDashoffset(0, radius)).toBeCloseTo(circumference, 3);

    // 100% score -> offset = 0
    expect(calculateStrokeDashoffset(100, radius)).toBeCloseTo(0, 3);

    // 50% score -> offset = half circumference
    expect(calculateStrokeDashoffset(50, radius)).toBeCloseTo(circumference / 2, 3);
  });

  describe('Color Boundaries and Categories across 45%, 72%, and 94%', () => {
    it('evaluates 45% as Rose boundary (<60%) with Low Fit category', () => {
      const score = 45;
      const expectedColor = '#f43f5e';
      const expectedCategory = 'Low Fit';

      expect(getScoreColor(score)).toBe(expectedColor);
      expect(getScoreCategory(score)).toBe(expectedCategory);

      render(<RadialScoreMeter score={score} />);

      const meter = screen.getByTestId('radial-score-meter');
      expect(meter).toHaveAttribute('data-color', expectedColor);
      expect(meter).toHaveAttribute('data-score', '45');

      expect(screen.getByTestId('radial-score-value')).toHaveTextContent('45%');
      expect(screen.getByTestId('radial-score-label')).toHaveTextContent(expectedCategory);

      const radius = (160 - 12) / 2; // 74
      const expectedOffset = calculateStrokeDashoffset(45, radius);
      const circle = screen.getByTestId('radial-score-circle');
      expect(Number.parseFloat(circle.getAttribute('data-target-offset') || '0')).toBeCloseTo(
        expectedOffset,
        1,
      );
    });

    it('evaluates 72% as Amber boundary (60-79%) with Moderate Match category', () => {
      const score = 72;
      const expectedColor = '#f59e0b';
      const expectedCategory = 'Moderate Match';

      expect(getScoreColor(score)).toBe(expectedColor);
      expect(getScoreCategory(score)).toBe(expectedCategory);

      render(<RadialScoreMeter score={score} />);

      const meter = screen.getByTestId('radial-score-meter');
      expect(meter).toHaveAttribute('data-color', expectedColor);
      expect(meter).toHaveAttribute('data-score', '72');

      expect(screen.getByTestId('radial-score-value')).toHaveTextContent('72%');
      expect(screen.getByTestId('radial-score-label')).toHaveTextContent(expectedCategory);

      const radius = (160 - 12) / 2;
      const expectedOffset = calculateStrokeDashoffset(72, radius);
      const circle = screen.getByTestId('radial-score-circle');
      expect(Number.parseFloat(circle.getAttribute('data-target-offset') || '0')).toBeCloseTo(
        expectedOffset,
        1,
      );
    });

    it('evaluates 94% as Emerald boundary (>=80%) with Exceptional Match category', () => {
      const score = 94;
      const expectedColor = '#10b981';
      const expectedCategory = 'Exceptional Match';

      expect(getScoreColor(score)).toBe(expectedColor);
      expect(getScoreCategory(score)).toBe(expectedCategory);

      render(<RadialScoreMeter score={score} />);

      const meter = screen.getByTestId('radial-score-meter');
      expect(meter).toHaveAttribute('data-color', expectedColor);
      expect(meter).toHaveAttribute('data-score', '94');

      expect(screen.getByTestId('radial-score-value')).toHaveTextContent('94%');
      expect(screen.getByTestId('radial-score-label')).toHaveTextContent(expectedCategory);

      const radius = (160 - 12) / 2;
      const expectedOffset = calculateStrokeDashoffset(94, radius);
      const circle = screen.getByTestId('radial-score-circle');
      expect(Number.parseFloat(circle.getAttribute('data-target-offset') || '0')).toBeCloseTo(
        expectedOffset,
        1,
      );
    });
  });
});
