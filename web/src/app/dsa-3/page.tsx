'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  SpotlightCard,
  ShinyText,
  Squares,
  FadeContent,
  AnimatedBadge,
  StarBorder,
  CountUp,
  AnimatedProgress,
} from '@/components/reactbits';
import {
  Layers,
  Cpu,
  Search,
  Binary,
  GitBranch,
  Network,
  Clock,
  Sparkles,
  ExternalLink,
  BookOpen,
  CheckCircle2,
  FileCode,
  ShieldAlert,
  ArrowLeft,
} from 'lucide-react';

interface Concept {
  id: string;
  module: 'M1' | 'M2' | 'M3' | 'M4' | 'M5' | 'M6';
  moduleTitle: string;
  co: string;
  btl: string;
  name: string;
  file: string;
  classFunc: string;
  timeComplexity: string;
  spaceComplexity: string;
  desc: string;
  application: string;
}

const CONCEPTS: Concept[] = [
  // M1
  {
    id: 'm1-zero-lib',
    module: 'M1',
    moduleTitle: 'Systems & Data Structures',
    co: 'CO1',
    btl: 'BTL5',
    name: 'Zero-Library Algorithmic Core',
    file: 'docs/architecture/adr/0001-zero-library-core.md',
    classFunc: 'ADR 0001: Zero-Library Core',
    timeComplexity: 'O(1) Policy Constraint',
    spaceComplexity: 'O(1) Memory Overhead',
    desc: 'Prohibition of external algorithmic packages (no networkx, scipy, or java.util.*). Hand-building all underlying structures.',
    application: 'Eliminates black-box vulnerabilities and enforces pure algorithmic control for low-latency scoring.',
  },
  {
    id: 'm1-4ary-heap',
    module: 'M1',
    moduleTitle: 'Systems & Data Structures',
    co: 'CO1',
    btl: 'BTL5',
    name: '4-ary Quaternary Priority Queue',
    file: 'core/engine/structures/priority_queue.py',
    classFunc: 'CustomPriorityQueue[T]',
    timeComplexity: 'O(log₄ n) Push/Pop',
    spaceComplexity: 'O(n) Memory',
    desc: 'Cache-conscious 4-way branching tree min/max heap supporting decrease-key and stable FIFO tie-breaker ordering.',
    application: 'Accelerates Dijkstra shortest-path searches inside Min-Cost Max-Flow (MCMF) allocation routines.',
  },
  {
    id: 'm1-hash-map',
    module: 'M1',
    moduleTitle: 'Systems & Data Structures',
    co: 'CO1',
    btl: 'BTL5',
    name: 'Custom Resizable Hash Map',
    file: 'core/engine/structures/hash_map.py',
    classFunc: 'CustomHashMap[K, V]',
    timeComplexity: 'O(1) Amortized',
    spaceComplexity: 'O(n) Memory',
    desc: 'Separate-chaining hash table with Horner polynomial rolling hash, dynamic table doubling, and 0.75 load factor rebalancing.',
    application: 'Zero-library dictionary indexing candidate IDs to flow network graph nodes and skill maps.',
  },
  {
    id: 'm1-adj-graph',
    module: 'M1',
    moduleTitle: 'Systems & Data Structures',
    co: 'CO1',
    btl: 'BTL5',
    name: 'Custom Residual Adjacency Graph',
    file: 'core/engine/structures/adjacency_graph.py',
    classFunc: 'CustomAdjacencyGraph',
    timeComplexity: 'O(V + E) Traversal',
    spaceComplexity: 'O(V + E) Memory',
    desc: 'Compact directed graph representation with Edge structures tracking capacity, flow, residual capacity, and reverse pointers.',
    application: 'Backbone data structure for Edmonds-Karp BFS, Dinic level graphs, and Min-Cost Max-Flow bipartite allocation.',
  },

  // M2
  {
    id: 'm2-kmp',
    module: 'M2',
    moduleTitle: 'String Algorithms',
    co: 'CO2',
    btl: 'BTL3',
    name: 'Knuth-Morris-Pratt (KMP) Matcher',
    file: 'core/engine/string/kmp.py',
    classFunc: 'KMPMatcher.find_all',
    timeComplexity: 'O(N + M) Time',
    spaceComplexity: 'O(M) Space',
    desc: 'Deterministic linear-time pattern search that precomputes a failure table (pi array) of longest proper prefix matching suffix.',
    application: 'Sub-millisecond exact keyword matching across unstructured resume text and Wikipedia corpus articles.',
  },
  {
    id: 'm2-z-algo',
    module: 'M2',
    moduleTitle: 'String Algorithms',
    co: 'CO2',
    btl: 'BTL3',
    name: 'Z-Algorithm (Z-Function)',
    file: 'core/engine/string/z_algorithm.py',
    classFunc: 'ZAlgorithm.compute_z_array',
    timeComplexity: 'O(N) Time',
    spaceComplexity: 'O(N) Space',
    desc: 'Linear-time string preprocessor computing for each index i the length of the longest substring starting at i matching prefix.',
    application: 'Modern alternative to KMP prefix function; used for dual-pass substring alignment and pattern verification.',
  },
  {
    id: 'm2-rabin-karp',
    module: 'M2',
    moduleTitle: 'String Algorithms',
    co: 'CO2',
    btl: 'BTL3',
    name: 'Rabin-Karp Rolling Hash',
    file: 'core/engine/string/rabin_karp.py',
    classFunc: 'RabinKarpMatcher.find_all',
    timeComplexity: 'O(N + M) Average',
    spaceComplexity: 'O(1) Auxiliary',
    desc: 'Multi-window rolling hash utilizing 64-bit prime modulus and double-hashing to suppress false-positive hash collisions.',
    application: 'Rapid candidate skill scanning across multiple search windows and batch document token streams.',
  },
  {
    id: 'm2-aho-corasick',
    module: 'M2',
    moduleTitle: 'String Algorithms',
    co: 'CO2',
    btl: 'BTL3',
    name: 'Aho-Corasick Multi-Pattern Automaton',
    file: 'core/engine/string/aho_corasick.py',
    classFunc: 'AhoCorasickAutomaton.search',
    timeComplexity: 'O(N + K) Search',
    spaceComplexity: 'O(Σ × M) Automaton',
    desc: 'Trie with BFS-built failure transitions and output suffix dictionary links enabling simultaneous matching of thousands of keywords.',
    application: 'Scans entire technical taxonomy (5,000+ skills, frameworks, and job titles) against raw resume text in O(text length).',
  },
  {
    id: 'm2-suffix-array',
    module: 'M2',
    moduleTitle: 'String Algorithms',
    co: 'CO2',
    btl: 'BTL3',
    name: 'Suffix Array & Kasai LCP Array',
    file: 'core/engine/string/suffix_array.py',
    classFunc: 'SuffixArray / KasaiLCP',
    timeComplexity: 'O(N log² N) SA • O(N) LCP',
    spaceComplexity: 'O(N) Space',
    desc: 'Prefix-doubling suffix array ranking combined with Kasai linear-time Longest Common Prefix (LCP) algorithm.',
    application: 'Computes document similarity via Longest Common Substring (LCS) to detect duplicate profiles and cross-article overlap.',
  },

  // M3
  {
    id: 'm3-wagner-fischer',
    module: 'M3',
    moduleTitle: 'Advanced Dynamic Programming',
    co: 'CO3',
    btl: 'BTL3',
    name: 'Wagner-Fischer Levenshtein Distance',
    file: 'core/engine/dp/wagner_fischer.py',
    classFunc: 'WagnerFischer.levenshtein_distance',
    timeComplexity: 'O(N × M) Time',
    spaceComplexity: 'O(min(N, M)) Space',
    desc: '2D dynamic programming grid for minimum edit distance (insertions, deletions, substitutions) with space optimization.',
    application: 'Fuzzy skill matching tolerating candidate typos and OCR scan errors with an edit-distance threshold of ≤ 2.',
  },
  {
    id: 'm3-seq-align',
    module: 'M3',
    moduleTitle: 'Advanced Dynamic Programming',
    co: 'CO3',
    btl: 'BTL3',
    name: 'Smith-Waterman Local Sequence Alignment',
    file: 'core/engine/dp/sequence_alignment.py',
    classFunc: 'SequenceAlignment.smith_waterman',
    timeComplexity: 'O(N × M) Time',
    spaceComplexity: 'O(N × M) Space',
    desc: 'Dynamic programming sequence alignment incorporating affine gap penalties and backtrack matrix reconstruction.',
    application: 'Local subsequence alignment for DNA genomic data in TextHack and credential phrase alignment in profiles.',
  },
  {
    id: 'm3-bitmask-tsp',
    module: 'M3',
    moduleTitle: 'Advanced Dynamic Programming',
    co: 'CO3',
    btl: 'BTL3',
    name: 'Bitmask DP (Held-Karp TSP)',
    file: 'core/engine/dp/bitmask_tsp.py',
    classFunc: 'BitmaskTSP.find_optimal_tour',
    timeComplexity: 'O(2ⁿ · n²) Time',
    spaceComplexity: 'O(2ⁿ · n) Space',
    desc: 'Exact Travelling Salesperson tour optimization using bitmask subset states dp[mask][u] and path reconstruction.',
    application: 'Finds the exact minimal travel distance for recruiter multi-city campus hiring tours (up to 20 cities).',
  },
  {
    id: 'm3-tree-rerooting',
    module: 'M3',
    moduleTitle: 'Advanced Dynamic Programming',
    co: 'CO3',
    btl: 'BTL3',
    name: 'Tree DP with Rerooting Technique',
    file: 'core/engine/dp/tree_rerooting.py',
    classFunc: 'TreeRerooting.find_centroid',
    timeComplexity: 'O(V) Time',
    spaceComplexity: 'O(V) Space',
    desc: 'Two-pass tree dynamic programming (bottom-up subtree aggregation + top-down parent transfer) computing all-pairs metrics.',
    application: 'Computes corporate reporting tree centroids and hierarchy diameters to optimize reporting lines in organizational planning.',
  },
  {
    id: 'm3-sos-dp',
    module: 'M3',
    moduleTitle: 'Advanced Dynamic Programming',
    co: 'CO3',
    btl: 'BTL3',
    name: 'Sum Over Subsets (SOS) DP',
    file: 'core/engine/dp/sos_dp.py',
    classFunc: 'SOSDP.compute_sos',
    timeComplexity: 'O(n · 2ⁿ) Time',
    spaceComplexity: 'O(2ⁿ) Space',
    desc: 'Fast subset transform variant computing cumulative sum over all submasks F[mask] in O(n · 2ⁿ) instead of O(3ⁿ).',
    application: 'Calculates candidate skill overlap profiles and superset coverage frequencies for talent marketplace analytics.',
  },

  // M4
  {
    id: 'm4-edmonds-karp',
    module: 'M4',
    moduleTitle: 'Network Flow',
    co: 'CO4',
    btl: 'BTL3',
    name: 'Edmonds-Karp Maximum Flow',
    file: 'core/engine/flow/edmonds_karp.py',
    classFunc: 'EdmondsKarpAlgorithm.compute_max_flow',
    timeComplexity: 'O(V · E²) Time',
    spaceComplexity: 'O(V + E) Space',
    desc: 'Ford-Fulkerson method specialization finding shortest augmenting paths via BFS in residual capacity graph.',
    application: 'Baseline reference implementation for bipartite matching and citation-flow community analysis.',
  },
  {
    id: 'm4-dinic',
    module: 'M4',
    moduleTitle: 'Network Flow',
    co: 'CO4',
    btl: 'BTL3',
    name: "Dinic's Algorithm with Blocking Flows",
    file: 'core/engine/flow/dinic.py',
    classFunc: 'DinicAlgorithm.compute_max_flow',
    timeComplexity: 'O(E √V) Bipartite',
    spaceComplexity: 'O(V + E) Space',
    desc: 'Level graph construction via BFS combined with DFS blocking flow augmentation and work-pointer edge pruning.',
    application: 'High-throughput matching of candidates to job vacancies under multi-headcount quotas in the talent allocation portal.',
  },
  {
    id: 'm4-mcmf',
    module: 'M4',
    moduleTitle: 'Network Flow',
    co: 'CO4',
    btl: 'BTL3',
    name: 'Min-Cost Max-Flow (MCMF)',
    file: 'core/engine/flow/min_cost_max_flow.py',
    classFunc: 'MinCostMaxFlow.compute_min_cost_max_flow',
    timeComplexity: 'O(F · E log V) Time',
    spaceComplexity: 'O(V + E) Space',
    desc: 'Successive Shortest Path (SSP) utilizing negative-cost edge augmentation and shortest-path potential algorithms.',
    application: 'Finds global optimal talent assignment that maximizes total match score while strictly enforcing requisition headcounts.',
  },
  {
    id: 'm4-min-cut',
    module: 'M4',
    moduleTitle: 'Network Flow',
    co: 'CO4',
    btl: 'BTL3',
    name: 'Max-Flow / Min-Cut Duality',
    file: 'core/engine/flow/min_cut.py',
    classFunc: 'MinCutAlgorithm.find_min_cut',
    timeComplexity: 'O(V + E) Cut Extraction',
    spaceComplexity: 'O(V) Partition',
    desc: 'Identifies the minimum s-t cut partition (S, T) by executing BFS from source over edges with residual capacity > 0.',
    application: 'Reveals hiring bottlenecks (/api/v1/marketplace/bottlenecks) and critical skill shortages blocking candidate allocations.',
  },
  {
    id: 'm4-network-model',
    module: 'M4',
    moduleTitle: 'Network Flow',
    co: 'CO4',
    btl: 'BTL3',
    name: 'Marketplace Flow Network Model',
    file: 'core/engine/flow/marketplace_network.py',
    classFunc: 'MarketplaceFlowNetwork.build_network',
    timeComplexity: 'O(C + J + E) Construction',
    spaceComplexity: 'O(C + J + E) Graph',
    desc: 'Transforms Candidate nodes, Job nodes, and compatibility edges into a unified flow network with Source and Sink supernodes.',
    application: 'Core business logic powering the Recruiter Allocation Engine (/api/v1/marketplace/allocate).',
  },

  // M5
  {
    id: 'm5-greedy-set-cover',
    module: 'M5',
    moduleTitle: 'NP-Completeness & Approximation',
    co: 'CO5',
    btl: 'BTL4',
    name: 'Greedy Set Cover Approximation',
    file: 'core/engine/approx/greedy_set_cover.py',
    classFunc: 'GreedySetCover.find_minimum_team',
    timeComplexity: 'O(M · ∑ |S_i|) Time',
    spaceComplexity: 'O(U + M) Space',
    desc: 'Greedy approximation selecting candidate with max uncovered skills per dollar, achieving provable (1 + ln |U|) harmonic ratio.',
    application: 'Powers the Team Builder feature (/api/v1/marketplace/team-builder) to assemble minimum-cost cross-functional hiring squads.',
  },
  {
    id: 'm5-vertex-cover',
    module: 'M5',
    moduleTitle: 'NP-Completeness & Approximation',
    co: 'CO5',
    btl: 'BTL4',
    name: 'Vertex Cover 2-Approximation',
    file: 'core/engine/approx/vertex_cover.py',
    classFunc: 'VertexCoverApproximation.approximate_vertex_cover',
    timeComplexity: 'O(V + E) Linear Time',
    spaceComplexity: 'O(V) Vertex Set',
    desc: 'Maximal matching approximation selecting both endpoints of disjoint edges to guarantee |C| ≤ 2 · OPT.',
    application: 'Resolves conflicting interview schedule bookings and incompatible candidate-job requisition constraints.',
  },
  {
    id: 'm5-knapsack-fptas',
    module: 'M5',
    moduleTitle: 'NP-Completeness & Approximation',
    co: 'CO5',
    btl: 'BTL4',
    name: 'Knapsack FPTAS',
    file: 'core/engine/approx/knapsack_fptas.py',
    classFunc: 'KnapsackFPTAS.solve',
    timeComplexity: 'O(n³ / ε) Time',
    spaceComplexity: 'O(n² / ε) Space',
    desc: 'Value-scaling dynamic programming scheme guaranteeing a (1 - ε) solution for 0-1 Knapsack in polynomial time.',
    application: 'Optimizes recruiter talent selection within strict hiring budget ceilings to maximize total team capability score.',
  },

  // M6
  {
    id: 'm6-miller-rabin',
    module: 'M6',
    moduleTitle: 'Randomised & Parallel Algorithms',
    co: 'CO6',
    btl: 'BTL3',
    name: 'Miller-Rabin Primality Test',
    file: 'core/engine/randomised/miller_rabin.py',
    classFunc: 'MillerRabin.is_prime',
    timeComplexity: 'O(k log³ n) Time',
    spaceComplexity: 'O(1) Memory',
    desc: 'Monte Carlo randomized primality test using n - 1 = 2ˢ · d witness decompositions, deterministic for n < 2⁶⁴, error probability ≤ 4⁻ᵏ.',
    application: 'Generates cryptographic candidate credential verification tokens and validates prime parameters for Carter-Wegman hashing.',
  },
  {
    id: 'm6-reservoir',
    module: 'M6',
    moduleTitle: 'Randomised & Parallel Algorithms',
    co: 'CO6',
    btl: 'BTL3',
    name: 'Reservoir Sampling for Streams',
    file: 'core/engine/randomised/reservoir_sampling.py',
    classFunc: 'ReservoirSampling.sample',
    timeComplexity: 'O(N) Single-Pass',
    spaceComplexity: 'O(k) Reservoir',
    desc: 'Uniform random sampling over unbounded candidate data streams maintaining exact 1/i inclusion probability.',
    application: 'Samples representative candidates and jobs from high-velocity live applicant feeds for real-time benchmark telemetry.',
  },
  {
    id: 'm6-blelloch-scan',
    module: 'M6',
    moduleTitle: 'Randomised & Parallel Algorithms',
    co: 'CO6',
    btl: 'BTL3',
    name: 'Blelloch Parallel Prefix-Scan',
    file: 'core/engine/randomised/parallel_primitives.py',
    classFunc: 'ParallelPrimitives.blelloch_scan',
    timeComplexity: 'Work T₁ = O(N) • Span T_∞ = O(log N)',
    spaceComplexity: 'O(N) Auxiliary Tree',
    desc: 'Work-efficient parallel scan with up-sweep reduce and down-sweep scan tree phases satisfying Brent Theorem T_p ≤ T₁/p + T_∞.',
    application: 'Massive parallel prefix sum computation across candidate batch scores for rapid bucket assignment and thread load balancing.',
  },
];

export default function DSA3ConceptsPage() {
  const [selectedModule, setSelectedModule] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const filteredConcepts = CONCEPTS.filter((c) => {
    const matchesModule = selectedModule === 'ALL' || c.module === selectedModule;
    const q = searchQuery.toLowerCase().trim();
    const matchesQuery =
      !q ||
      c.name.toLowerCase().includes(q) ||
      c.desc.toLowerCase().includes(q) ||
      c.file.toLowerCase().includes(q) ||
      c.classFunc.toLowerCase().includes(q) ||
      c.application.toLowerCase().includes(q);
    return matchesModule && matchesQuery;
  });

  return (
    <main className="relative min-h-screen bg-gray-950 text-gray-100 p-4 sm:p-8 md:p-12 overflow-hidden font-sans">
      {/* Background Interactive Squares Canvas */}
      <div className="absolute inset-0 z-0 pointer-events-none opacity-40">
        <Squares direction="diagonal" speed={0.35} squareSize={48} borderColor="rgba(255, 255, 255, 0.05)" />
      </div>

      <FadeContent className="relative z-10 max-w-7xl mx-auto space-y-12">
        {/* Navigation Bar */}
        <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-gray-800">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-sm font-mono text-gray-400 hover:text-cyan-400 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Marketplace</span>
          </Link>

          <div className="flex items-center gap-3">
            <a
              href="https://github.com/tejaswin-amara/Resume_Job_Matching_Talent_Marketplace_Engine"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gray-700 bg-gray-900/60 hover:bg-gray-800 text-xs font-mono text-gray-200 transition-colors"
            >
              <ExternalLink className="w-3.5 h-3.5 text-cyan-400" />
              <span>GitHub Repo</span>
            </a>
            <a
              href="/docs/index.html"
              target="_blank"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-indigo-700/60 bg-indigo-950/60 hover:bg-indigo-900 text-xs font-mono text-indigo-300 transition-colors"
            >
              <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
              <span>Standalone GitHub Page</span>
            </a>
          </div>
        </div>

        {/* Hero Section */}
        <div className="text-center space-y-4 max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-950/80 border border-indigo-500/30 text-indigo-300 text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span>DSA-3 (25CS2103E) • Project-Based Learning (PBL) Canon • 4 Credits</span>
          </div>

          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight">
            <ShinyText text="DSA-3 Concepts & Implementation Matrix" />
          </h1>

          <p className="text-sm sm:text-base text-gray-400 leading-relaxed max-w-3xl mx-auto font-light">
            Every concept from the <strong>Data Structures & Algorithms - 3 (25CS2103E)</strong> syllabus implemented
            from scratch beneath the <strong>Talent Marketplace & Resume Matching Engine (TextHack)</strong>. Zero external
            algorithmic libraries; verified with 77+ rigorous property and unit tests.
          </p>

          {/* Metric Stats Banner */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6">
            <SpotlightCard className="p-4 text-center bg-gray-900/60 border border-gray-800" spotlightColor="rgba(99, 102, 241, 0.2)">
              <div className="text-2xl font-black font-mono text-indigo-400">
                <CountUp from={1} to={6} suffix=" / 6" />
              </div>
              <div className="text-[11px] font-semibold text-gray-400 uppercase mt-0.5">Course Outcomes</div>
              <div className="text-[10px] text-gray-500">BTL3 to BTL5</div>
            </SpotlightCard>

            <SpotlightCard className="p-4 text-center bg-gray-900/60 border border-gray-800" spotlightColor="rgba(6, 182, 212, 0.2)">
              <div className="text-2xl font-black font-mono text-cyan-400">
                <CountUp from={1} to={6} suffix=" Modules" />
              </div>
              <div className="text-[11px] font-semibold text-gray-400 uppercase mt-0.5">Curriculum Scope</div>
              <div className="text-[10px] text-gray-500">M1 through M6</div>
            </SpotlightCard>

            <SpotlightCard className="p-4 text-center bg-gray-900/60 border border-gray-800" spotlightColor="rgba(16, 185, 129, 0.2)">
              <div className="text-2xl font-black font-mono text-emerald-400">
                <CountUp from={10} to={25} suffix=" Primitives" />
              </div>
              <div className="text-[11px] font-semibold text-gray-400 uppercase mt-0.5">Zero-Library Algos</div>
              <div className="text-[10px] text-gray-500">Hand-Built Core</div>
            </SpotlightCard>

            <SpotlightCard className="p-4 text-center bg-gray-900/60 border border-gray-800" spotlightColor="rgba(245, 158, 11, 0.2)">
              <div className="text-2xl font-black font-mono text-amber-400">
                <CountUp from={50} to={77} suffix=" / 77" />
              </div>
              <div className="text-[11px] font-semibold text-gray-400 uppercase mt-0.5">Tests Passing</div>
              <div className="text-[10px] text-gray-500">100% Quality Gate</div>
            </SpotlightCard>
          </div>
        </div>

        {/* Filter & Search Bar */}
        <div className="bg-gray-900/70 border border-gray-800 rounded-2xl p-4 backdrop-blur flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="relative w-full md:w-96">
            <Search className="w-4 h-4 text-gray-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter by algorithm, file, or complexity..."
              className="w-full bg-gray-950 border border-gray-700 focus:border-indigo-500 focus:outline-none rounded-xl pl-10 pr-4 py-2 text-xs font-mono text-gray-200 placeholder-gray-500"
            />
          </div>

          <div className="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto pb-2 md:pb-0">
            {(['ALL', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6'] as const).map((mod) => (
              <button
                key={mod}
                onClick={() => setSelectedModule(mod)}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all ${
                  selectedModule === mod
                    ? 'bg-indigo-600 text-white shadow'
                    : 'bg-gray-800 hover:bg-gray-700 text-gray-400'
                }`}
              >
                {mod === 'ALL' ? 'All (25)' : mod}
              </button>
            ))}
          </div>
        </div>

        {/* Concept Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredConcepts.map((c) => (
            <SpotlightCard
              key={c.id}
              className="p-6 bg-gray-900/60 border border-gray-800 flex flex-col justify-between"
              spotlightColor="rgba(99, 102, 241, 0.18)"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-3">
                  <AnimatedBadge variant="default">
                    {c.module} • {c.co}
                  </AnimatedBadge>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-gray-800 text-gray-300 border border-gray-700">
                    {c.btl}
                  </span>
                </div>

                <h3 className="font-bold text-white text-base mb-1">{c.name}</h3>
                <div className="text-xs font-mono text-cyan-400 mb-2">{c.classFunc}</div>
                <p className="text-xs text-gray-400 leading-relaxed mb-4">{c.desc}</p>
              </div>

              <div>
                <div className="p-2.5 bg-gray-950/80 rounded-lg border border-gray-800 mb-3 space-y-1 font-mono text-[11px]">
                  <div className="flex justify-between text-gray-400">
                    <span>Complexity:</span>
                    <span className="text-emerald-400 font-semibold">{c.timeComplexity}</span>
                  </div>
                  <div className="flex justify-between text-gray-400">
                    <span>Space:</span>
                    <span className="text-amber-400">{c.spaceComplexity}</span>
                  </div>
                </div>

                <div className="text-[11px] text-gray-400 mb-4">
                  <strong className="text-gray-300">Production Role:</strong> {c.application}
                </div>

                <div className="pt-3 border-t border-gray-800 flex items-center justify-between font-mono text-[11px]">
                  <span className="text-gray-500 truncate max-w-[170px]" title={c.file}>
                    <FileCode className="w-3.5 h-3.5 inline mr-1 text-gray-400" />
                    {c.file}
                  </span>
                  <a
                    href={`https://github.com/tejaswin-amara/Resume_Job_Matching_Talent_Marketplace_Engine/blob/main/${c.file}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-cyan-400 hover:text-cyan-300 font-semibold transition-colors"
                  >
                    <span>View Code</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            </SpotlightCard>
          ))}
        </div>

        {/* Course Outcomes Matrix Section */}
        <div className="pt-8 border-t border-gray-800 space-y-6">
          <div className="text-center max-w-2xl mx-auto">
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">Course Outcomes &amp; Bloom&apos;s Taxonomy</h2>
            <p className="text-xs text-gray-400 mt-1">
              Mapped according to the 25CS2103E Course Handout Specification.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-gray-900/40 border border-gray-800">
              <div className="flex items-center justify-between text-xs font-mono mb-2">
                <span className="text-indigo-400 font-bold">CO1</span>
                <span className="text-rose-400">BTL5 — Evaluate</span>
              </div>
              <h4 className="text-sm font-semibold text-gray-200 mb-1">Evaluate Problem Signatures</h4>
              <p className="text-xs text-gray-400">
                Pattern search, sequence alignment, network flows, and NP-hard scheduling strategy selection.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-gray-900/40 border border-gray-800">
              <div className="flex items-center justify-between text-xs font-mono mb-2">
                <span className="text-cyan-400 font-bold">CO2</span>
                <span className="text-blue-400">BTL3 — Apply</span>
              </div>
              <h4 className="text-sm font-semibold text-gray-200 mb-1">Linear String Algorithms</h4>
              <p className="text-xs text-gray-400">
                KMP, Z-function, Rabin-Karp rolling hash, Aho-Corasick automaton, Suffix Arrays and Kasai LCP.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-gray-900/40 border border-gray-800">
              <div className="flex items-center justify-between text-xs font-mono mb-2">
                <span className="text-emerald-400 font-bold">CO3</span>
                <span className="text-blue-400">BTL3 — Apply</span>
              </div>
              <h4 className="text-sm font-semibold text-gray-200 mb-1">Advanced Dynamic Programming</h4>
              <p className="text-xs text-gray-400">
                Wagner-Fischer edit distance, Smith-Waterman alignment, Bitmask TSP, Tree rerooting, and SOS DP.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-gray-900/40 border border-gray-800">
              <div className="flex items-center justify-between text-xs font-mono mb-2">
                <span className="text-amber-400 font-bold">CO4</span>
                <span className="text-blue-400">BTL3 — Apply</span>
              </div>
              <h4 className="text-sm font-semibold text-gray-200 mb-1">Network Flow & Duality</h4>
              <p className="text-xs text-gray-400">
                Edmonds-Karp BFS, Dinic blocking flows, Min-Cost Max-Flow, and Min-Cut bottleneck duality.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-gray-900/40 border border-gray-800">
              <div className="flex items-center justify-between text-xs font-mono mb-2">
                <span className="text-rose-400 font-bold">CO5</span>
                <span className="text-amber-400">BTL4 — Analyze</span>
              </div>
              <h4 className="text-sm font-semibold text-gray-200 mb-1">NP-Completeness & Approx</h4>
              <p className="text-xs text-gray-400">
                Cook-Levin reductions, Greedy Set Cover (1+ln n) ratio, Vertex Cover 2-approx, and Knapsack FPTAS.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-gray-900/40 border border-gray-800">
              <div className="flex items-center justify-between text-xs font-mono mb-2">
                <span className="text-violet-400 font-bold">CO6</span>
                <span className="text-blue-400">BTL3 — Apply</span>
              </div>
              <h4 className="text-sm font-semibold text-gray-200 mb-1">Randomised & Parallel Primitives</h4>
              <p className="text-xs text-gray-400">
                Miller-Rabin primality, Reservoir streaming sampling, and Blelloch work-efficient parallel scan.
              </p>
            </div>
          </div>
        </div>

        {/* Bottom CTA */}
        <div className="pt-6 text-center">
          <Link href="/candidates">
            <StarBorder>Launch Candidate Portal</StarBorder>
          </Link>
        </div>
      </FadeContent>
    </main>
  );
}
