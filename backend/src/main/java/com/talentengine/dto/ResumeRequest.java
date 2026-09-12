package com.talentengine.dto;

import jakarta.validation.constraints.NotBlank;
import java.util.List;

public class ResumeRequest {
    @NotBlank(message = "Candidate ID is required")
    private String candidateId;
    private List<String> skills;

    // Getters and Setters
    public String getCandidateId() { return candidateId; }
    public void setCandidateId(String candidateId) { this.candidateId = candidateId; }
    public List<String> getSkills() { return skills; }
    public void setSkills(List<String> skills) { this.skills = skills; }
}
