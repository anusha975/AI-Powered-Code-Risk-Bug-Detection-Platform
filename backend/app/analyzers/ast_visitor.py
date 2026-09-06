"""
Python AST Static Code Analysis Engine.
Parses and traverses Python source code using Abstract Syntax Trees (ast.NodeVisitor)
without executing the code under analysis.
"""

import ast
from typing import List, Optional, Any
from app.analyzers.base import BaseAnalyzer
from app.schemas.analysis import NormalizedFinding, FindingSeverity, FindingCategory


class PythonASTSecurityVisitor(ast.NodeVisitor):
    """AST Visitor that inspects Python AST nodes for security and code quality vulnerabilities."""

    def __init__(self, filename: str, lines: List[str]):
        super().__init__()
        self.filename = filename
        self.lines = lines
        self.findings: List[NormalizedFinding] = []
        self._current_nesting_depth = 0

    def _get_snippet(self, node: ast.AST) -> str:
        """Extract source code line corresponding to an AST node."""
        line_no = getattr(node, "lineno", 1)
        if 1 <= line_no <= len(self.lines):
            return self.lines[line_no - 1].strip()
        return "<code context unavailable>"

    # =========================================================================
    # 1. Call Expressions (Dangerous Functions, Injections, Deserialization)
    # =========================================================================
    def visit_Call(self, node: ast.Call) -> None:
        func_name = self._get_call_name(node.func)

        # 1.1 Dangerous Code Execution Functions (eval, exec, compile)
        if func_name == "eval":
            self.findings.append(
                NormalizedFinding(
                    issue_id="AST-SEC-EVAL-001",
                    title="Use of dangerous dynamic eval() function",
                    category=FindingCategory.SECURITY.value,
                    severity=FindingSeverity.CRITICAL.value,
                    confidence=0.95,
                    file=self.filename,
                    line_number=getattr(node, "lineno", 1),
                    code_snippet=self._get_snippet(node),
                    recommendation="Avoid eval(). Use ast.literal_eval() for safe literal evaluation or write specific parsing logic.",
                    analyzer="ast_analyzer"
                )
            )
        elif func_name == "exec":
            self.findings.append(
                NormalizedFinding(
                    issue_id="AST-SEC-EXEC-002",
                    title="Use of arbitrary code execution function exec()",
                    category=FindingCategory.SECURITY.value,
                    severity=FindingSeverity.CRITICAL.value,
                    confidence=0.95,
                    file=self.filename,
                    line_number=getattr(node, "lineno", 1),
                    code_snippet=self._get_snippet(node),
                    recommendation="Remove exec(). Dynamic code execution introduces severe remote code execution vulnerabilities.",
                    analyzer="ast_analyzer"
                )
            )
        elif func_name == "compile":
            self.findings.append(
                NormalizedFinding(
                    issue_id="AST-SEC-COMP-003",
                    title="Dynamic code compilation via compile()",
                    category=FindingCategory.SECURITY.value,
                    severity=FindingSeverity.MEDIUM.value,
                    confidence=0.85,
                    file=self.filename,
                    line_number=getattr(node, "lineno", 1),
                    code_snippet=self._get_snippet(node),
                    recommendation="Ensure compiled code inputs originate strictly from trusted internal constants.",
                    analyzer="ast_analyzer"
                )
            )

        # 1.2 Command Injection (os.system, os.popen, subprocess with shell=True)
        if func_name in ("os.system", "os.popen", "os.spawnlp", "os.spawnlpe"):
            self.findings.append(
                NormalizedFinding(
                    issue_id="AST-CMD-OS-001",
                    title=f"Potential command injection via {func_name}()",
                    category=FindingCategory.SECURITY.value,
                    severity=FindingSeverity.CRITICAL.value,
                    confidence=0.92,
                    file=self.filename,
                    line_number=getattr(node, "lineno", 1),
                    code_snippet=self._get_snippet(node),
                    recommendation="Avoid os.system(). Use subprocess.run() with shell=False and pass arguments as a structured list.",
                    analyzer="ast_analyzer"
                )
            )
        elif func_name and func_name.startswith("subprocess."):
            # Check for shell=True keyword argument
            for kw in node.keywords:
                if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    self.findings.append(
                        NormalizedFinding(
                            issue_id="AST-CMD-SUBP-002",
                            title=f"Subprocess invoked with shell=True ({func_name})",
                            category=FindingCategory.SECURITY.value,
                            severity=FindingSeverity.CRITICAL.value,
                            confidence=0.95,
                            file=self.filename,
                            line_number=getattr(node, "lineno", 1),
                            code_snippet=self._get_snippet(node),
                            recommendation="Set shell=False and pass arguments as a list of strings [\"cmd\", \"arg1\", ...] to prevent shell injection.",
                            analyzer="ast_analyzer"
                        )
                    )

        # 1.3 SQL Injection Heuristics (execute with formatted / concatenated string)
        if func_name and (func_name.endswith(".execute") or func_name.endswith(".executemany") or func_name == "execute"):
            if node.args:
                first_arg = node.args[0]
                is_sql_injection_risk = False
                
                # Check f-string in SQL query: cursor.execute(f"SELECT ...")
                if isinstance(first_arg, ast.JoinedStr):
                    is_sql_injection_risk = True
                # Check % formatting: cursor.execute("SELECT ..." % var)
                elif isinstance(first_arg, ast.BinOp) and isinstance(first_arg.op, ast.Mod):
                    is_sql_injection_risk = True
                # Check string concatenation: cursor.execute("SELECT ..." + var)
                elif isinstance(first_arg, ast.BinOp) and isinstance(first_arg.op, ast.Add):
                    is_sql_injection_risk = True
                # Check .format() call: cursor.execute("SELECT ...".format(...))
                elif isinstance(first_arg, ast.Call) and isinstance(first_arg.func, ast.Attribute) and first_arg.func.attr == "format":
                    is_sql_injection_risk = True

                if is_sql_injection_risk:
                    self.findings.append(
                        NormalizedFinding(
                            issue_id="AST-SQL-INJ-001",
                            title="Potential SQL Injection pattern via formatted query string",
                            category=FindingCategory.SECURITY.value,
                            severity=FindingSeverity.HIGH.value,
                            confidence=0.90,
                            file=self.filename,
                            line_number=getattr(node, "lineno", 1),
                            code_snippet=self._get_snippet(node),
                            recommendation="Use parameterized queries with bind variables (e.g. cursor.execute('SELECT * FROM tbl WHERE id = %s', (id,))) instead of string interpolation.",
                            analyzer="ast_analyzer"
                        )
                    )

        # 1.4 Unsafe Deserialization (pickle, marshal, yaml.load)
        if func_name in ("pickle.loads", "pickle.load", "_pickle.loads", "_pickle.load"):
            self.findings.append(
                NormalizedFinding(
                    issue_id="AST-DESER-PCK-001",
                    title=f"Unsafe deserialization using {func_name}()",
                    category=FindingCategory.SECURITY.value,
                    severity=FindingSeverity.CRITICAL.value,
                    confidence=0.95,
                    file=self.filename,
                    line_number=getattr(node, "lineno", 1),
                    code_snippet=self._get_snippet(node),
                    recommendation="Never unpickle untrusted data. Use safer serialization formats such as JSON or Protocol Buffers.",
                    analyzer="ast_analyzer"
                )
            )
        elif func_name in ("marshal.loads", "marshal.load"):
            self.findings.append(
                NormalizedFinding(
                    issue_id="AST-DESER-MSH-002",
                    title="Unsafe deserialization via marshal",
                    category=FindingCategory.SECURITY.value,
                    severity=FindingSeverity.HIGH.value,
                    confidence=0.90,
                    file=self.filename,
                    line_number=getattr(node, "lineno", 1),
                    code_snippet=self._get_snippet(node),
                    recommendation="The marshal module is not intended to be secure against erroneous or maliciously constructed data.",
                    analyzer="ast_analyzer"
                )
            )
        elif func_name in ("yaml.load", "yaml.unsafe_load"):
            has_safe_loader = False
            for kw in node.keywords:
                if kw.arg == "Loader":
                    loader_name = self._get_call_name(kw.value)
                    if loader_name in ("yaml.SafeLoader", "SafeLoader", "yaml.CSafeLoader"):
                        has_safe_loader = True
            
            if not has_safe_loader and func_name == "yaml.load":
                self.findings.append(
                    NormalizedFinding(
                        issue_id="AST-DESER-YML-003",
                        title="Unsafe PyYAML load() without SafeLoader",
                        category=FindingCategory.SECURITY.value,
                        severity=FindingSeverity.HIGH.value,
                        confidence=0.92,
                        file=self.filename,
                        line_number=getattr(node, "lineno", 1),
                        code_snippet=self._get_snippet(node),
                        recommendation="Use yaml.safe_load() or specify Loader=yaml.SafeLoader to prevent arbitrary Python object execution.",
                        analyzer="ast_analyzer"
                    )
                )

        # 1.5 Weak Cryptographic Hashes (MD5, SHA-1)
        if func_name in ("hashlib.md5", "md5"):
            self.findings.append(
                NormalizedFinding(
                    issue_id="AST-CRYPTO-MD5-001",
                    title="Use of broken cryptographic hash function MD5",
                    category=FindingCategory.SECURITY.value,
                    severity=FindingSeverity.MEDIUM.value,
                    confidence=0.90,
                    file=self.filename,
                    line_number=getattr(node, "lineno", 1),
                    code_snippet=self._get_snippet(node),
                    recommendation="MD5 is cryptographically broken and prone to collision attacks. Use SHA-256 (hashlib.sha256) or SHA-3.",
                    analyzer="ast_analyzer"
                )
            )
        elif func_name in ("hashlib.sha1", "sha1"):
            self.findings.append(
                NormalizedFinding(
                    issue_id="AST-CRYPTO-SHA1-002",
                    title="Use of weak cryptographic hash function SHA-1",
                    category=FindingCategory.SECURITY.value,
                    severity=FindingSeverity.MEDIUM.value,
                    confidence=0.90,
                    file=self.filename,
                    line_number=getattr(node, "lineno", 1),
                    code_snippet=self._get_snippet(node),
                    recommendation="SHA-1 is deprecated for security contexts. Upgrade to SHA-256 (hashlib.sha256) or SHA-3.",
                    analyzer="ast_analyzer"
                )
            )

        # 1.6 Insecure Configurations (ssl._create_unverified_context, tempfile.mktemp, app.run debug)
        if func_name == "ssl._create_unverified_context":
            self.findings.append(
                NormalizedFinding(
                    issue_id="AST-CFG-SSL-001",
                    title="SSL certificate verification explicitly disabled",
                    category=FindingCategory.INSECURE_CONFIG.value,
                    severity=FindingSeverity.HIGH.value,
                    confidence=0.95,
                    file=self.filename,
                    line_number=getattr(node, "lineno", 1),
                    code_snippet=self._get_snippet(node),
                    recommendation="Enable SSL/TLS certificate validation to protect against Man-in-the-Middle (MitM) attacks.",
                    analyzer="ast_analyzer"
                )
            )
        elif func_name == "tempfile.mktemp":
            self.findings.append(
                NormalizedFinding(
                    issue_id="AST-TMP-001",
                    title="Use of insecure tempfile.mktemp() (race condition vulnerability)",
                    category=FindingCategory.SECURITY.value,
                    severity=FindingSeverity.MEDIUM.value,
                    confidence=0.90,
                    file=self.filename,
                    line_number=getattr(node, "lineno", 1),
                    code_snippet=self._get_snippet(node),
                    recommendation="Use tempfile.NamedTemporaryFile() or tempfile.mkstemp() to prevent symlink/race-condition attacks.",
                    analyzer="ast_analyzer"
                )
            )
        elif func_name and func_name.endswith(".run") and ("app" in func_name or "server" in func_name):
            for kw in node.keywords:
                if kw.arg == "debug" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    self.findings.append(
                        NormalizedFinding(
                            issue_id="AST-CFG-DBG-002",
                            title="Web application executed with debug=True",
                            category=FindingCategory.INSECURE_CONFIG.value,
                            severity=FindingSeverity.MEDIUM.value,
                            confidence=0.88,
                            file=self.filename,
                            line_number=getattr(node, "lineno", 1),
                            code_snippet=self._get_snippet(node),
                            recommendation="Ensure debug mode is disabled (debug=False) in production to prevent interactive debugger and traceback leaks.",
                            analyzer="ast_analyzer"
                        )
                    )

        self.generic_visit(node)

    # =========================================================================
    # 2. Exception Handling (Broad & Empty Handlers)
    # =========================================================================
    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        handler_name = self._get_call_name(node.type) if node.type else "bare"
        line_no = getattr(node, "lineno", 1)

        # Check if empty exception handler (e.g. only contains 'pass')
        is_empty = False
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            is_empty = True
        elif len(node.body) == 1 and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
            is_empty = True

        if is_empty:
            self.findings.append(
                NormalizedFinding(
                    issue_id="AST-ERR-EMPTY-002",
                    title="Silent empty exception handler ('except: pass')",
                    category=FindingCategory.ERROR_HANDLING.value,
                    severity=FindingSeverity.MEDIUM.value,
                    confidence=0.95,
                    file=self.filename,
                    line_number=line_no,
                    code_snippet=self._get_snippet(node),
                    recommendation="Do not silently swallow exceptions with 'pass'. Log the error or handle specific exception classes.",
                    analyzer="ast_analyzer"
                )
            )
        elif handler_name in ("Exception", "BaseException", "bare"):
            self.findings.append(
                NormalizedFinding(
                    issue_id="AST-ERR-BROAD-001",
                    title=f"Overly broad exception clause ('except {handler_name}')",
                    category=FindingCategory.ERROR_HANDLING.value,
                    severity=FindingSeverity.LOW.value,
                    confidence=0.85,
                    file=self.filename,
                    line_number=line_no,
                    code_snippet=self._get_snippet(node),
                    recommendation="Catch specific exceptions (e.g. ValueError, KeyError, OSError) instead of catching all Exceptions.",
                    analyzer="ast_analyzer"
                )
            )

        self.generic_visit(node)

    # =========================================================================
    # 3. Suspicious Imports
    # =========================================================================
    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name in ("telnetlib", "ftplib", "pty"):
                self.findings.append(
                    NormalizedFinding(
                        issue_id="AST-IMP-SUSP-001",
                        title=f"Import of legacy or unencrypted protocol library '{alias.name}'",
                        category=FindingCategory.SECURITY.value,
                        severity=FindingSeverity.LOW.value,
                        confidence=0.85,
                        file=self.filename,
                        line_number=getattr(node, "lineno", 1),
                        code_snippet=self._get_snippet(node),
                        recommendation=f"The '{alias.name}' module uses plaintext unencrypted protocols. Consider modern encrypted alternatives (SSH, SFTP).",
                        analyzer="ast_analyzer"
                    )
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module in ("Crypto.Cipher", "cryptography.hazmat.primitives.ciphers"):
            for alias in node.names:
                if alias.name in ("DES", "ARC4", "Blowfish"):
                    self.findings.append(
                        NormalizedFinding(
                            issue_id="AST-CRYPTO-WEAK-003",
                            title=f"Import of weak/legacy cipher '{alias.name}'",
                            category=FindingCategory.SECURITY.value,
                            severity=FindingSeverity.HIGH.value,
                            confidence=0.92,
                            file=self.filename,
                            line_number=getattr(node, "lineno", 1),
                            code_snippet=self._get_snippet(node),
                            recommendation=f"Cipher '{alias.name}' is obsolete and vulnerable. Use AES-256-GCM or ChaCha20-Poly1305.",
                            analyzer="ast_analyzer"
                        )
                    )
        self.generic_visit(node)

    # =========================================================================
    # 4. Function Complexity & Deep Nesting
    # =========================================================================
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        # Calculate cyclomatic complexity
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.And, ast.Or, ast.ExceptHandler, ast.Assert)):
                complexity += 1

        if complexity > 10:
            self.findings.append(
                NormalizedFinding(
                    issue_id="AST-CPLX-FUNC-001",
                    title=f"Excessive function complexity (Cyclomatic Complexity = {complexity}) in '{node.name}'",
                    category=FindingCategory.COMPLEXITY.value,
                    severity=FindingSeverity.LOW.value,
                    confidence=0.85,
                    file=self.filename,
                    line_number=node.lineno,
                    code_snippet=self._get_snippet(node),
                    recommendation="Refactor this function into smaller, single-responsibility helper functions to reduce defect propensity.",
                    analyzer="ast_analyzer"
                )
            )

        self.generic_visit(node)

    def _track_nesting(self, node: ast.AST) -> None:
        self._current_nesting_depth += 1
        if self._current_nesting_depth >= 4:
            self.findings.append(
                NormalizedFinding(
                    issue_id="AST-NEST-DEEP-001",
                    title=f"Deeply nested control structure (nesting depth = {self._current_nesting_depth})",
                    category=FindingCategory.CODE_QUALITY.value,
                    severity=FindingSeverity.LOW.value,
                    confidence=0.90,
                    file=self.filename,
                    line_number=getattr(node, "lineno", 1),
                    code_snippet=self._get_snippet(node),
                    recommendation="Flatten deeply nested code using guard clauses, early returns, or helper functions.",
                    analyzer="ast_analyzer"
                )
            )

    def visit_If(self, node: ast.If) -> None:
        self._track_nesting(node)
        self.generic_visit(node)
        self._current_nesting_depth -= 1

    def visit_For(self, node: ast.For) -> None:
        self._track_nesting(node)
        self.generic_visit(node)
        self._current_nesting_depth -= 1

    def visit_While(self, node: ast.While) -> None:
        self._track_nesting(node)
        self.generic_visit(node)
        self._current_nesting_depth -= 1

    def _get_call_name(self, node: Any) -> Optional[str]:
        """Resolve dotted or direct function names from AST nodes."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value_name = self._get_call_name(node.value)
            return f"{value_name}.{node.attr}" if value_name else node.attr
        return None


class PythonASTAnalyzer(BaseAnalyzer):
    """AST-based static analyzer for Python."""

    analyzer_id = "ast_analyzer"
    name = "Python Abstract Syntax Tree Analyzer"
    supported_languages = ["python"]

    def analyze(self, code: str, filename: str = "snippet.py") -> List[NormalizedFinding]:
        """Parse source code into AST and run visitor inspections."""
        if not code or not code.strip():
            return []

        try:
            tree = ast.parse(code, filename=filename)
        except SyntaxError as exc:
            # Report syntax error gracefully as a code quality finding
            return [
                NormalizedFinding(
                    issue_id="AST-SYNTAX-ERROR-001",
                    title=f"Python Syntax Error: {exc.msg}",
                    category=FindingCategory.CODE_QUALITY.value,
                    severity=FindingSeverity.HIGH.value,
                    confidence=1.0,
                    file=filename,
                    line_number=exc.lineno or 1,
                    code_snippet=exc.text.strip() if exc.text else "<syntax error>",
                    recommendation="Fix Python syntax error before proceeding with deep security analysis.",
                    analyzer=self.analyzer_id
                )
            ]

        lines = code.splitlines()
        visitor = PythonASTSecurityVisitor(filename=filename, lines=lines)
        visitor.visit(tree)
        return visitor.findings
