package com.talentengine.dto;

import jakarta.validation.constraints.NotBlank;
import java.util.List;

public class JobRequest {
    @NotBlank(message = "Job Title is required")
    private String title;
    private List<String> requiredSkills;

    // Getters and Setters
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public List<String> getRequiredSkills() { return requiredSkills; }
    public void setRequiredSkills(List<String> requiredSkills) { this.requiredSkills = requiredSkills; }
}
