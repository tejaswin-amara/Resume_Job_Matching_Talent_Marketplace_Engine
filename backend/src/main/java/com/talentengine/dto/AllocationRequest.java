package com.talentengine.dto;

import jakarta.validation.constraints.NotEmpty;
import java.util.List;

public class AllocationRequest {
    @NotEmpty(message = "Candidates list cannot be empty")
    private List<String> candidates;

    @NotEmpty(message = "Jobs list cannot be empty")
    private List<String> jobs;

    // Getters and Setters
    public List<String> getCandidates() { return candidates; }
    public void setCandidates(List<String> candidates) { this.candidates = candidates; }
    public List<String> getJobs() { return jobs; }
    public void setJobs(List<String> jobs) { this.jobs = jobs; }
}
