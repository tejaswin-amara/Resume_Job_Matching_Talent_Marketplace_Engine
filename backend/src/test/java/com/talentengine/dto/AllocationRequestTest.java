package com.talentengine.dto;

import jakarta.validation.ConstraintViolation;
import jakarta.validation.Validation;
import jakarta.validation.Validator;
import jakarta.validation.ValidatorFactory;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Collections;
import java.util.List;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class AllocationRequestTest {

    private Validator validator;

    @BeforeEach
    public void setUp() {
        ValidatorFactory factory = Validation.buildDefaultValidatorFactory();
        validator = factory.getValidator();
    }

    @Test
    public void testValidAllocationRequest() {
        AllocationRequest request = new AllocationRequest();
        request.setCandidates(List.of("C-1"));
        request.setJobs(List.of("J-1"));

        Set<ConstraintViolation<AllocationRequest>> violations = validator.validate(request);
        assertTrue(violations.isEmpty());
    }

    @Test
    public void testInvalidAllocationRequestEmptyCandidates() {
        AllocationRequest request = new AllocationRequest();
        request.setCandidates(Collections.emptyList());
        request.setJobs(List.of("J-1"));

        Set<ConstraintViolation<AllocationRequest>> violations = validator.validate(request);
        assertEquals(1, violations.size());
        assertEquals("Candidates list cannot be empty", violations.iterator().next().getMessage());
    }
}
