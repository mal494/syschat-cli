# Technology Stack

## Core Language & Runtime
- **Python:** The primary development language for the CLI, chosen for its extensive ecosystem of AI and system administration libraries.

## Key Dependencies
- **requests:** Handles communication with both local (Ollama) and cloud-based (OpenAI) LLM APIs.
- **python-dotenv:** Manages configuration and secrets via `.env` files.

## AI Infrastructure
- **Model Agnostic Support:**
    - **Ollama:** Primary local provider for on-premise, secure inference.
    - **OpenAI:** Secondary cloud provider for enhanced reasoning capabilities when configured.
