# TODO: Agentic AI for Intelligent Desktop Automation

## Phase 1: Foundation, Safety & Dependencies
- [x] Update `requirements.txt` to include `mss`, `pyautogui`, and `pillow` [dependencies]
- [x] Create `src/desktop.py` module [core]
  - [x] Implement `capture_screen()` function [vision]
    - [x] Return compressed/resized base64 image
  - [x] Implement DPI awareness logic [os-integration]
    - [x] Handle Windows high-DPI scaling
  - [x] Implement coordinate normalization logic (0-1000 scale) [logic]
  - [x] Implement `execute_action(action_dict)` function [action]
    - [x] Add input validation (coordinate bounds)
    - [x] Implement fail-safe check (mouse to corner)
    - [x] Implement retry logic for failed actions
- [x] Define resource limit constants (`MAX_STEPS`, `TIMEOUT_SECONDS`) [config]

## Phase 2: Multimodal Brain Upgrade
- [x] Update `src/brain.py` [ai-integration]
  - [x] Modify `ask_llm` signature to accept `image_data` argument
  - [x] Implement retry decorator for API calls (network/rate-limit handling)
  - [x] Implement payload construction logic
    - [x] Support Ollama image format (`{"images": [b64]}`)
    - [x] Support OpenAI image format (`{"type": "image_url", ...}`)
- [x] Design and implement robust system prompt [prompt-engineering]
  - [x] Define JSON schema for output (`{"action": "CLICK", "x": 10, "y": 10}`)
  - [x] Mandate coordinate reasoning in instructions

## Phase 3: The Robust Agentic Loop
- [x] Update `src/main.py` [cli]
  - [x] Add `--agent` CLI argument
  - [x] Implement context management (sliding window for history) [logic]
  - [x] Implement `agent_loop()` function [core]
    - [x] Implement structured audit logging (`logs/agent_history.json`) [logging]
    - [x] Implement visual debugging (save annotated `debug_step_N.png`) [debugging]
    - [x] Implement main loop logic
      - [x] Check resource limits
      - [x] Capture and process screen
      - [x] Query brain (with retry)
      - [x] Validate JSON response (schema compliance)
      - [x] Execute action (with fail-safe)
      - [x] Verify (optional screen change check)
    - [x] Implement centralized error handling (abort vs retry decisions)

## Phase 4: Testing & Verification
- [x] Implement unit tests [testing]
  - [x] Test `execute_action` validation logic (e.g., negative coordinates)
  - [x] Test coordinate normalization math
  - [x] Test `ask_llm` retry logic using mocks
- [ ] Perform manual verification [qa]
  - [ ] Test "Fail-Safe" mechanism (mouse interrupt)
  - [ ] Test "DPI Awareness" on scaled display