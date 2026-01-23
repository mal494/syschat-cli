# Test Execution Plan - Agentic AI for Intelligent Desktop Automation

## 1. Unit Tests (Automated)
Execute the suite of unit tests to verify individual components.

- [x] `tests/test_desktop.py`: Verify coordinate normalization and action validation logic.
- [x] `tests/test_brain_retry.py`: Verify API retry mechanism.
- [x] `tests/test_brain_multimodal.py`: Verify payload construction for vision models.
- [x] `tests/test_main.py`: Verify system prompt construction logic.

**Result:** ALL TESTS PASSED.
Command: `.venv\Scripts\python.exe -m unittest discover tests`
Output: `Ran 21 tests in 0.156s - OK`

## 2. Manual Verification (QA)
Since this feature interacts with the physical desktop, some tests require manual execution.

- [ ] **Fail-Safe Mechanism** (Pending User Verification):
    1. Run the agent with a dummy task: `python src/main.py --agent "Click start"`
    2. Immediately jerk the mouse to the top-left corner (0, 0).
    3. Verify that the script aborts with a `pyautogui.FailSafeException`.

- [ ] **DPI Awareness** (Pending User Verification):
    1. On a High-DPI display (e.g., Windows at 150% scaling), run the agent.
    2. Provide a task that targets a specific known element (e.g., "Click the center of the screen").
    3. Verify that the mouse moves to the physical center, not an offset location.

- [ ] **Integration Test** (Pending User Verification):
    1. Run `python src/main.py --agent "Open Notepad and type 'Hello World'"`
    2. Observe the agent taking screenshots (check `logs/` for debug artifacts).
    3. Verify the agent successfully performs the actions.