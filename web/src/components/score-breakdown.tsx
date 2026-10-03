"use client";
import React from "react";
import { ProgressBar } from "./ui/progress-bar";
import { MatchScore } from "../lib/api";

export function ScoreBreakdown({ score }: { score: MatchScore }) {
  return (
    <div className="space-y-4">
      <div>
        <div className="flex justify-between text-sm mb-1">
          <span className="text-gray-300">Overall Match</span>
          <span className="font-semibold text-blue-400">{(score.overallScore * 100).toFixed(0)}%</span>
        </div>
        <ProgressBar value={score.overallScore * 100} indicatorClassName="bg-blue-500" />
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-400">Semantic</span>
            <span className="text-gray-300">{(score.semanticScore * 100).toFixed(0)}%</span>
          </div>
          <ProgressBar value={score.semanticScore * 100} indicatorClassName="bg-purple-500" />
        </div>
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-400">Skills</span>
            <span className="text-gray-300">{(score.skillScore * 100).toFixed(0)}%</span>
          </div>
          <ProgressBar value={score.skillScore * 100} indicatorClassName="bg-green-500" />
        </div>
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-400">Experience</span>
            <span className="text-gray-300">{(score.experienceScore * 100).toFixed(0)}%</span>
          </div>
          <ProgressBar value={score.experienceScore * 100} indicatorClassName="bg-amber-500" />
        </div>
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-400">Education</span>
            <span className="text-gray-300">{(score.educationScore * 100).toFixed(0)}%</span>
          </div>
          <ProgressBar value={score.educationScore * 100} indicatorClassName="bg-cyan-500" />
        </div>
      </div>
    </div>
  );
}
