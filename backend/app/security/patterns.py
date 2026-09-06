"""
Curated Secret Detection Regex Patterns & Rules.
Defines regular expressions for cloud keys, SaaS tokens, database URIs, JWTs, and private keys.
"""

import re
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class SecretPattern:
    """Definition of a secret signature pattern."""
    secret_type: str
    pattern: re.Pattern
    placeholder: str
    confidence: str
    description: str
    group_index: int = 0  # Group index to redact (0 for full match, 1 for captured secret)


# Registry of Standardized Secret Patterns
SECRET_PATTERNS: List[SecretPattern] = [
    # 1. Private Keys (RSA, EC, DSA, OpenSSH, PGP)
    SecretPattern(
        secret_type="PRIVATE_KEY",
        pattern=re.compile(
            r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"
        ),
        placeholder="[REDACTED_PRIVATE_KEY]",
        confidence="HIGH",
        description="Asymmetric cryptographic private key block",
        group_index=0
    ),

    # 2. AWS Access Key ID
    SecretPattern(
        secret_type="AWS_ACCESS_KEY",
        pattern=re.compile(r"\b((?:AKIA|ASIA|ABIA|ACCA)[0-9A-Z]{16})\b"),
        placeholder="[REDACTED_AWS_ACCESS_KEY]",
        confidence="HIGH",
        description="Amazon Web Services (AWS) 20-character Access Key ID",
        group_index=1
    ),

    # 3. AWS Secret Access Key (Assignment context)
    SecretPattern(
        secret_type="AWS_SECRET_KEY",
        pattern=re.compile(
            r"(?i)(?:aws_secret_access_key|aws_secret_key|secret_access_key)\s*[:=]\s*['\"]([A-Za-z0-9/+=]{40})['\"]"
        ),
        placeholder="[REDACTED_AWS_SECRET_KEY]",
        confidence="HIGH",
        description="Amazon Web Services (AWS) 40-character Secret Access Key",
        group_index=1
    ),

    # 4. GitHub Personal Access Tokens
    SecretPattern(
        secret_type="GITHUB_TOKEN",
        pattern=re.compile(r"\b(gh[pousr]_[A-Za-z0-9_]{36,255}|github_pat_[A-Za-z0-9_]{82})\b"),
        placeholder="[REDACTED_GITHUB_TOKEN]",
        confidence="HIGH",
        description="GitHub Classic or Fine-Grained Personal Access Token",
        group_index=1
    ),

    # 5. GitLab Personal Access Tokens
    SecretPattern(
        secret_type="GITLAB_TOKEN",
        pattern=re.compile(r"\b(glpat-[0-9a-zA-Z\-_]{20,})\b"),
        placeholder="[REDACTED_GITLAB_TOKEN]",
        confidence="HIGH",
        description="GitLab Personal Access Token",
        group_index=1
    ),

    # 6. OpenAI API Key
    SecretPattern(
        secret_type="OPENAI_API_KEY",
        pattern=re.compile(r"\b(sk-[a-zA-Z0-9]{20,T3BlbkFJ[a-zA-Z0-9]{20,}|sk-proj-[a-zA-Z0-9_\-]{40,}|sk-[a-zA-Z0-9]{32,})\b"),
        placeholder="[REDACTED_OPENAI_KEY]",
        confidence="HIGH",
        description="OpenAI Platform API Secret Key",
        group_index=1
    ),

    # 7. Google Cloud / Maps API Key
    SecretPattern(
        secret_type="GOOGLE_API_KEY",
        pattern=re.compile(r"\b(AIza[0-9A-Za-z\-_]{35})\b"),
        placeholder="[REDACTED_GOOGLE_API_KEY]",
        confidence="HIGH",
        description="Google Cloud API / Firebase Credentials",
        group_index=1
    ),

    # 8. Stripe API Key (Live & Test)
    SecretPattern(
        secret_type="STRIPE_KEY",
        pattern=re.compile(r"\b((?:sk|rk)_(?:live|test)_[0-9a-zA-Z]{24,})\b"),
        placeholder="[REDACTED_STRIPE_KEY]",
        confidence="HIGH",
        description="Stripe Secret or Restricted API Key",
        group_index=1
    ),

    # 9. Slack OAuth & Bot Token
    SecretPattern(
        secret_type="SLACK_TOKEN",
        pattern=re.compile(r"\b(xox[baprs]-[0-9a-zA-Z]{10,48})\b"),
        placeholder="[REDACTED_SLACK_TOKEN]",
        confidence="HIGH",
        description="Slack Web API Bot or User OAuth Token",
        group_index=1
    ),

    # 10. JSON Web Token (JWT)
    SecretPattern(
        secret_type="JWT_TOKEN",
        pattern=re.compile(r"\b(eyJ[A-Za-z0-9-_=]{10,}\.eyJ[A-Za-z0-9-_=]{10,}\.[A-Za-z0-9-_.+/=]{10,})\b"),
        placeholder="[REDACTED_JWT_TOKEN]",
        confidence="HIGH",
        description="Signed JSON Web Token (JWT) credential",
        group_index=1
    ),

    # 11. Database Connection URI with embedded password
    SecretPattern(
        secret_type="DATABASE_URI",
        pattern=re.compile(
            r"\b((?:postgres|postgresql|mysql|mongodb|redis|amqp|mssql):\/\/[a-zA-Z0-9_\-\.]+:[^@\s/]+@[a-zA-Z0-9_\-\.]+(?::\d+)?\/[a-zA-Z0-9_\-\.]+)\b"
        ),
        placeholder="[REDACTED_DATABASE_URI]",
        confidence="HIGH",
        description="Database Connection String containing embedded credentials",
        group_index=1
    ),

    # 12. Generic Hardcoded Password / Credentials Assignment
    SecretPattern(
        secret_type="PASSWORD",
        pattern=re.compile(
            r"(?i)(?:password|passwd|pwd|db_password|api_secret|auth_token|client_secret|secret_key)\s*[:=]\s*['\"]([^'\"\r\n]{6,})['\"]"
        ),
        placeholder="[REDACTED_PASSWORD]",
        confidence="MEDIUM",
        description="Hardcoded password or secret key assignment",
        group_index=1
    ),
]
