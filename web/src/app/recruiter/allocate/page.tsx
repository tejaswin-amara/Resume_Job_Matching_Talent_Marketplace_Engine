"use client";
import React, { useState } from "react";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
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
    <div className="min-h-screen bg-gray-950 p-8">
      <div className="max-w-5xl mx-auto space-y-8">
        <div className="flex items-center gap-4">
          <Link href="/recruiter">
            <Button variant="ghost" size="sm"><ArrowLeft className="w-4 h-4 mr-2" /> Back</Button>
          </Link>
          <h1 className="text-3xl font-bold text-gray-100">Marketplace Allocation</h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="bg-blue-900/20 border-blue-900">
            <CardHeader>
              <Network className="w-8 h-8 text-blue-500 mb-2" />
              <CardTitle className="text-blue-400">Dinic's Flow Allocation</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-400 mb-4">Optimizes maximum candidate-to-job assignments across the entire marketplace.</p>
              <Button onClick={runAllocation} disabled={loading} className="w-full">
                {loading ? <Loader2 className="animate-spin w-4 h-4 mr-2" /> : null}
                Run Allocation
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-red-900/20 border-red-900">
            <CardHeader>
              <GitBranch className="w-8 h-8 text-red-500 mb-2" />
              <CardTitle className="text-red-400">Min-Cut Bottlenecks</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-400 mb-4">Identifies market inefficiencies where talent supply fails to meet demand.</p>
              <Button onClick={runBottlenecks} disabled={loading} variant="outline" className="w-full border-red-900 text-red-400 hover:bg-red-900/50">
                Analyze Bottlenecks
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-emerald-900/20 border-emerald-900">
            <CardHeader>
              <Users className="w-8 h-8 text-emerald-500 mb-2" />
              <CardTitle className="text-emerald-400">Team Builder</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-400 mb-4">Forms optimal cross-functional teams covering required skill sets.</p>
              <Button disabled variant="outline" className="w-full border-emerald-900 text-emerald-400">
                Coming Soon
              </Button>
            </CardContent>
          </Card>
        </div>

        {allocation && (
          <Card>
            <CardHeader>
              <CardTitle>Allocation Results</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex justify-between items-center mb-6 p-4 bg-gray-900 rounded-lg">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-500">{allocation.total_allocated || 0}</div>
                  <div className="text-sm text-gray-400">Total Matches</div>
                </div>
              </div>
              <div className="space-y-2">
                <h3 className="font-medium text-gray-300">Assignments</h3>
                <div className="grid grid-cols-1 gap-2">
                  {allocation.assignments && allocation.assignments.map((a: any, i: number) => (
                    <div key={i} className="flex justify-between p-3 bg-gray-900 border border-gray-800 rounded text-sm">
                      <span className="text-gray-300">Candidate: {a.candidate_id.substring(0,8)}</span>
                      <span className="text-gray-500">→</span>
                      <span className="text-blue-400">Job: {a.job_id.substring(0,8)}</span>
                    </div>
                  ))}
                  {(!allocation.assignments || allocation.assignments.length === 0) && (
                    <div className="text-gray-500 italic p-4 text-center">No assignments possible</div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {bottlenecks && (
          <Card>
            <CardHeader>
              <CardTitle className="text-red-400">Market Bottlenecks Detected</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-semibold text-gray-400 mb-2">Unfilled Demand (Jobs)</h4>
                  <div className="flex flex-wrap gap-2">
                    {bottlenecks.unfilled_demand && bottlenecks.unfilled_demand.map((job: string, i: number) => (
                      <Badge key={i} variant="danger">Job: {job.substring(0,8)}</Badge>
                    ))}
                    {(!bottlenecks.unfilled_demand || bottlenecks.unfilled_demand.length === 0) && <span className="text-gray-500 text-sm">None</span>}
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-gray-400 mb-2">Unutilized Supply (Candidates)</h4>
                  <div className="flex flex-wrap gap-2">
                    {bottlenecks.unutilized_supply && bottlenecks.unutilized_supply.map((cand: string, i: number) => (
                      <Badge key={i} variant="outline">Cand: {cand.substring(0,8)}</Badge>
                    ))}
                    {(!bottlenecks.unutilized_supply || bottlenecks.unutilized_supply.length === 0) && <span className="text-gray-500 text-sm">None</span>}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
