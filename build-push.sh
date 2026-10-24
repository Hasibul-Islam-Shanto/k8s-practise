#!/bin/bash
# ──────────────────────────────────────────────────────
# Build & push multi-platform images to Docker Hub
# Platforms: linux/amd64 (Intel/Linux) + linux/arm64 (Apple Silicon)
# ──────────────────────────────────────────────────────
set -e

DOCKER_USER="shanto78"
PLATFORMS="linux/amd64,linux/arm64"
TAG="${1:-latest}"

echo "🔐 Logging in to Docker Hub..."
docker login -u "$DOCKER_USER"

echo ""
echo "🏗️  Building & pushing backend (${PLATFORMS})..."
docker buildx build \
  --builder multiarch \
  --platform "$PLATFORMS" \
  --tag "${DOCKER_USER}/techblog-backend:${TAG}" \
  --push \
  ./backend

echo ""
echo "🏗️  Building & pushing frontend (${PLATFORMS})..."
docker buildx build \
  --builder multiarch \
  --platform "$PLATFORMS" \
  --tag "${DOCKER_USER}/techblog-frontend:${TAG}" \
  --build-arg VITE_API_URL=/api/v1 \
  --push \
  ./frontend

echo ""
echo "✅ Done! Images pushed:"
echo "   → docker.io/${DOCKER_USER}/techblog-backend:${TAG}"
echo "   → docker.io/${DOCKER_USER}/techblog-frontend:${TAG}"
echo ""
echo "🔍 Verify with:"
echo "   docker buildx imagetools inspect ${DOCKER_USER}/techblog-backend:${TAG}"
echo "   docker buildx imagetools inspect ${DOCKER_USER}/techblog-frontend:${TAG}"
