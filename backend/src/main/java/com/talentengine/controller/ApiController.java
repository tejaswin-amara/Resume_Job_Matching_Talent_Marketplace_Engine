package com.talentengine.controller;

import com.talentengine.dto.AllocationRequest;
import com.talentengine.dto.JobRequest;
import com.talentengine.dto.ResumeRequest;
import com.talentengine.dto.MinSkillSetRequest;
import com.talentengine.service.StorageService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.util.Map;

@RestController
@RequestMapping("/v1")
public class ApiController {

    private final RestClient restClient;
    private final StorageService storageService;

    public ApiController(RestClient.Builder restClientBuilder, @Value("${app.engine.url}") String engineUrl, StorageService storageService) {
        this.restClient = restClientBuilder
                .baseUrl(engineUrl)
                .build();
        this.storageService = storageService;
    }

    @PostMapping("/resumes")
    public ResponseEntity<?> createResume(@Valid @RequestBody ResumeRequest payload) {
        // Save raw text locally as requested
        String content = "Candidate ID: " + payload.getCandidateId() + "\nSkills: " + payload.getSkills();
        ByteArrayInputStream is = new ByteArrayInputStream(content.getBytes(StandardCharsets.UTF_8));
        storageService.store(payload.getCandidateId() + ".txt", is);

        return ResponseEntity.ok(Map.of("message", "Resume uploaded successfully and stored locally"));
    }

    @PostMapping("/jobs")
    public ResponseEntity<?> createJob(@Valid @RequestBody JobRequest payload) {
        // Mock save logic
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
            Map response = restClient.post()
                    .uri("/api/v1/algorithms/score")
                    .body(request)
                    .retrieve()
                    .body(Map.class);
            return ResponseEntity.ok(response);
        } catch(RestClientException e) {
            return ResponseEntity.internalServerError().body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/allocations/run")
    public ResponseEntity<?> runAllocation(@Valid @RequestBody AllocationRequest payload) {
        return ResponseEntity.ok(Map.of("run_id", "alloc_123", "status", "started"));
    }

    @PostMapping("/teams/{teamId}/min-skill-set")
    public ResponseEntity<?> minSkillSet(@PathVariable String teamId, @Valid @RequestBody MinSkillSetRequest payload) {
        try {
            Map response = restClient.post()
                    .uri("/api/v1/algorithms/min-cover/exact")
                    .body(payload)
                    .retrieve()
                    .body(Map.class);
            return ResponseEntity.ok(response);
        } catch(RestClientException e) {
            return ResponseEntity.internalServerError().body(Map.of("error", e.getMessage()));
        }
    }
}
