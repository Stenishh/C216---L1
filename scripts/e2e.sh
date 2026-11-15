#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Fixed project and dedicated ports keep development data out of this lifecycle.
export API_PORT=8001 FRONTEND_PORT=5174 DB_PORT=5433
export VITE_API_URL=http://localhost:8001
export CORS_ORIGINS=http://localhost:5174,http://127.0.0.1:5174
export E2E_BASE_URL=http://localhost:5174
compose=(docker compose --env-file .env.example -p lab-e2e)
cleanup() { "${compose[@]}" down -v --remove-orphans; }
trap cleanup EXIT
"${compose[@]}" up --build --wait --wait-timeout 180
"${compose[@]}" run --rm api alembic upgrade head
npm run test:e2e --prefix frontend
