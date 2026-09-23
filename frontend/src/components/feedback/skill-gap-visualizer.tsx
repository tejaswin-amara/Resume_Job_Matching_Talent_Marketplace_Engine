'use client';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import type { SkillAssessment } from '@/contracts/match-engine.schema';
import { AlertCircle, CheckCircle2, ShieldAlert } from 'lucide-react';
import * as React from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

export interface SkillGapVisualizerProps {
  skillAssessments: SkillAssessment[];
  sharedSkills: string[];
  missingCoreSkills: string[];
}

export function SkillGapVisualizer({
  skillAssessments,
  sharedSkills,
  missingCoreSkills,
}: SkillGapVisualizerProps) {
  const radarData = React.useMemo(() => {
    return skillAssessments.map((item) => ({
      skill: item.skill,
      candidateProficiency: item.candidateProficiency,
      targetExpectation: Math.round(item.importanceWeight * 100),
      fullMark: 100,
    }));
  }, [skillAssessments]);

  return (
    <Card className="border-slate-800 bg-slate-900/60" data-testid="skill-gap-visualizer">
      <CardHeader className="pb-3">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div>
            <CardTitle className="text-base font-semibold text-white">
              Skill Taxonomy & Proficiency Calibration
            </CardTitle>
            <p className="text-xs text-slate-400 mt-1">
              Multi-dimensional comparison between role requirements and candidate evidence
            </p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Dual Badge System */}
        <div className="space-y-4">
          <div>
            <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400 mb-2">
              <CheckCircle2 className="h-3.5 w-3.5" />
              <span>Demonstrated & Matched Competencies ({sharedSkills.length})</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {sharedSkills.length > 0 ? (
                sharedSkills.map((skill) => (
                  <Badge
                    key={skill}
                    variant="success"
                    className="flex items-center gap-1 py-1 px-2.5 text-xs font-medium"
                    data-testid="matched-skill-badge"
                  >
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                    {skill}
                  </Badge>
                ))
              ) : (
                <span className="text-xs text-slate-500 italic">
                  No direct skill matches detected
                </span>
              )}
            </div>
          </div>

          <div>
            <div className="flex items-center gap-1.5 text-xs font-semibold text-rose-400 mb-2">
              <AlertCircle className="h-3.5 w-3.5" />
              <span>Critical Omissions & Skill Gaps ({missingCoreSkills.length})</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {missingCoreSkills.length > 0 ? (
                missingCoreSkills.map((skill) => (
                  <Badge
                    key={skill}
                    variant="destructive"
                    className="flex items-center gap-1 py-1 px-2.5 text-xs font-medium"
                    data-testid="missing-skill-badge"
                  >
                    <ShieldAlert className="h-3 w-3 text-rose-400" />
                    {skill}
                  </Badge>
                ))
              ) : (
                <span className="text-xs text-emerald-400 italic font-medium">
                  Zero critical skill deficits detected!
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Visual Charts: Radar & Bar Views */}
        <Tabs defaultValue="radar" className="w-full">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
              Diagnostic Visualization
            </span>
            <TabsList className="h-8">
              <TabsTrigger value="radar" className="text-xs px-2.5 py-1">
                Radar View
              </TabsTrigger>
              <TabsTrigger value="bar" className="text-xs px-2.5 py-1">
                Bar Comparison
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="radar" className="pt-2">
            <div className="h-[280px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
                  <PolarGrid stroke="#334155" strokeDasharray="3 3" />
                  <PolarAngleAxis dataKey="skill" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <PolarRadiusAxis
                    angle={30}
                    domain={[0, 100]}
                    stroke="#475569"
                    tick={{ fill: '#64748b', fontSize: 9 }}
                  />
                  <Radar
                    name="Candidate Proficiency"
                    dataKey="candidateProficiency"
                    stroke="#3b82f6"
                    fill="#3b82f6"
                    fillOpacity={0.45}
                  />
                  <Radar
                    name="Target Expectation"
                    dataKey="targetExpectation"
                    stroke="#10b981"
                    fill="#10b981"
                    fillOpacity={0.2}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      borderColor: '#334155',
                      borderRadius: '8px',
                      color: '#f8fafc',
                      fontSize: '12px',
                    }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </TabsContent>

          <TabsContent value="bar" className="pt-2">
            <div className="h-[280px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={radarData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis
                    dataKey="skill"
                    stroke="#64748b"
                    tick={{ fill: '#94a3b8', fontSize: 10 }}
                    interval={0}
                    angle={-15}
                    textAnchor="end"
                  />
                  <YAxis
                    domain={[0, 100]}
                    stroke="#64748b"
                    tick={{ fill: '#64748b', fontSize: 10 }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      borderColor: '#334155',
                      borderRadius: '8px',
                      color: '#f8fafc',
                      fontSize: '12px',
                    }}
                  />
                  <Bar
                    dataKey="candidateProficiency"
                    name="Candidate Proficiency"
                    fill="#3b82f6"
                    radius={[4, 4, 0, 0]}
                  />
                  <Bar
                    dataKey="targetExpectation"
                    name="Required Weight"
                    fill="#10b981"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
