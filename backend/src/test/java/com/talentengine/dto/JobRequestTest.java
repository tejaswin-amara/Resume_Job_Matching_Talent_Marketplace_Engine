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

public class JobRequestTest {

    private Validator validator;

    @BeforeEach
    public void setUp() {
        ValidatorFactory factory = Validation.buildDefaultValidatorFactory();
        validator = factory.getValidator();
    }

    @Test
    public void testValidJobRequest() {
        JobRequest request = new JobRequest();
        request.setTitle("Developer");
        request.setRequiredSkills(List.of("Java"));

        Set<ConstraintViolation<JobRequest>> violations = validator.validate(request);
        assertTrue(violations.isEmpty());
    }

    @Test
    public void testInvalidJobRequestMissingTitle() {
        JobRequest request = new JobRequest();
        request.setTitle(""); // Not blank
        request.setRequiredSkills(List.of("Java"));

        Set<ConstraintViolation<JobRequest>> violations = validator.validate(request);
        assertEquals(1, violations.size());
        assertEquals("Job Title is required", violations.iterator().next().getMessage());
    }
}
