"""
Offline Safe Mock LLM Provider.

Simulates privacy-preserving LLM explanations for local development and CI testing
without transmitting source code to any external network or requiring API keys.
"""

from typing import Dict, Any
import asyncio

from app.schemas.ai import MinimizedContext, AIFindingExplanation
from app.ai.providers.base import LLMProvider


class MockLLMProvider(LLMProvider):
    """Deterministic offline provider generating context-aware remediation templates."""

    def __init__(self, model_name: str = "privacy-guard-mock-v1", simulated_delay_ms: float = 20.0) -> None:
        super().__init__(model_name=model_name)
        self.simulated_delay_ms = simulated_delay_ms

    @property
    def provider_name(self) -> str:
        return "MockLLMProvider (Offline)"

    async def generate_explanation(
        self,
        context: MinimizedContext
    ) -> AIFindingExplanation:
        """Generate targeted remediation advice based on issue title and minimized snippet."""
        if self.simulated_delay_ms > 0:
            await asyncio.sleep(self.simulated_delay_ms / 1000.0)

        title = context.issue_title.lower()
        finding_id = context.finding_id

        # Tailor explanation based on finding type
        if "eval" in title or "dynamic code" in title:
            root_cause = (
                "Dynamic code evaluation via `eval()` compiles and executes arbitrary string payloads "
                "in the current process context. If any portion of the input is controlled or influenced "
                "by untrusted data, attackers can execute arbitrary Python commands and compromise the system."
            )
            remediation = (
                "Replace `eval()` with `ast.literal_eval()` if evaluating Python literals (strings, numbers, dicts). "
                "For mathematical expressions, implement a dedicated parser (e.g. using `ast` or `mathjs`)."
            )
            secure_code = (
                "import ast\n"
                "# Safe alternative for literal expressions\n"
                "safe_data = ast.literal_eval(untrusted_string)"
            )
        elif "command injection" in title or "system" in title or "popen" in title:
            root_cause = (
                "Passing unvalidated or unsanitized user inputs to shell commands (`os.system` or `subprocess` with `shell=True`) "
                "allows command chaining via shell metacharacters (`;`, `|`, `&&`), enabling remote command execution."
            )
            remediation = (
                "Use `subprocess.run()` with a list of arguments and set `shell=False`. Validate all input strings against "
                "a strict allowlist before execution."
            )
            secure_code = (
                "import subprocess\n"
                "# Pass arguments as a discrete list without shell=True\n"
                "subprocess.run(['ping', '-c', '1', validated_target], shell=False, check=True)"
            )
        elif "sql injection" in title or "sql" in title:
            root_cause = (
                "Direct string formatting or interpolation in database queries allows attackers to break "
                "out of query data contexts and manipulate SQL execution logic."
            )
            remediation = (
                "Use parameterized queries (prepared statements) with placeholder parameters instead of string concatenation."
            )
            secure_code = (
                "# Parameterized query example\n"
                "cursor.execute('SELECT * FROM users WHERE role = ?', (role_param,))"
            )
        elif "secret" in title or "password" in title or "credential" in title or context.has_redactions:
            root_cause = (
                "Hardcoding credentials or API keys directly into source code exposes them to version control "
                "history and unauthorized viewers."
            )
            remediation = (
                "Store credentials in environment variables or a secure key vault (AWS Secrets Manager, HashiCorp Vault). "
                "Retrieve them at runtime using `os.getenv()`."
            )
            secure_code = (
                "import os\n"
                "API_KEY = os.environ.get('SECRET_API_KEY')\n"
                "if not API_KEY:\n"
                "    raise ValueError('SECRET_API_KEY environment variable is missing.')"
            )
        elif "deserialization" in title or "pickle" in title:
            root_cause = (
                "The `pickle` module is not secure against erroneous or maliciously constructed data. "
                "Unpickling untrusted data can instantiate arbitrary objects and execute arbitrary code via `__reduce__`."
            )
            remediation = (
                "Use safer serialization formats such as JSON, Protocol Buffers, or MessagePack for untrusted data streams."
            )
            secure_code = (
                "import json\n"
                "# Use JSON for safe data exchange\n"
                "data = json.loads(raw_json_string)"
            )
        elif "exception" in title or "except" in title:
            root_cause = (
                "Broad or empty `except:` clauses suppress critical errors and unexpected system failures silently, "
                "making debugging difficult and leaving the system in an indeterminate state."
            )
            remediation = (
                "Catch specific exception classes (e.g. `except (ValueError, KeyError):`) and log or handle the error explicitly."
            )
            secure_code = (
                "try:\n"
                "    perform_operation()\n"
                "except SpecificExpectedError as exc:\n"
                "    logger.error(f'Operation failed: {exc}')"
            )
        else:
            root_cause = (
                f"The static analyzer flagged {context.issue_title} at line {context.line_number}. "
                "This pattern violates secure coding best practices and increases regression or vulnerability risk."
            )
            remediation = (
                "Review the flagged line in context, isolate control flow branches, and refactor according to project security guidelines."
            )
            secure_code = (
                "# Refactored implementation with input validation\n"
                "def secure_handler(data):\n"
                "    if not is_valid(data):\n"
                "        raise ValueError('Invalid input')\n"
                "    return process(data)"
            )

        return AIFindingExplanation(
            finding_id=finding_id,
            issue_title=context.issue_title,
            severity=context.severity,
            line_number=context.line_number,
            root_cause_explanation=root_cause,
            remediation_advice=remediation,
            secure_code_example=secure_code,
            provider_used=self.provider_name,
            model_name=self.model_name,
            minimized_context=context
        )

    async def generate_remediation_json(
        self,
        context: MinimizedContext,
        finding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate complete tripartite remediation fields for MockLLMProvider."""
        if self.simulated_delay_ms > 0:
            await asyncio.sleep(self.simulated_delay_ms / 1000.0)

        title = context.issue_title.lower()
        confidence = float(finding.get("confidence", 0.5))

        if "eval" in title or "dynamic code" in title:
            dev_explanation = (
                f"The function `eval()` at line {context.line_number} parses and executes untrusted string inputs directly in Python's runtime engine."
            )
            why_it_matters = (
                "Dynamic code evaluation violates the principle of separation between code and data. It allows runtime injection of arbitrary bytecode."
            )
            potential_impact = (
                "Critical Remote Code Execution (RCE). An attacker can spawn reverse shells, exfiltrate file data, or compromise the entire host process."
            )
            remediation = (
                "Replace `eval()` with `ast.literal_eval()` if evaluating standard Python literals (dict, list, int, str), or write a dedicated expression evaluator."
            )
            safer_code = (
                "import ast\n\n"
                "# Safely evaluate literal structures without arbitrary code execution\n"
                "safe_result = ast.literal_eval(user_payload)"
            )
            steps = [
                "Remove all direct calls to `eval()` or `exec()`.",
                "Use `ast.literal_eval()` for literal data formats.",
                "Sanitize and validate string payloads against an expected schema."
            ]
        elif "command injection" in title or "system" in title or "popen" in title:
            dev_explanation = (
                f"Line {context.line_number} invokes a system shell command with unsanitized arguments, exposing shell metacharacters to injection."
            )
            why_it_matters = (
                "Shell execution via string concatenation allows attackers to append additional commands using `;`, `&&`, or `|`."
            )
            potential_impact = (
                "Command injection enabling unauthorized process spawning, system modification, or privilege escalation."
            )
            remediation = (
                "Use `subprocess.run()` with a list of discrete command arguments and `shell=False`. Validate all input strings strictly."
            )
            safer_code = (
                "import subprocess\n\n"
                "# Execute command safely without shell interpretation\n"
                "result = subprocess.run(['ping', '-c', '1', validated_host], shell=False, check=True, capture_output=True)"
            )
            steps = [
                "Set `shell=False` in all `subprocess` invocations.",
                "Pass command arguments as an array rather than a formatted string.",
                "Validate user inputs with a strict regex allowlist."
            ]
        elif "sql injection" in title or "sql" in title:
            dev_explanation = (
                f"Line {context.line_number} constructs a SQL query using string formatting or interpolation instead of parameterized placeholders."
            )
            why_it_matters = (
                "Direct string insertion in SQL statements allows attackers to alter query logic, bypassing authentication or dumping tables."
            )
            potential_impact = (
                "Complete database compromise, unauthorized data extraction, or record deletion."
            )
            remediation = (
                "Use parameterized queries with bound placeholders (`?` or `%s` depending on driver) so input data is never treated as SQL instructions."
            )
            safer_code = (
                "# Parameterized query prevents SQL injection\n"
                "cursor.execute('SELECT id, username, email FROM users WHERE id = ?', (user_id,))"
            )
            steps = [
                "Replace string formatting (`%`, `.format()`, f-strings) in SQL queries with parameter placeholders.",
                "Pass query variables as a tuple to `cursor.execute(query, params)`.",
                "Use an ORM or query builder with automatic parameter binding."
            ]
        elif "secret" in title or "password" in title or context.has_redactions:
            dev_explanation = (
                f"Line {context.line_number} contains hardcoded credential tokens in source code."
            )
            why_it_matters = (
                "Hardcoded credentials in code repositories persist indefinitely in version control history and can be leaked to unauthorized parties."
            )
            potential_impact = (
                "Unauthorized API access, cloud infrastructure compromise, and data leakage."
            )
            remediation = (
                "Store sensitive credentials in secure environment variables or a secret vault, loading them dynamically at runtime."
            )
            safer_code = (
                "import os\n\n"
                "# Retrieve sensitive tokens from runtime environment\n"
                "SECRET_TOKEN = os.environ.get('API_SECRET_TOKEN')\n"
                "if not SECRET_TOKEN:\n"
                "    raise RuntimeError('Missing API_SECRET_TOKEN environment variable')"
            )
            steps = [
                "Revoke and rotate the exposed credential immediately.",
                "Store credentials in `.env` files (excluded via `.gitignore`) or a secret manager.",
                "Access secrets using `os.getenv()` or secret manager SDKs."
            ]
        else:
            dev_explanation = (
                f"Static analysis identified {context.issue_title} at line {context.line_number}."
            )
            why_it_matters = (
                "This pattern violates established secure coding standards and introduces quality, error handling, or security risks."
            )
            potential_impact = (
                "Elevated vulnerability propensity, regression bugs, or maintenance overhead."
            )
            remediation = (
                "Review the flagged line in the minimized context window and refactor using safe standard library functions."
            )
            safer_code = (
                "# Refactored implementation with input validation\n"
                "def process_safely(data):\n"
                "    if not data:\n"
                "        return None\n"
                "    return transform(data)"
            )
            steps = [
                "Inspect the flagged AST node at the indicated line number.",
                "Refactor using explicit types and input validation.",
                "Verify behavior with automated test cases."
            ]

        confidence_stmt = f"High confidence: Verified direct static call at line {context.line_number} (Analyzer confidence: {confidence:.2f})."

        return {
            "developer_explanation": dev_explanation,
            "why_it_matters": why_it_matters,
            "potential_impact": potential_impact,
            "recommended_remediation": remediation,
            "safer_code_example": safer_code,
            "confidence_statement": confidence_stmt,
            "remediation_steps": steps
        }

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "OPERATIONAL",
            "provider": self.provider_name,
            "model": self.model_name,
            "endpoint_url": "memory://offline_mock",
            "air_gapped": True,
            "privacy_score": 100,
            "latency_ms": 0.5,
            "diagnostic_message": "Deterministic offline mock engine active. Guaranteed zero network egress."
        }
