import networkx as nx

def allocate_min_cost_flow(candidates: list, jobs: list, teams: list, fit_scores: dict):
    """
    Min-cost max-flow allocation using NetworkX
    """
    graph = nx.DiGraph()
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

def min_candidates_to_cover(skills_universe: list, candidate_skill_masks: list):
    """
    Bitmask DP minimum skill-set (exact for small k)
    """
    k = len(skills_universe)
    n = len(candidate_skill_masks)
    FULL = (1 << k) - 1
    INF = float('inf')

    dp = [INF] * (FULL + 1)
    choice = [None] * (FULL + 1)
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
    chosen_candidates = []
    while curr > 0:
        prev_mask, cand_idx = choice[curr]
        chosen_candidates.append(cand_idx)
        curr = prev_mask

    return chosen_candidates

def greedy_set_cover(skills_universe: set, candidates: list, cost_fn):
    """
    Greedy weighted set cover (approximation for large k/n)
    """
    uncovered = set(skills_universe)
    chosen = []

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
