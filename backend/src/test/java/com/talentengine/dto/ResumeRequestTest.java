package com.talentengine.dto;

import jakarta.validation.ConstraintViolation;
import jakarta.validation.Validation;
import jakarta.validation.Validator;
import jakarta.validation.ValidatorFactory;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class ResumeRequestTest {

    private Validator validator;

    @BeforeEach
    public void setUp() {
        ValidatorFactory factory = Validation.buildDefaultValidatorFactory();
        validator = factory.getValidator();
    }

    @Test
    public void testValidResumeRequest() {
        ResumeRequest request = new ResumeRequest();
        request.setCandidateId("C-1");
        request.setSkills(List.of("Java"));

        Set<ConstraintViolation<ResumeRequest>> violations = validator.validate(request);
        assertTrue(violations.isEmpty());
    }

    @Test
    public void testInvalidResumeRequestMissingCandidateId() {
        ResumeRequest request = new ResumeRequest();
        request.setCandidateId(null);
        request.setSkills(List.of("Java"));

        Set<ConstraintViolation<ResumeRequest>> violations = validator.validate(request);
        assertEquals(1, violations.size());
        assertEquals("Candidate ID is required", violations.iterator().next().getMessage());
    }
}
