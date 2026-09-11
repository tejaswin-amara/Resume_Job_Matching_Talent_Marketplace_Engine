package com.talentengine.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import java.util.Map;

@RestController
@RequestMapping("/v1")
public class ApiController {

    @Autowired
    private RestTemplate restTemplate;

    @Value("${app.engine.url}")
    private String engineUrl;

    @PostMapping("/resumes")
    public ResponseEntity<?> createResume(@RequestBody Map<String, Object> payload) {
        // Mock save logic, forwards to engine if needed
        return ResponseEntity.ok(Map.of("message", "Resume uploaded successfully"));
    }

    @PostMapping("/jobs")
    public ResponseEntity<?> createJob(@RequestBody Map<String, Object> payload) {
        return ResponseEntity.ok(Map.of("message", "Job posted successfully"));
    }

    @GetMapping("/jobs/{jobId}/matches")
    public ResponseEntity<?> getJobMatches(@PathVariable String jobId) {
        // Forward mock request to python engine to demonstrate interaction
        Map<String, Object> request = Map.of(
            "candidate", Map.of("skills", java.util.List.of()),
            "job", Map.of("required_skills", java.util.List.of()),
            "weights", Map.of()
        );
        try {
            ResponseEntity<Map> response = restTemplate.postForEntity(
                engineUrl + "/api/v1/algorithms/score", request, Map.class);
            return ResponseEntity.ok(response.getBody());
        } catch(Exception e) {
            return ResponseEntity.internalServerError().body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/allocations/run")
    public ResponseEntity<?> runAllocation(@RequestBody Map<String, Object> payload) {
        return ResponseEntity.ok(Map.of("run_id", "alloc_123", "status", "started"));
    }

    @PostMapping("/teams/{teamId}/min-skill-set")
    public ResponseEntity<?> minSkillSet(@PathVariable String teamId, @RequestBody Map<String, Object> payload) {
        try {
            ResponseEntity<Map> response = restTemplate.postForEntity(
                engineUrl + "/api/v1/algorithms/min-cover/exact", payload, Map.class);
            return ResponseEntity.ok(response.getBody());
        } catch(Exception e) {
            return ResponseEntity.internalServerError().body(Map.of("error", e.getMessage()));
        }
    }
}
