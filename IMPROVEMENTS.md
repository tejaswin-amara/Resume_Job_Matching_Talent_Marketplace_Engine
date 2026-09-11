# Repository Improvements & Fixes

This document outlines a comprehensive list of improvements, fixes, and technical debt items that need to be addressed across the `DSA-3-PROJECT-` repository.

## 1. Security & Hardening

*   **Secrets in Source Control:** The `backend/src/main/resources/application.yml` file contains a hardcoded JWT secret (`404E635266556A586E3272357538782F413F4428472B4B6250645367566B5970`). This must be removed from the repository, generated securely, and injected via environment variables.
*   **Database Credentials:** Default MySQL credentials (`root`/`root`) are exposed in `docker-compose.yml` and `application.yml`. These should be replaced with strong, environment-specific passwords and should not be committed to source control.
*   **Security Best Practices:** Ensure that CORS policies are strictly defined in the Spring Boot backend. Use strong hashing algorithms (e.g., Argon2 or BCrypt) for user passwords instead of plain text or weak hashes.
*   **Dependencies:** Regularly scan and update frontend (`package.json`), backend (`pom.xml`), and engine (`requirements.txt`) dependencies to mitigate known vulnerabilities.

## 2. Testing & Quality Assurance

*   **Missing Automated Tests:** The repository is entirely missing automated test suites across all domains (frontend, backend, engine). This is a critical gap.
    *   **Backend (Java):** Implement JUnit tests for services, controllers, and data access layers. Integrate Mockito for mocking dependencies.
    *   **Engine (Python):** Implement `pytest` for all core algorithms (scoring, normalization, allocation). Create dedicated test suites for the hand-built algorithms (KMP, Wagner-Fischer, etc.) against known textbook results and adversarial edge cases as specified in `docs/10-operational-considerations.md`.
    *   **Frontend (Next.js):** Add React Testing Library and Jest for component and page testing. Add Playwright or Cypress for End-to-End (E2E) testing.
*   **Test Coverage:** Set up a test coverage tool (e.g., JaCoCo for Java, `pytest-cov` for Python) and enforce minimum coverage thresholds in CI.

## 3. Architecture & Infrastructure

*   **Database Persistence:** The `docker-compose.yml` mounts `./db/init.sql` but does not persist the MySQL data directory to a named volume. If the container is removed, all database data will be lost. Add a named volume for `/var/lib/mysql`.
*   **Database Schema Management:** The backend relies on Hibernate's `ddl-auto: update`. For production systems, this is highly discouraged. Implement a schema migration tool like Flyway or Liquibase to manage database versioning systematically.
*   **Production Readiness:** The FastAPI engine uses `uvicorn` as a development server. For production, it should use a production-grade ASGI server manager like Gunicorn with Uvicorn workers (`gunicorn -k uvicorn.workers.UvicornWorker`).

## 4. Backend (Spring Boot)

*   **Logging:** Implement structured logging (e.g., using Logback with JSON output) to improve observability, instead of relying on default console logs.
*   **Exception Handling:** Create a centralized `@ControllerAdvice` to handle exceptions globally and return consistent, standardized error responses (e.g., following RFC 7807 Problem Details for HTTP APIs).
*   **Input Validation:** Enforce strict validation on all incoming API payloads using `jakarta.validation` annotations (e.g., `@NotNull`, `@Size`, `@Email`).

## 5. Engine (Python/FastAPI)

*   **Type Hinting & Static Analysis:** Ensure full and accurate Python type hinting across the entire engine codebase. Introduce `mypy` to enforce static type checking.
*   **Code Formatting & Linting:** Standardize code style using `black`, `isort`, and `flake8` or `ruff`. Enforce these checks in the CI pipeline.

## 6. Frontend (Next.js/React)

*   **Linting and Formatting:** Integrate ESLint and Prettier, and configure a strict ruleset. Ensure code formatting is consistent across the frontend.
*   **State Management:** As the application grows, ensure a scalable state management strategy is in place (e.g., React Context, Zustand, or Redux) if prop drilling becomes an issue.
*   **Error Boundaries:** Implement React Error Boundaries to gracefully handle UI crashes and prevent the entire application from unmounting.

## 7. CI/CD & Automation

*   **Pre-commit Hooks:** Introduce `pre-commit` to the repository to automate linting, formatting, and secret scanning (e.g., `trufflehog` or `detect-secrets`) locally before commits are allowed.
*   **GitHub Actions Expansion:** The current `.github/workflows/docs-check.yml` only checks documentation. Expand GitHub Actions to include:
    *   Linting and formatting checks for Python, Java, and TypeScript/JavaScript.
    *   Running all automated tests (unit and integration).
    *   Building Docker images to ensure the build process succeeds.
*   **Git Hooks TODOs:** There are lingering `TODO` comments in `.git/hooks/sendemail-validate.sample`. If this hook is actively used, implement the appropriate validation logic; otherwise, ignore or remove it.

## 8. Documentation

*   **Swagger/OpenAPI:** The API documentation in `docs/07-api-and-service-contracts.md` mentions a "full OpenAPI/Swagger spec should be generated from code." Ensure that `springdoc-openapi` is integrated into the backend and FastAPI's native Swagger UI is exposed for the engine.
*   **Run Instructions:** Add explicit commands in the `README.md` on how to start the full stack using `docker-compose up`, as this is currently implied but not explicitly stated.
