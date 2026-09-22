package com.talentengine.dto;

import jakarta.validation.ConstraintViolation;
import jakarta.validation.Validation;
import jakarta.validation.Validator;
import jakarta.validation.ValidatorFactory;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class MinSkillSetRequestTest {

    private Validator validator;

    @BeforeEach
    public void setUp() {
        ValidatorFactory factory = Validation.buildDefaultValidatorFactory();
        validator = factory.getValidator();
    }

    @Test
    public void testValidMinSkillSetRequest() {
        MinSkillSetRequest request = new MinSkillSetRequest();
        request.setCapabilities(Map.of("C-1", List.of("Java")));
        request.setRequiredSkills(List.of("Java"));

        Set<ConstraintViolation<MinSkillSetRequest>> violations = validator.validate(request);
        assertTrue(violations.isEmpty());
    }

    @Test
    public void testInvalidMinSkillSetRequestEmptyCapabilities() {
        MinSkillSetRequest request = new MinSkillSetRequest();
        request.setCapabilities(Collections.emptyMap());
        request.setRequiredSkills(List.of("Java"));

        Set<ConstraintViolation<MinSkillSetRequest>> violations = validator.validate(request);
        assertEquals(1, violations.size());
        assertEquals("Capabilities map cannot be empty", violations.iterator().next().getMessage());
    }
}
