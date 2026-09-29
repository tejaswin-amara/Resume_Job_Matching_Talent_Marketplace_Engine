FROM python:3.12-slim
LABEL org.opencontainers.image.title="Talent Matching Engine Algorithms API" \
      org.opencontainers.image.description="FastAPI Python engine implementing DSA-3 matching algorithms" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.vendor="Tejaswin Amara" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/tejaswin-amara/resume_job_matching_talent_marketplace_engine"

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m myuser
USER myuser
EXPOSE 8000
CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
