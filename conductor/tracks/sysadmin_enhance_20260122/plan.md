# Implementation Plan - Enhance SysChat for System Administrators

## Phase 1: Log Parsing & Analysis Logic
- [x] Task: Create `src/log_parser.py` module. [commit: 6b3e1fc]
    - [ ] Create `src/log_parser.py` and define `parse_log_file(file_path, max_lines=50)` function.
    - [ ] Implement basic keyword scanning (ERROR, WARN, CRITICAL) to extract relevant lines.
    - [ ] Add unit tests in `tests/test_log_parser.py` for standard log formats.
- [x] Task: Integrate Log Parser into Analyzer. [commit: e20ff3e]
    - [ ] Update `src/analyzer.py` to import and use `parse_log_file`.
    - [ ] Modify `get_file_metadata` to detect if a file is likely a log file (via extension or content).
    - [ ] Update `tests/test_analyzer.py` to verify log detection integration.
- [x] Task: Conductor - User Manual Verification 'Log Parsing & Analysis Logic' (Protocol in workflow.md)

## Phase 2: LLM Prompt Engineering for SysAdmins
- [ ] Task: Refine System Prompt for Script Generation.
    - [ ] Modify `generate_system_prompt` in `src/main.py`.
    - [ ] Add explicit instructions: "If the user asks for a script, provide a complete, safe Bash or Python script block."
    - [ ] Add instructions for "Log Summarization" based on the extracted log lines.
- [ ] Task: Test LLM Response Quality.
    - [ ] Create a manual test script or use the CLI to verify `SysChat` produces valid scripts for simple prompts.
- [ ] Task: Conductor - User Manual Verification 'LLM Prompt Engineering for SysAdmins' (Protocol in workflow.md)

## Phase 3: Resilience & Safety Hardening
- [ ] Task: Enforce 10KB Limit & Error Resilience.
    - [ ] Review `read_file_safe` in `src/analyzer.py`. Ensure the 10KB limit is strict.
    - [ ] Ensure exceptions during file reading (e.g., locking issues) are caught, logged to stderr, and do not crash the app.
    - [ ] Add a test case in `tests/test_analyzer.py` for a mocked "locked" file.
- [ ] Task: Conductor - User Manual Verification 'Resilience & Safety Hardening' (Protocol in workflow.md)
