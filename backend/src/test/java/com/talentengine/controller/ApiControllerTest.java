package com.talentengine.controller;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(properties = {
    "spring.datasource.url=jdbc:h2:mem:testdb",
    "spring.datasource.driver-class-name=org.h2.Driver",
    "spring.flyway.enabled=false"
})
@AutoConfigureMockMvc
@ActiveProfiles("test")
public class ApiControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    public void testCreateResumeValidationFail() throws Exception {
        String invalidPayload = "{\"skills\": []}"; // Missing candidateId
        mockMvc.perform(post("/v1/resumes")
                .contentType(MediaType.APPLICATION_JSON)
                .content(invalidPayload))
                .andExpect(status().isBadRequest());
    }

    @Test
    public void testCreateResumeSuccess() throws Exception {
        String validPayload = "{\"candidateId\": \"cand-123\", \"skills\": [\"Java\"]}";
        mockMvc.perform(post("/v1/resumes")
                .contentType(MediaType.APPLICATION_JSON)
                .content(validPayload))
                .andExpect(status().isOk());
    }

    @Test
    public void testCreateJobValidationFail() throws Exception {
        String invalidPayload = "{\"requiredSkills\": []}"; // Missing title
        mockMvc.perform(post("/v1/jobs")
                .contentType(MediaType.APPLICATION_JSON)
                .content(invalidPayload))
                .andExpect(status().isBadRequest());
    }

    @Test
    public void testCreateJobSuccess() throws Exception {
        String validPayload = "{\"title\": \"Software Engineer\", \"requiredSkills\": [\"Java\"]}";
        mockMvc.perform(post("/v1/jobs")
                .contentType(MediaType.APPLICATION_JSON)
                .content(validPayload))
                .andExpect(status().isOk());
    }

    @Test
    public void testRunAllocationValidationFail() throws Exception {
        String invalidPayload = "{\"candidates\": [\"cand-1\"]}"; // Missing jobs
        mockMvc.perform(post("/v1/allocations/run")
                .contentType(MediaType.APPLICATION_JSON)
                .content(invalidPayload))
                .andExpect(status().isBadRequest());
    }

    @Test
    public void testRunAllocationSuccess() throws Exception {
        String validPayload = "{\"candidates\": [\"cand-1\"], \"jobs\": [\"job-1\"]}";
        mockMvc.perform(post("/v1/allocations/run")
                .contentType(MediaType.APPLICATION_JSON)
                .content(validPayload))
                .andExpect(status().isOk());
    }
}
