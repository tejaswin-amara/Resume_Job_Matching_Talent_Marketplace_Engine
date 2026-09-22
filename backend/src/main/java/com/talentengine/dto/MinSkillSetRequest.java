package com.talentengine.dto;

import jakarta.validation.constraints.NotEmpty;
import java.util.List;
import java.util.Map;

public class MinSkillSetRequest {

    @NotEmpty(message = "Capabilities map cannot be empty")
    private Map<String, List<String>> capabilities;

    @NotEmpty(message = "Required skills list cannot be empty")
    private List<String> requiredSkills;

    public Map<String, List<String>> getCapabilities() {
        return capabilities;
    }

    public void setCapabilities(Map<String, List<String>> capabilities) {
        this.capabilities = capabilities;
    }

    public List<String> getRequiredSkills() {
        return requiredSkills;
    }

    public void setRequiredSkills(List<String> requiredSkills) {
        this.requiredSkills = requiredSkills;
    }
}
