"""
Central API Router for the Modular Monolith Backend.
Aggregates all module routers under standard API prefixes.
"""

from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.ingestion import router as ingestion_router
from app.api.v1.security import router as security_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.risk import router as risk_router
from app.api.v1.ai import router as ai_router
from app.api.v1.remediation import router as remediation_router
from app.api.v1.rag import router as rag_router
from app.api.v1.github_pr import router as github_pr_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.auth import router as auth_router
from app.api.v1.audit import router as audit_router

# Root API Router
api_router = APIRouter()

# Register Health routes directly at /api/health
api_router.include_router(health_router, prefix="", tags=["Health"])

# Register Authentication & Authorization routes at /api/auth
api_router.include_router(auth_router, prefix="", tags=["Authentication & Authorization"])

# Register Security Audit routes at /api/audit
api_router.include_router(audit_router, prefix="", tags=["Security Audit & Compliance"])

# Register Code Ingestion routes directly at /api/code
api_router.include_router(ingestion_router, prefix="/code", tags=["Code Ingestion"])

# Register Security & Privacy routes directly at /api/security
api_router.include_router(security_router, prefix="/security", tags=["Security & Privacy"])

# Register Static Code Analysis routes directly at /api/analysis
api_router.include_router(analysis_router, prefix="/analysis", tags=["Static Code Analysis"])

# Register Code Risk Scoring routes directly at /api/risk
api_router.include_router(risk_router, prefix="/risk", tags=["Code Risk Scoring"])

# Register Privacy-Aware AI Analysis routes directly at /api/ai
api_router.include_router(ai_router, prefix="/ai", tags=["Privacy-Aware AI Analysis"])

# Register AI Developer Remediation routes directly at /api/remediation
api_router.include_router(remediation_router, prefix="/remediation", tags=["AI Developer Remediation"])

# Register Engineering Knowledge RAG routes directly at /api/rag
api_router.include_router(rag_router, prefix="/rag", tags=["Engineering Knowledge RAG"])

# Register GitHub PR Security routes directly at /api/github/pr
api_router.include_router(github_pr_router, prefix="/github/pr", tags=["GitHub Pull Request Security"])

# Register Dashboard Analytics routes directly at /api/analytics
api_router.include_router(analytics_router, prefix="/analytics", tags=["Engineering Dashboard Analytics"])

# Version 1 Subrouter (/api/v1)
v1_router = APIRouter(prefix="/v1")
v1_router.include_router(health_router, prefix="", tags=["Health"])
v1_router.include_router(auth_router, prefix="", tags=["Authentication & Authorization"])
v1_router.include_router(audit_router, prefix="", tags=["Security Audit & Compliance"])
v1_router.include_router(ingestion_router, prefix="/code", tags=["Code Ingestion"])
v1_router.include_router(security_router, prefix="/security", tags=["Security & Privacy"])
v1_router.include_router(analysis_router, prefix="/analysis", tags=["Static Code Analysis"])
v1_router.include_router(risk_router, prefix="/risk", tags=["Code Risk Scoring"])
v1_router.include_router(ai_router, prefix="/ai", tags=["Privacy-Aware AI Analysis"])
v1_router.include_router(remediation_router, prefix="/remediation", tags=["AI Developer Remediation"])
v1_router.include_router(rag_router, prefix="/rag", tags=["Engineering Knowledge RAG"])
v1_router.include_router(github_pr_router, prefix="/github/pr", tags=["GitHub Pull Request Security"])
v1_router.include_router(analytics_router, prefix="/analytics", tags=["Engineering Dashboard Analytics"])

api_router.include_router(v1_router)


