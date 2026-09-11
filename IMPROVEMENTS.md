# Comprehensive Repository Improvements & Fixes

This document serves as a detailed roadmap for addressing technical debt, fixing vulnerabilities, and establishing production-grade engineering standards across the `DSA-3-PROJECT-` repository.

---

## 1. Security & Hardening 🔒

*   **Remove Hardcoded Secrets:** The `backend/src/main/resources/application.yml` file contains a hardcoded, plaintext JWT secret (`app.jwt.secret`). This must be removed from source control immediately. Secrets must be injected via environment variables (e.g., `${JWT_SECRET}`).
*   **Secure Database Credentials:** Default MySQL credentials (`root`/`root`) are exposed in both `docker-compose.yml` and `application.yml`. These must be changed to strong, environment-specific credentials and managed via `.env` files (which should be added to `.gitignore`).
*   **Backend Security Configuration:** The Spring Security setup needs to be explicitly configured to define robust CORS policies, enable/disable CSRF appropriately for stateless API usage, and provide a strong `PasswordEncoder` (e.g., `BCryptPasswordEncoder` or `Argon2PasswordEncoder`).
*   **Container Security:** Ensure Dockerfiles across all services (frontend, backend, engine) utilize non-root users, employ multi-stage builds to minimize image surface area, and scan for CVEs during the CI pipeline.

## 2. Architecture & Infrastructure 🏗️

*   **Database Persistence:** The MySQL service in `docker-compose.yml` mounts an initialization script but lacks a named volume for `/var/lib/mysql`. Without this, all database state is lost when the container is removed or updated. Add a persistent named volume.
*   **Database Schema Management:** The Spring Boot backend currently relies on `spring.jpa.hibernate.ddl-auto: update`. This is highly dangerous for production databases. Implement a formal schema migration tool (Flyway or Liquibase) and disable `ddl-auto`. Move `db/init.sql` into the appropriate migration folder structure.
*   **Engine Production Readiness:** The FastAPI engine currently runs using the `uvicorn` development server directly in `docker-compose.yml` (`command: uvicorn main:app --host 0.0.0.0 --port 8000`). For a production deployment, it must use a robust ASGI process manager like Gunicorn with Uvicorn workers (`gunicorn -k uvicorn.workers.UvicornWorker`).

## 3. Backend (Spring Boot / Java) ☕

*   **Replace RestTemplate:** `ApiController.java` uses `RestTemplate`, which is in maintenance mode. Migrate to the modern synchronous `RestClient` (introduced in Spring 6.1) or the reactive `WebClient`.
*   **Strong Typing & DTOs:** The `ApiController` endpoints accept and return raw `Map<String, Object>`. This defeats the purpose of Java's static typing. Introduce dedicated Data Transfer Objects (DTOs) for all requests and responses.
*   **Input Validation:** Implement robust input validation using `jakarta.validation` annotations (`@Valid`, `@NotNull`, `@NotBlank`, etc.) on incoming DTOs to prevent malformed data from reaching the business logic.
*   **Global Exception Handling:** Implement a centralized `@ControllerAdvice` class to catch exceptions (e.g., `MethodArgumentNotValidException`, generic `Exception`) and return standardized RFC 7807 Problem Detail JSON responses.
*   **Structured Logging:** Replace default console logging with structured JSON logging (e.g., via Logback JSON encoder) to facilitate ingestion by observability platforms like ELK or Datadog.
*   **OpenAPI Documentation:** Add the `springdoc-openapi-starter-webmvc-ui` dependency to automatically generate and host Swagger documentation for the Java backend APIs.

## 4. Engine (Python / FastAPI) 🐍

*   **Comprehensive Type Hinting:** Add strict static type hints (`-> dict`, `-> List[str]`, etc.) to all functions and variables in the `engine/` directory.
*   **Static Analysis & Formatting:** Integrate `mypy` for static type checking, `black` for deterministic code formatting, `isort` for import sorting, and `ruff` or `flake8` for linting. Add these to `requirements.txt`.
*   **State Management:** `main.py` utilizes in-memory dictionaries and models (`AliasTrie`, `OntologyEmbeddings`). This will not scale horizontally across multiple worker processes. Consider moving shared state to an external store like Redis or initializing models efficiently on worker startup.

## 5. Frontend (Next.js / React) ⚛️

*   **Linting & Code Style:** The frontend lacks a configured linter. Install and configure `eslint` (with Next.js core web vitals) and `prettier` to enforce code consistency.
*   **Error Boundaries:** The Next.js App Router does not currently have robust error handling. Implement `error.js` / `global-error.js` boundaries to catch render errors gracefully and prevent white screens of death.
*   **State Management Strategy:** As the UI scales, define a clear state management approach (e.g., React Context for global theme/auth, Zustand or Redux for complex domain state) to avoid prop-drilling.

## 6. Testing & Quality Assurance 🧪

*   **Address Complete Lack of Tests:** The entire repository has **zero** automated tests. This is a critical risk.
    *   **Backend (Java):** Write unit tests for controllers and services using JUnit 5 and Mockito. Implement integration tests using `@SpringBootTest` and Testcontainers for the database.
    *   **Engine (Python):** Add `pytest` to `requirements.txt`. Write exhaustive unit tests for the core, hand-built algorithms (KMP, Wagner-Fischer, bipartite matching, set cover) using known edge cases.
    *   **Frontend (Next.js):** Integrate Jest and React Testing Library for component unit tests. Add Playwright or Cypress for end-to-end (E2E) testing of critical user journeys.
*   **Code Coverage:** Enforce code coverage thresholds using JaCoCo (Java) and `pytest-cov` (Python). Fail the CI build if coverage drops below the defined threshold (e.g., 80%).

## 7. CI/CD & Automation ⚙️

*   **Expand GitHub Actions:** The current `.github/workflows/docs-check.yml` only validates markdown links. Create a robust CI pipeline (`ci.yml`) that triggers on PRs to:
    *   Run frontend, backend, and engine linting/formatting checks.
    *   Execute all automated tests across all three codebases.
    *   Build Docker images to verify compilation and dependency resolution succeed.
*   **Pre-Commit Hooks:** Add a `.pre-commit-config.yaml` file to enforce code formatting (`black`, `isort`, `prettier`) and basic security scanning (e.g., `detect-secrets`) locally before developers can push commits.
*   **Clean Up Git Hooks:** Review and resolve the `TODO` placeholders in `.git/hooks/sendemail-validate.sample`, or remove the sample file if email patch validation is not part of the team's workflow.

## 8. Documentation 📚

*   **Onboarding / Startup Guide:** While the documentation is extensive regarding algorithms and system design, the `README.md` lacks explicit, step-by-step instructions for a new developer to start the application (e.g., `docker-compose up --build`). Update the README to include a "Quick Start" section.
