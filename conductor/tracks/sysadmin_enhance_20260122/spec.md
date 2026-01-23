# Track Specification: Enhance SysChat for System Administrators

## 1. Overview
This track focuses on expanding SysChat's capabilities to better serve system administrators. The key additions include sophisticated log file parsing to pinpoint errors and summarize system events, and the ability to generate automation scripts (Bash/Python) based on the analysis of existing system files.

## 2. Goals
1.  **Log Analysis:** Implement logic to identify common log file formats and extract error/warning messages.
2.  **Error Summarization:** Use the LLM to provide high-level summaries of the extracted log events.
3.  **Script Generation:** Enable the LLM to propose Bash or Python scripts based on the context of analyzed configuration or log files.
4.  **Batch Resilience:** Ensure the tool can handle multiple files without crashing on individual failures.

## 3. User Stories
-   **As a SysAdmin**, I want to point SysChat at a log file so that I can quickly understand what errors occurred without reading thousands of lines.
-   **As a SysAdmin**, I want SysChat to suggest a fix or a cleanup script for the errors found in the logs.
-   **As a SysAdmin**, I want to scan a directory of config files and get a summary of their purpose.

## 4. Technical Requirements
-   **Log Parser:** Create a specialized module in `src/analyzer.py` or `src/log_parser.py` (new) to handle text-based log patterns.
-   **Prompt Engineering:** Update `src/main.py` (system prompt) to include instructions for script generation and log summarization.
-   **Error Handling:** Refactor file reading to log warnings instead of stopping, especially for batch operations (though batch mode is a future full feature, basic resilience is needed here).
-   **Safe Peeking:** Enforce the 10KB read limit strictly.

## 5. Non-Functional Requirements
-   **Performance:** Parsing should be efficient; only relevant chunks should be sent to the LLM.
-   **Safety:** No script should be executed automatically; only generated as text output.
