FROM maven:3.9.6-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre
LABEL org.opencontainers.image.title="Talent Engine Java Backend" \
      org.opencontainers.image.description="Spring Boot Java API Gateway and Service Controller" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.vendor="Tejaswin Amara" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/tejaswin-amara/resume_job_matching_talent_marketplace_engine"

WORKDIR /app
COPY --from=build /app/target/backend-0.0.1-SNAPSHOT.jar app.jar
RUN useradd -m myuser
USER myuser
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
