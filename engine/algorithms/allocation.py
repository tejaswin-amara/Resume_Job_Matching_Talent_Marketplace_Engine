import networkx as nx
from typing import List, Dict, Tuple, Any, Set, Optional, Callable

def allocate_min_cost_flow(candidates: List[Dict[str, Any]], jobs: List[Dict[str, Any]], teams: List[Dict[str, Any]], fit_scores: Dict[Tuple[str, str], float]) -> List[Tuple[str, str]]:
    """
    Min-cost max-flow allocation using NetworkX to optimally assign candidates to jobs
    while satisfying team headcount constraints and maximizing fit scores.

    Args:
        candidates: List of candidate dictionaries.
        jobs: List of job dictionaries.
        teams: List of team dictionaries.
        fit_scores: Dictionary mapping (candidate_id, job_id) to fit scores.

    Returns:
        A list of tuples (candidate_id, job_id) representing the optimal assignments.
    """
    graph: nx.DiGraph = nx.DiGraph()
    source, sink = "S", "T"

    for c in candidates:
        graph.add_edge(source, c['id'], capacity=1, weight=0)

    for j in jobs:
        team_node = f"team_{j['team_id']}_{j.get('role_category', 'default')}"

        for c in candidates:
            # We assume candidates are pre-filtered by hard constraints for this job
            if (c['id'], j['id']) in fit_scores:
                # Networkx min_cost_flow minimizes weight
                cost = -int(fit_scores[(c['id'], j['id'])] * 1000)
                graph.add_edge(c['id'], j['id'], capacity=1, weight=cost)

        graph.add_edge(j['id'], team_node, capacity=j.get('headcount', 1), weight=0)

    team_nodes = set(f"team_{j['team_id']}_{j.get('role_category', 'default')}" for j in jobs)
    for team_node in team_nodes:
        # Assuming team subcap is the sum of headcounts for its jobs for now
        subcap = sum(j.get('headcount', 1) for j in jobs if f"team_{j['team_id']}_{j.get('role_category', 'default')}" == team_node)
        graph.add_edge(team_node, sink, capacity=subcap, weight=0)

    try:
        flow_dict = nx.max_flow_min_cost(graph, source, sink)
        assignments = []
        for c in candidates:
            c_id = c['id']
            if c_id in flow_dict:
                for target, flow in flow_dict[c_id].items():
                    if flow > 0:
                        assignments.append((c_id, target))
        return assignments
    except nx.NetworkXUnfeasible:
        return []

def min_candidates_to_cover(skills_universe: List[str], candidate_skill_masks: List[int]) -> Optional[List[int]]:
    """
    Bitmask DP minimum skill-set (exact for small k) to find the minimum number
    of candidates needed to cover all required skills in the universe.

    Args:
        skills_universe: List of skills required.
        candidate_skill_masks: List of integer bitmasks representing candidate skills.

    Returns:
        A list of candidate indices that form the minimum set cover, or None if impossible.
    """
    k = len(skills_universe)
    n = len(candidate_skill_masks)
    FULL = (1 << k) - 1
    INF = float('inf')

    dp: List[float] = [INF] * (FULL + 1)
    choice: List[Optional[Tuple[int, int]]] = [None] * (FULL + 1)
    dp[0] = 0

    for mask in range(FULL + 1):
        if dp[mask] == INF: continue
        for i in range(n):
            new_mask = mask | candidate_skill_masks[i]
            if dp[mask] + 1 < dp[new_mask]:
                dp[new_mask] = dp[mask] + 1
                choice[new_mask] = (mask, i)

    if dp[FULL] == INF:
        return None

    # Reconstruct
    curr = FULL
    chosen_candidates: List[int] = []
    while curr > 0:
        val = choice[curr]
        if val is None: break
        prev_mask, cand_idx = val
        chosen_candidates.append(cand_idx)
        curr = prev_mask

    return chosen_candidates

def greedy_set_cover(skills_universe: Set[str], candidates: List[Dict[str, Any]], cost_fn: Callable[[Dict[str, Any]], float]) -> Dict[str, Any]:
    """
    Greedy weighted set cover (approximation for large k/n) to select candidates
    minimizing cost while maximizing new skill coverage.

    Args:
        skills_universe: Set of required skills.
        candidates: List of candidate dictionaries.
        cost_fn: Callable to evaluate a candidate's cost.

    Returns:
        A dictionary with 'chosen' candidates and 'residual_uncovered' skills.
    """
    uncovered = set(skills_universe)
    chosen: List[Dict[str, Any]] = []

    while uncovered:
        best_candidate = None
        best_ratio = -float('inf')

        for c in candidates:
            if c in chosen: continue
            c_skills = set(c['skills'])
            new_coverage = len(c_skills.intersection(uncovered))
            if new_coverage == 0: continue

            ratio = new_coverage / max(cost_fn(c), 0.001)
            if ratio > best_ratio:
                best_ratio = ratio
                best_candidate = c

        if best_candidate is None:
            return {"chosen": chosen, "residual_uncovered": list(uncovered)}

        chosen.append(best_candidate)
        uncovered -= set(best_candidate['skills'])

    return {"chosen": chosen, "residual_uncovered": []}
