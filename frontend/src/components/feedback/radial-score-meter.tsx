'use client';

import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
import * as React from 'react';

export interface RadialScoreMeterProps {
  score: number;
  size?: number;
  strokeWidth?: number;
  className?: string;
  showLabel?: boolean;
}

export function getScoreColor(score: number): string {
  if (score >= 80) {
    return '#10b981'; // Emerald
  }
  if (score >= 60) {
    return '#f59e0b'; // Amber
  }
  return '#f43f5e'; // Rose
}

export function getScoreCategory(score: number): string {
  if (score >= 80) {
    return 'Exceptional Match';
  }
  if (score >= 60) {
    return 'Moderate Match';
  }
  return 'Low Fit';
}

export function calculateCircumference(radius: number): number {
  return 2 * Math.PI * radius;
}

export function calculateStrokeDashoffset(score: number, radius = 54): number {
  const clamped = Math.min(100, Math.max(0, score));
  const circumference = calculateCircumference(radius);
  return circumference - (clamped / 100) * circumference;
}

export function RadialScoreMeter({
  score,
  size = 160,
  strokeWidth = 12,
  className,
  showLabel = true,
}: RadialScoreMeterProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = calculateCircumference(radius);
  const targetOffset = calculateStrokeDashoffset(score, radius);
  const color = getScoreColor(score);
  const category = getScoreCategory(score);
  const clampedScore = Math.round(Math.min(100, Math.max(0, score)));

  return (
    <div
      className={cn('flex flex-col items-center justify-center', className)}
      data-testid="radial-score-meter"
      data-score={clampedScore}
      data-color={color}
    >
      <div
        className="relative flex items-center justify-center"
        style={{ width: size, height: size }}
      >
        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          className="rotate-[-90deg] transform"
          aria-label={`Match score: ${clampedScore}%`}
          role="img"
        >
          {/* Background Track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#1e293b"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Dynamic Animated Meter */}
          <motion.circle
            data-testid="radial-score-circle"
            data-target-offset={targetOffset}
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={targetOffset}
            strokeLinecap="round"
            fill="transparent"
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: targetOffset }}
            transition={{ duration: 1.2, ease: 'easeOut' }}
          />
        </svg>

        {/* Center Content */}
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span
            data-testid="radial-score-value"
            className="text-3xl font-extrabold tracking-tight text-white"
          >
            {clampedScore}%
          </span>
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
            Affinity
          </span>
        </div>
      </div>

      {showLabel && (
        <div className="mt-3 flex flex-col items-center">
          <span
            data-testid="radial-score-label"
            className="text-sm font-semibold tracking-wide"
            style={{ color }}
          >
            {category}
          </span>
          <span className="text-xs text-slate-400">Semantic Engine Calibration</span>
        </div>
      )}
    </div>
  );
}
