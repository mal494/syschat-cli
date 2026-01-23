# Plan: Agentic AI for Intelligent Desktop Automation (Integrated & Robust)

## Goal
Integrate an "Agentic Mode" into `syschat-cli` that allows users to perform desktop automation tasks using Vision-Language Models (VLMs). The agent will operate autonomously with world-class robustness, error handling, and observability.

## Context
This feature upgrades `syschat-cli` from a file analyzer to an active desktop agent. It uses an OODA Loop (Observe, Orient, Decide, Act) architecture, prioritized for autonomy and reliability across different screen resolutions.

## Architecture
1.  **Interface Layer**: CLI `--agent` mode.
2.  **Observation**: `mss` for high-speed, DPI-aware screen capture.
3.  **Cognition**: Multimodal LLM integration (text + image) with context management.
4.  **Action**: `src/desktop.py` wrapping `pyautogui` with coordinate normalization.
5.  **Control Plane**:
    -   **Fail-Safe**: `pyautogui.FAILSAFE = True`.
    -   **Resource Limits**: Max steps per task, timeout per action.
    -   **Retry Logic**: Exponential backoff for VLM errors or failed actions.
    -   **Observability**: Structured audit logs and visual debugging artifacts.

## Step-by-Step Implementation Plan

### Phase 1: Foundation, Safety & Dependencies
- [ ] **Update Requirements**: Add `mss`, `pyautogui`, `pillow` to `requirements.txt`.
- [ ] **Create `src/desktop.py`**:
    -   **Screen Capture**: `capture_screen()` returns compressed/resized base64 image.
    -   **DPI & Coordinates**: Implement logic to handle Windows high-DPI scaling and normalize coordinates (0-1000 scale) to support resolution independence.
    -   **Action Executor**: `execute_action(action_dict)` with:
        -   Validation (is the coordinate on screen?).
        -   Fail-safe check (mouse to corner).
        -   Retry logic (if action raises exception, try 1 more time).
- [ ] **Resource Limits**: Define constants `MAX_STEPS = 15`, `TIMEOUT_SECONDS = 30`.

### Phase 2: Multimodal Brain Upgrade
- [ ] **Update `src/brain.py`**:
    -   Modify `ask_llm` to accept `image_data`.
    -   **Retry Decorator**: Wrap API calls with retry logic for network/rate-limit errors.
    -   **Payload Construction**:
        -   **Ollama**: `{"images": [b64]}`.
        -   **OpenAI**: `{"type": "image_url", ...}`.
- [ ] **System Prompt**: Define robust JSON schema output for actions (`{"action": "CLICK", "x": 10, "y": 10}`) and mandate coordinate reasoning.

### Phase 3: The Robust Agentic Loop
- [ ] **Update `src/main.py`**:
    -   Add `--agent` argument.
    -   **Context Management**: Implement a sliding window for history (keep only last 3 screenshots to save tokens).
    -   **Implement `agent_loop()`**:
        -   **Structured Audit**: Write each step to `logs/agent_history.json`.
        -   **Visual Debugging**: Save `debug_step_N.png` with a red dot marking the intended click target.
        -   **Loop Logic**:
            1.  Check Resource Limits (Steps < MAX).
            2.  Capture & Process Screen.
            3.  Query Brain (with Retry).
            4.  Validate JSON Response (ensure schema compliance).
            5.  Execute Action (with Fail-Safe).
            6.  Verify (Optional: Check if screen changed?).
        -   **Error Handling**: Catch exceptions, log them, and decide whether to abort or retry.

### Phase 4: Testing & Verification
- [ ] **Unit Tests**:
    -   Test `execute_action` validation logic (e.g., negative coordinates).
    -   Test coordinate normalization math.
    -   Test `ask_llm` retry logic using mocks.
- [ ] **Manual Verification**:
    -   Test "Fail-Safe": Jerk mouse to corner during execution -> Ensure clean exit.
    -   Test "DPI Awareness": Verify accurate clicks on a scaled display.

## User Configuration
-   **Note**: User must ensure their `LLM_MODEL` (env var) supports vision (e.g., `llava`, `moondream`, `gpt-4o`).