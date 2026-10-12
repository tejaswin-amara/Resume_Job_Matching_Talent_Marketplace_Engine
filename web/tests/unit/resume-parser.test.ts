import { describe, it, expect } from "vitest";
import {
  extractNameFromText,
  extractContactInfo,
  extractSkillsFromText,
  extractEducation,
  extractRolesAndExperience,
  parseFullResume,
} from "../../src/lib/server-engine";

describe("Resume Parser Engine", () => {
  const sampleResume = `
Jane Doe
jane.doe@example.com | (555) 234-5678 | San Francisco, CA
https://linkedin.com/in/janedoe | https://github.com/janedoe

Professional Summary
Senior Full-Stack Engineer with 6+ years of experience designing and deploying high-scale cloud native applications.

Work Experience
Senior Full-Stack Engineer | Acme Cloud Corp
2021 - Present
- Architected microservices with FastAPI and React
- Optimized PostgreSQL database queries

Software Engineer | BetaTech Systems
2018 - 2021
- Developed frontend UI in TypeScript and Next.js
- Configured Docker and CI/CD pipelines

Education
Bachelor of Science in Computer Science
Stanford University, 2018

Skills
Python, FastAPI, TypeScript, React, Next.js, PostgreSQL, Docker, Kubernetes, AWS, Git
`;

  it("extracts candidate name from top lines or explicit label", () => {
    const name = extractNameFromText(sampleResume);
    expect(name).toBe("Jane Doe");

    const labeledResume = "Name: Alex Mercer\nDeveloper with Python skills.";
    expect(extractNameFromText(labeledResume)).toBe("Alex Mercer");

    const fallbackName = extractNameFromText("Random skills only", "john_smith_resume.pdf");
    expect(fallbackName).toBe("John Smith");
  });

  it("extracts contact information (email, phone, location, linkedin, github)", () => {
    const contact = extractContactInfo(sampleResume);
    expect(contact.email).toBe("jane.doe@example.com");
    expect(contact.phone).toBe("(555) 234-5678");
    expect(contact.location).toBe("San Francisco, CA");
    expect(contact.linkedin).toBe("linkedin.com/in/janedoe");
    expect(contact.github).toBe("github.com/janedoe");
  });

  it("extracts skills accurately from taxonomy", () => {
    const skills = extractSkillsFromText(sampleResume);
    expect(skills).toContain("Python");
    expect(skills).toContain("FastAPI");
    expect(skills).toContain("TypeScript");
    expect(skills).toContain("React");
    expect(skills).toContain("Docker");
    expect(skills).toContain("PostgreSQL");
  });

  it("extracts education with degree level and institution", () => {
    const { education, education_level } = extractEducation(sampleResume);
    expect(education.length).toBeGreaterThan(0);
    expect(education[0].degree).toBe("Bachelor's Degree");
    expect(education[0].institution).toContain("Stanford University");
    expect(education[0].year).toBe("2018");
    expect(education_level).toBe(2);
  });

  it("extracts work experience roles and calculates total years", () => {
    const { roles, years_experience } = extractRolesAndExperience(sampleResume);
    expect(roles.length).toBe(2);
    expect(roles[0].title).toBe("Senior Full-Stack Engineer");
    expect(roles[0].company).toContain("Acme Cloud Corp");
    expect(roles[1].title).toBe("Software Engineer");
    expect(roles[1].company).toContain("BetaTech Systems");
    expect(years_experience).toBeGreaterThanOrEqual(6.0);
  });

  it("produces a complete parsed profile with parseFullResume", () => {
    const profile = parseFullResume(sampleResume, "Jane_Doe_Resume.pdf");
    expect(profile.name).toBe("Jane Doe");
    expect(profile.email).toBe("jane.doe@example.com");
    expect(profile.phone).toBe("(555) 234-5678");
    expect(profile.location).toBe("San Francisco, CA");
    expect(profile.skills.length).toBeGreaterThan(5);
    expect(profile.roles.length).toBe(2);
    expect(profile.education.length).toBe(1);
    expect(profile.years_experience).toBeGreaterThanOrEqual(6.0);
  });
});
