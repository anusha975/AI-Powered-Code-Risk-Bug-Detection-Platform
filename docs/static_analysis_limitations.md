# Static Code Analysis: Technical Capabilities & Limitations

## Overview

The **Local Static Code Analysis Engine** inspects source code purely as static text and Abstract Syntax Tree (AST) structures. It operates 100% locally on the host machine without executing source code or transmitting code to external cloud/LLM endpoints.

While static analysis provides an indispensable first line of defense, **no static analysis tool can claim 100% detection accuracy**. This document defines the theoretical and practical boundaries of static code analysis.

---

## Theoretical Foundations & Rice's Theorem

In computer science, **Rice's Theorem (1953)** establishes that:
> *Any non-trivial semantic property of a universal computing program is undecidable.*

Consequently, a static analyzer cannot mathematically determine with 100% certainty whether a given function will produce a specific runtime effect (such as an exploit or dynamic injection) without running the code.

---

## Key Limitations

### 1. False Positives (False Alarms)
- **Context Blindness**: A static rule flagging `os.system("clear")` or `eval("1 + 1")` in a local unit test script may flag a `CRITICAL` or `HIGH` warning even if the input is completely hardcoded and unexploitable by external users.
- **Defensive Wrappers**: If an application sanitizes user input through custom validation functions before passing it to `cursor.execute()`, standard AST inspection may still flag the concatenated query because it cannot prove the custom sanitizer's efficacy.

### 2. False Negatives (Undetected Vulnerabilities)
- **Dynamic Reflection & Metaprogramming**:
  ```python
  # Static analyzer may not resolve dynamic function invocations:
  fn_name = "sys" + "tem"
  getattr(__import__("o" + "s"), fn_name)("rm -rf /")
  ```
- **Complex Inter-Module Dataflow**: When a malicious payload enters Module A, flows through 5 classes, a database, and executes in Module B, simple AST analysis without full inter-procedural symbolic execution may fail to trace the taint.
- **Third-Party Dependency Vulnerabilities**: Static analysis on user code cannot guarantee safety within uninspected compiled C extensions or upstream packages.

### 3. Dynamic Runtime State Blindness
- Static analyzers cannot inspect environment variables, production configuration files, network socket states, or database table contents at runtime.

---

## Capabilities & High-Confidence Strengths

Despite theoretical limits, static AST and rule-based SAST provide immense value:
1. **Zero Execution Safety**: Code is never executed, preventing malicious code from compromising the scanner.
2. **Instant Local Feedback**: Sub-second analysis feedback during development.
3. **High-Confidence Bug & Smells**: Catches empty exception handlers (`except: pass`), broken hashing algorithms (`md5`), known dangerous functions (`eval`, `exec`, `pickle`), and obvious injection patterns.
4. **Zero Cloud Leakage**: Full operational capability in air-gapped environments without AI dependencies.

---

## Summary Matrix

| Issue Type | Static AST Detection Confidence | Note |
| :--- | :--- | :--- |
| Dangerous Functions (`eval`, `exec`) | **95% (High)** | Immediate AST Call node detection |
| Command Injection (`shell=True`, `os.system`) | **92-95% (High)** | Catches direct shell execution calls |
| Unsafe Deserialization (`pickle.loads`) | **95% (High)** | Detects unpickling patterns |
| SQL Injection (F-string in `.execute()`) | **85-90% (High)** | Identifies dynamic query string interpolation |
| Broken Hashes (`md5`, `sha1`) | **90% (High)** | Detects legacy cryptographic primitives |
| Empty Exception Handlers (`except: pass`) | **95% (High)** | Direct AST block inspection |
| Deeply Nested Code ($\ge 4$ levels) | **90% (High)** | Direct AST structure depth measurement |
| Indirect Dynamic Reflection (`getattr(...)`) | **Low (Limitation)** | Requires dynamic taint tracing / runtime DAST |
