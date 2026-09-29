FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

FROM node:20-alpine AS runner
LABEL org.opencontainers.image.title="Talent Engine Frontend" \
      org.opencontainers.image.description="Next.js dark-themed glassmorphic marketplace UI" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.vendor="Tejaswin Amara" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/tejaswin-amara/resume_job_matching_talent_marketplace_engine"

WORKDIR /app
ENV NODE_ENV=production
RUN addgroup -S nodejs && adduser -S nextjs -G nodejs
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
ENV PORT=3000
CMD ["node", "server.js"]
