"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  SpotlightCard,
  AnimatedBadge,
  StarBorder,
  CountUp,
  ShinyText,
  Squares,
} from "@/components/reactbits";
import { api } from "@/lib/api";
import { Loader2, ArrowLeft, Network, GitBranch, Users } from "lucide-react";

export default function MarketAllocation() {
  const [loading, setLoading] = useState(false);
  const [allocation, setAllocation] = useState<any>(null);
  const [bottlenecks, setBottlenecks] = useState<any>(null);

  const runAllocation = async () => {
    setLoading(true);
    try {
      const res = await api.allocateMarketplace();
      setAllocation(res);
    } catch (e) {
      console.error(e);
      alert("Failed to run allocation");
    } finally {
      setLoading(false);
    }
  };

  const runBottlenecks = async () => {
    setLoading(true);
    try {
      const res = await api.getBottlenecks();
      setBottlenecks(res);
    } catch (e) {
      console.error(e);
      alert("Failed to analyze bottlenecks");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-gray-950 p-8 overflow-hidden">
      <div className="absolute inset-0 z-0 pointer-events-none opacity-30">
        <Squares direction="diagonal" speed={0.3} squareSize={48} borderColor="rgba(255, 255, 255, 0.05)" />
      </div>

      <div className="relative z-10 max-w-5xl mx-auto space-y-8">
        <div className="flex items-center gap-4">
          <Link href="/recruiter">
            <StarBorder className="text-xs py-1 px-3">
              <span className="flex items-center gap-1">
                <ArrowLeft className="w-3.5 h-3.5" /> Back
              </span>
            </StarBorder>
          </Link>
          <h1 className="text-3xl font-bold text-gray-100">
            <ShinyText text="Marketplace Allocation" />
          </h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <SpotlightCard
            spotlightColor="rgba(59, 130, 246, 0.25)"
            className="p-6 bg-blue-950/20 border-blue-900/60"
          >
            <Network className="w-8 h-8 text-blue-500 mb-2" />
            <h3 className="text-lg font-bold text-blue-400 mb-2">Dinic's Flow Allocation</h3>
            <p className="text-sm text-gray-400 mb-4">
              Optimizes maximum candidate-to-job assignments across the entire marketplace.
            </p>
            <StarBorder
              onClick={runAllocation}
              disabled={loading}
              color="#3b82f6"
              className="w-full text-xs"
            >
              <span className="flex items-center justify-center gap-2">
                {loading ? <Loader2 className="animate-spin w-4 h-4" /> : null}
                Run Allocation
              </span>
            </StarBorder>
          </SpotlightCard>

          <SpotlightCard
            spotlightColor="rgba(239, 68, 68, 0.25)"
            className="p-6 bg-red-950/20 border-red-900/60"
          >
            <GitBranch className="w-8 h-8 text-red-500 mb-2" />
            <h3 className="text-lg font-bold text-red-400 mb-2">Min-Cut Bottlenecks</h3>
            <p className="text-sm text-gray-400 mb-4">
              Identifies market inefficiencies where talent supply fails to meet demand.
            </p>
            <StarBorder
              onClick={runBottlenecks}
              disabled={loading}
              color="#ef4444"
              className="w-full text-xs"
            >
              <span className="text-red-400">Analyze Bottlenecks</span>
            </StarBorder>
          </SpotlightCard>

          <SpotlightCard
            spotlightColor="rgba(16, 185, 129, 0.25)"
            className="p-6 bg-emerald-950/20 border-emerald-900/60"
          >
            <Users className="w-8 h-8 text-emerald-500 mb-2" />
            <h3 className="text-lg font-bold text-emerald-400 mb-2">Team Builder</h3>
            <p className="text-sm text-gray-400 mb-4">
              Forms optimal cross-functional teams covering required skill sets.
            </p>
            <StarBorder disabled color="#10b981" className="w-full text-xs">
              <span className="text-emerald-400">Coming Soon</span>
            </StarBorder>
          </SpotlightCard>
        </div>

        {allocation && (
          <SpotlightCard className="p-6">
            <h2 className="text-xl font-bold text-gray-100 mb-4">Allocation Results</h2>
            <div className="flex justify-between items-center mb-6 p-4 bg-gray-900 rounded-lg border border-gray-800">
              <div className="text-center w-full">
                <div className="text-3xl font-bold text-blue-500">
                  <CountUp to={allocation.total_allocated || 0} />
                </div>
                <div className="text-sm text-gray-400">Total Matches</div>
              </div>
            </div>
            <div className="space-y-2">
              <h3 className="font-medium text-gray-300">Assignments</h3>
              <div className="grid grid-cols-1 gap-2">
                {allocation.assignments &&
                  allocation.assignments.map((a: any, i: number) => (
                    <div
                      key={i}
                      className="flex justify-between p-3 bg-gray-900 border border-gray-800 rounded text-sm"
                    >
                      <span className="text-gray-300">
                        Candidate: {a.candidate_id.substring(0, 8)}
                      </span>
                      <span className="text-gray-500">→</span>
                      <span className="text-blue-400">
                        Job: {a.job_id.substring(0, 8)}
                      </span>
                    </div>
                  ))}
                {(!allocation.assignments || allocation.assignments.length === 0) && (
                  <div className="text-gray-500 italic p-4 text-center">
                    No assignments possible
                  </div>
                )}
              </div>
            </div>
          </SpotlightCard>
        )}

        {bottlenecks && (
          <SpotlightCard className="p-6">
            <h2 className="text-xl font-bold text-red-400 mb-4">
              Market Bottlenecks Detected
            </h2>
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-semibold text-gray-400 mb-2">
                  Unfilled Demand (Jobs)
                </h4>
                <div className="flex flex-wrap gap-2">
                  {bottlenecks.unfilled_demand &&
                    bottlenecks.unfilled_demand.map((job: string, i: number) => (
                      <AnimatedBadge key={i} variant="danger">
                        Job: {job.substring(0, 8)}
                      </AnimatedBadge>
                    ))}
                  {(!bottlenecks.unfilled_demand ||
                    bottlenecks.unfilled_demand.length === 0) && (
                    <span className="text-gray-500 text-sm">None</span>
                  )}
                </div>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-gray-400 mb-2">
                  Unutilized Supply (Candidates)
                </h4>
                <div className="flex flex-wrap gap-2">
                  {bottlenecks.unutilized_supply &&
                    bottlenecks.unutilized_supply.map((cand: string, i: number) => (
                      <AnimatedBadge key={i} variant="outline">
                        Cand: {cand.substring(0, 8)}
                      </AnimatedBadge>
                    ))}
                  {(!bottlenecks.unutilized_supply ||
                    bottlenecks.unutilized_supply.length === 0) && (
                    <span className="text-gray-500 text-sm">None</span>
                  )}
                </div>
              </div>
            </div>
          </SpotlightCard>
        )}
      </div>
    </div>
  );
}
