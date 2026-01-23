# Product Guidelines

## Tone and Voice
- **Technical, Concise, and Action-Oriented:** The assistant's voice is professional and direct, prioritizing technical accuracy and actionable outputs. It focuses on providing specific script snippets and "ready-to-run" commands for the user.

## Operational Principles
- **Batch Processing Resilience:** When processing multiple files, the system maintains progress despite individual file failures. It logs specific warnings for unreadable files while continuing to analyze the remaining set.

## Safety and Security Standards
- **Safe Content Peeking:** To ensure system stability and prevent memory exhaustion, content retrieval is strictly limited by a maximum byte count (e.g., 10KB per file) before being processed by the LLM.
