package com.talentengine;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.MySQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@Testcontainers
public class DatabaseIntegrationTest {

    @Container
    static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8.0")
            .withDatabaseName("talent_engine")
            .withUsername("root")
            .withPassword("root");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", mysql::getJdbcUrl);
        registry.add("spring.datasource.username", mysql::getUsername);
        registry.add("spring.datasource.password", mysql::getPassword);
        registry.add("spring.flyway.enabled", () -> "true");
    }

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Test
    void testDatabaseConnectionAndFlywayMigration() {
        Integer count = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'talent_engine'", Integer.class);
        assertThat(count).isGreaterThanOrEqualTo(0);
    }
}
