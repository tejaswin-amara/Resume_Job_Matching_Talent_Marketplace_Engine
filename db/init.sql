-- Phase 1: Database Initialization & Modeling
-- Tables based on 02-data-model-and-normalization.md and 11-schemas-workflows-pseudocode.md

CREATE DATABASE IF NOT EXISTS talent_engine;
USE talent_engine;

-- Skill Ontology
CREATE TABLE skill_nodes (
    skill_id VARCHAR(255) PRIMARY KEY,
    display_name VARCHAR(255) NOT NULL,
    embedding_vector JSON, -- using JSON to store float array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE skill_aliases (
    alias VARCHAR(255) PRIMARY KEY,
    skill_id VARCHAR(255) NOT NULL,
    FOREIGN KEY (skill_id) REFERENCES skill_nodes(skill_id)
);

CREATE TABLE skill_hierarchy (
    parent_id VARCHAR(255) NOT NULL,
    child_id VARCHAR(255) NOT NULL,
    PRIMARY KEY (parent_id, child_id),
    FOREIGN KEY (parent_id) REFERENCES skill_nodes(skill_id),
    FOREIGN KEY (child_id) REFERENCES skill_nodes(skill_id)
);

CREATE TABLE skill_related (
    skill_id_1 VARCHAR(255) NOT NULL,
    skill_id_2 VARCHAR(255) NOT NULL,
    weight FLOAT NOT NULL,
    PRIMARY KEY (skill_id_1, skill_id_2),
    FOREIGN KEY (skill_id_1) REFERENCES skill_nodes(skill_id),
    FOREIGN KEY (skill_id_2) REFERENCES skill_nodes(skill_id)
);

-- Candidates & Resumes
CREATE TABLE candidates (
    candidate_id VARCHAR(36) PRIMARY KEY,
    email_hash VARCHAR(255) UNIQUE NOT NULL,
    phone_hash VARCHAR(255),
    location_geo JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE resumes (
    resume_id VARCHAR(36) PRIMARY KEY,
    candidate_id VARCHAR(36) NOT NULL,
    raw_source_ref VARCHAR(1024),
    summary_text TEXT,
    earliest_start_date DATE,
    hours_per_week INT,
    remote_ok BOOLEAN,
    work_auth_status VARCHAR(50),
    embedding_vector JSON,
    parsed_at TIMESTAMP,
    parser_version VARCHAR(50),
    FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id)
);

CREATE TABLE resume_skills (
    resume_id VARCHAR(36) NOT NULL,
    skill_id VARCHAR(255) NOT NULL,
    raw_text VARCHAR(255),
    confidence FLOAT,
    years_experience FLOAT,
    source_span_start INT,
    source_span_end INT,
    PRIMARY KEY (resume_id, skill_id),
    FOREIGN KEY (resume_id) REFERENCES resumes(resume_id),
    FOREIGN KEY (skill_id) REFERENCES skill_nodes(skill_id)
);

CREATE TABLE resume_experience (
    experience_id INT AUTO_INCREMENT PRIMARY KEY,
    resume_id VARCHAR(36) NOT NULL,
    title VARCHAR(255),
    company VARCHAR(255),
    start_date DATE,
    end_date DATE,
    responsibilities_text TEXT,
    FOREIGN KEY (resume_id) REFERENCES resumes(resume_id)
);

CREATE TABLE resume_education (
    education_id INT AUTO_INCREMENT PRIMARY KEY,
    resume_id VARCHAR(36) NOT NULL,
    degree VARCHAR(255),
    institution VARCHAR(255),
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (resume_id) REFERENCES resumes(resume_id)
);

CREATE TABLE consent_records (
    candidate_id VARCHAR(36) PRIMARY KEY,
    given_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revocable_until TIMESTAMP,
    marketing_opt_in BOOLEAN DEFAULT FALSE,
    scopes JSON,
    FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id)
);

-- Employers & Job Postings
CREATE TABLE employers (
    employer_id VARCHAR(36) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE job_postings (
    job_id VARCHAR(36) PRIMARY KEY,
    employer_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    team_id VARCHAR(36),
    description_text TEXT,
    location_geo JSON,
    remote_policy VARCHAR(50),
    seniority_level VARCHAR(50),
    headcount INT DEFAULT 1,
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('open', 'filled', 'closed') DEFAULT 'open',
    embedding_vector JSON,
    work_auth_required JSON,
    FOREIGN KEY (employer_id) REFERENCES employers(employer_id)
);

CREATE TABLE job_skills (
    job_id VARCHAR(36) NOT NULL,
    skill_id VARCHAR(255) NOT NULL,
    is_required BOOLEAN NOT NULL DEFAULT TRUE,
    min_years FLOAT,
    weight FLOAT,
    hard_constraint BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (job_id, skill_id),
    FOREIGN KEY (job_id) REFERENCES job_postings(job_id),
    FOREIGN KEY (skill_id) REFERENCES skill_nodes(skill_id)
);

-- Indexes for performance (Section 2.4 & 6.5)
CREATE INDEX idx_job_status ON job_postings(status);
CREATE INDEX idx_resume_parsed_at ON resumes(parsed_at);
CREATE INDEX idx_resume_skills_skill ON resume_skills(skill_id);
CREATE INDEX idx_job_skills_skill ON job_skills(skill_id);
CREATE INDEX idx_candidate_email ON candidates(email_hash);

-- Team and Allocation Models
CREATE TABLE teams (
    team_id VARCHAR(36) PRIMARY KEY,
    employer_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    FOREIGN KEY (employer_id) REFERENCES employers(employer_id)
);

CREATE TABLE allocations (
    allocation_id VARCHAR(36) PRIMARY KEY,
    team_id VARCHAR(36),
    job_id VARCHAR(36) NOT NULL,
    candidate_id VARCHAR(36) NOT NULL,
    score FLOAT,
    status ENUM('proposed', 'accepted', 'rejected') DEFAULT 'proposed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    FOREIGN KEY (job_id) REFERENCES job_postings(job_id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id)
);

CREATE INDEX idx_allocations_job ON allocations(job_id);
CREATE INDEX idx_allocations_candidate ON allocations(candidate_id);
