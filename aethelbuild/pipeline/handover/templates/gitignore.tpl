# AethelBuild default .gitignore — copy to prototype repo root
# (Never weaken the secret blocks; adjust only the project-specific sections.)

# ---- Secrets & credentials (hard block) ----
.env
.env.*
!.env.example
*.pem
*.key
*.p12
*.pfx
id_rsa
id_ed25519
credentials.json
*service-account*.json
secrets.*
*.local

# ---- Build / runtime ----
node_modules/
dist/
build/
__pycache__/
*.pyc
.venv/
venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.egg-info/
target/
.bun/

# ---- AethelBuild artifacts (rebuilt, never committed) ----
handover/releases/
handover/bundles/
ab-prototype-*.tar.gz
ab-prototype-*.tar.gz.sha256
ab-handover-*.zip
ab-handover-*.zip.sha256

# ---- Editors / OS ----
.DS_Store
Thumbs.db
*.swp
.idea/
.vscode/