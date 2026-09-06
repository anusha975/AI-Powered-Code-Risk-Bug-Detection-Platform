# AI Developer Explanation & Remediation Engine Specification

**Module:** Module 7: AI Developer Explanation & Remediation Engine  
**Status:** Active  
**Core Principles:** Static Analysis is the Authoritative Detector, Tripartite Epistemic Segregation, Strict Anti-Hallucination Boundaries, and Guaranteed Non-Execution of Model Outputs.

---

## 1. Grounding in Authoritative Static Analysis

A fundamental design constraint of this platform is that **the AI layer does NOT discover arbitrary vulnerabilities independently**. 

Unconstrained LLM vulnerability discovery produces excessive false positives, hallucinates non-existent security flaws, and claims artificial certainty. In this architecture:
1. **Local Static Code Analysis (Python AST Visitor & Bandit SAST)** serves as the sole, authoritative source of truth for issue identification.
2. The AI layer acts strictly as an **epistemic interpreter and remediation assistant**, transforming raw static diagnostic metrics into actionable engineering guidance.

```
+-----------------------------------------------------------------------------------+
|                        AUTHORITATIVE STATIC DISCOVERY                             |
|          (Python AST NodeVisitor & Bandit isolated SAST runner)                   |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                  PRIVACY-MINIMIZED CONTEXT WINDOW (±4 lines)                      |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                      TRIPARTITE EPISTEMIC REASONING ENGINE                        |
|                                                                                   |
|  [TIER 1: DETECTED FACT]    [TIER 2: AI INTERPRETATION]   [TIER 3: RECOMMENDATION]|
|  • Local analyzer truth     • Plain-English summary       • Actionable steps      |
|  • Tool & rule ID           • Why it matters              • Safer code example    |
|  • Line & raw snippet       • Potential runtime impact    • Safe refactoring plan |
|  • Detection confidence     • Uncertainty statement                               |
+-----------------------------------------------------------------------------------+
```

---

## 2. The Tripartite Epistemic Model

Every remediation record emitted by the engine separates facts, interpretations, and recommendations:

### Tier 1: `DETECTED_FACT`
- **What it is:** Immutable diagnostic observations verified by deterministic AST parsing or Bandit rules.
- **Inviolability:** The AI model is strictly prohibited from mutating line numbers, analyzer IDs, or code tokens.
- **Fields:** `analyzer`, `issue_id`, `title`, `category`, `severity`, `line_number`, `code_snippet`, `detection_confidence`.

### Tier 2: `AI_INTERPRETATION`
- **What it is:** The AI model's contextual reasoning regarding why the pattern exists, why it matters, and how it could be exploited.
- **Anti-Overclaiming Rule:** The response must explicitly articulate an uncertainty boundary if context is limited.
- **Fields:** `developer_explanation`, `why_it_matters`, `potential_impact`, `confidence_statement`, `is_insufficient_evidence`.

### Tier 3: `RECOMMENDATION`
- **What it is:** Actionable refactoring guidance and validated safer replacement code.
- **Non-Execution Safety:** The replacement snippet is sanitized for display and **never executed**.
- **Fields:** `recommended_remediation`, `safer_code_example`, `remediation_steps`.

---

## 3. Insufficient Evidence Fallback Protocol

> [!IMPORTANT]
> **Anti-Hallucination Guarantee:**
> If the static analyzer confidence is below threshold ($< 0.40$), or if the model cannot establish clear evidence of vulnerability reach in the context window, the engine returns:
> 
> `developer_explanation`: **"Insufficient evidence for a reliable explanation."**
> 
> The engine sets `is_insufficient_evidence = true` and directs the developer to perform manual inspection rather than presenting fabricated certainty.

---

## 4. Response Validation & Error Resilience

The `validate_and_parse_llm_response` engine provides multi-layered defenses:
1. **Malformed JSON Recovery**: Strips markdown fences (````json ... ````) and performs regex boundary extraction.
2. **Missing Key Defaults**: Injects fallback diagnostic strings if model omitted individual fields.
3. **Control Character Stripping**: Removes non-printable ANSI/terminal control characters from code snippets.
4. **Guaranteed Non-Execution**: Code examples are returned as immutable text strings.
