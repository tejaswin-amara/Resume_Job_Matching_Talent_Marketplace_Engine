# Threat Model (OWASP Aligned)

## 1. PDF Decompression Bombs
**Threat:** Maliciously crafted PDFs that consume excessive memory or CPU when parsed, leading to Denial of Service (DoS).
**Mitigation:** 
- Implement strict file size limits (e.g., 5MB max).
- Set timeouts for PDF parsing operations.
- Process documents in isolated, resource-constrained workers/sandboxes.

## 2. Script Injection in Resumes
**Threat:** Cross-Site Scripting (XSS) via injected JavaScript payloads within resume text or metadata.
**Mitigation:**
- Strict input validation and sanitization of all extracted text.
- Context-aware output encoding on the Next.js frontend.
- Enforce strict Content Security Policy (CSP).

## 3. Rate Limiting Evasion / Brute Force
**Threat:** Automated scraping of jobs or mass resume uploads to overwhelm the embedding service.
**Mitigation:**
- Implement token bucket rate limiting at the API Gateway level based on IP/User ID.
- Separate limits for read and write operations.

## 4. PII Leakage Prevention
**Threat:** Exposure of sensitive Personally Identifiable Information (PII) to unauthorized parties or embedding logs.
**Mitigation:**
- Run Named Entity Recognition (NER) to redact names, emails, and phone numbers before embedding generation and storage.
- Implement Row-Level Security (RLS) in PostgreSQL.
- Encrypt data at rest (TDE) and in transit (TLS 1.3).
