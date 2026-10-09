"use client";

import React from "react";
import { AnimatedProgress, CountUp } from "@/components/reactbits";
import { MatchScore } from "../lib/api";

export function ScoreBreakdown({ score }: { score: MatchScore }) {
  const overallPercent = Math.round(score.total_score * 100);
  const semanticPercent = Math.round(score.semantic_score * 100);
  const skillPercent = Math.round(score.skill_score * 100);
  const expPercent = Math.round(score.experience_score * 100);
  const eduPercent = Math.round(score.education_score * 100);

  return (
    <div className="space-y-4">
      <div>
        <div className="flex justify-between text-sm mb-1">
          <span className="text-gray-300">Overall Match</span>
          <span className="font-semibold text-blue-400">
            <CountUp to={overallPercent} suffix="%" />
          </span>
        </div>
        <AnimatedProgress
          value={overallPercent}
          indicatorClassName="bg-blue-500 shadow-[0_0_12px_rgba(59,130,246,0.5)]"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-400">Semantic</span>
            <span className="text-gray-300">
              <CountUp to={semanticPercent} suffix="%" />
            </span>
          </div>
          <AnimatedProgress
            value={semanticPercent}
            indicatorClassName="bg-purple-500 shadow-[0_0_10px_rgba(168,85,247,0.4)]"
          />
        </div>
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-400">Skills</span>
            <span className="text-gray-300">
              <CountUp to={skillPercent} suffix="%" />
            </span>
          </div>
          <AnimatedProgress
            value={skillPercent}
            indicatorClassName="bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.4)]"
          />
        </div>
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-400">Experience</span>
            <span className="text-gray-300">
              <CountUp to={expPercent} suffix="%" />
            </span>
          </div>
          <AnimatedProgress
            value={expPercent}
            indicatorClassName="bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.4)]"
          />
        </div>
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-400">Education</span>
            <span className="text-gray-300">
              <CountUp to={eduPercent} suffix="%" />
            </span>
          </div>
          <AnimatedProgress
            value={eduPercent}
            indicatorClassName="bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.4)]"
          />
        </div>
      </div>
    </div>
  );
}
