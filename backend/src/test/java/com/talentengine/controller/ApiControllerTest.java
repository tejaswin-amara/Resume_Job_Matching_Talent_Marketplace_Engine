package com.talentengine.controller;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.client.AutoConfigureMockRestServiceServer;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.web.client.RestClient;

import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withServerError;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(properties = {
    "spring.datasource.url=jdbc:h2:mem:testdb",
    "spring.datasource.driver-class-name=org.h2.Driver",
    "spring.flyway.enabled=false",
    "app.jwt.secret=secret",
    "app.engine.url=http://localhost:8000"
})
@AutoConfigureMockMvc
@AutoConfigureMockRestServiceServer
@ActiveProfiles("test")
public class ApiControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private MockRestServiceServer mockServer;

    @BeforeEach
    public void setUp() {
        mockServer.reset();
    }

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

    @Test
    public void testGetJobMatchesSuccess() throws Exception {
        mockServer.expect(requestTo("http://localhost:8000/api/v1/algorithms/score"))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withSuccess("{\"score\": 100}", MediaType.APPLICATION_JSON));

        mockMvc.perform(get("/v1/jobs/job-1/matches"))
                .andExpect(status().isOk());

        mockServer.verify();
    }

    @Test
    public void testGetJobMatchesEngineError() throws Exception {
        mockServer.expect(requestTo("http://localhost:8000/api/v1/algorithms/score"))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withServerError());

        mockMvc.perform(get("/v1/jobs/job-1/matches"))
                .andExpect(status().isInternalServerError());

        mockServer.verify();
    }

    @Test
    public void testMinSkillSetSuccess() throws Exception {
        mockServer.expect(requestTo("http://localhost:8000/api/v1/algorithms/min-cover/exact"))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withSuccess("{\"result\": \"success\"}", MediaType.APPLICATION_JSON));

        String validPayload = "{\"capabilities\": {\"cand-1\": [\"Java\"]}, \"requiredSkills\": [\"Java\"]}";
        mockMvc.perform(post("/v1/teams/team-1/min-skill-set")
                .contentType(MediaType.APPLICATION_JSON)
                .content(validPayload))
                .andExpect(status().isOk());

        mockServer.verify();
    }

    @Test
    public void testMinSkillSetEngineError() throws Exception {
        mockServer.expect(requestTo("http://localhost:8000/api/v1/algorithms/min-cover/exact"))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withServerError());

        String validPayload = "{\"capabilities\": {\"cand-1\": [\"Java\"]}, \"requiredSkills\": [\"Java\"]}";
        mockMvc.perform(post("/v1/teams/team-1/min-skill-set")
                .contentType(MediaType.APPLICATION_JSON)
                .content(validPayload))
                .andExpect(status().isInternalServerError());

        mockServer.verify();
    }

    @Test
    public void testMinSkillSetValidationFail() throws Exception {
        String invalidPayload = "{\"requiredSkills\": [\"Java\"]}"; // Missing capabilities
        mockMvc.perform(post("/v1/teams/team-1/min-skill-set")
                .contentType(MediaType.APPLICATION_JSON)
                .content(invalidPayload))
                .andExpect(status().isBadRequest());
    }
}
