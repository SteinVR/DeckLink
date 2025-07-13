# Agent Protocol & Directives

## 1. Mission

Autonomously implement or improve features while keeping the codebase healthy, tested and aligned with project conventions. Follow this playbook unless explicitly overridden in the current task.

---

## 2. Pre-Task Checklist

Before beginning any work, you MUST perform the following steps:
1.  **Review Architecture:** Read the `ARCHITECTURE.md` file in its entirety to understand the project's structure, components, and conventions.
2.  **Review Tasks:** Read the `TASK.md` file to understand the current objectives.

---

## 3. The Development Cycle (Plan-then-Code)

This is your mandatory, non-negotiable workflow for every task.

1.  **Select Tasks:** Identify the tasks in `TASK.md` that is not marked as done: `X`.
2.  **Create Implementation Plan:** Propose a detailed, step-by-step implementation plan. This plan is your primary output for the first phase. It MUST include:
    -   A list of all files you will create or modify.
    -   The definitions of new functions, classes, or methods you will add.
    -   A clear description of the tests (both unit and E2E) you will write to verify the functionality.
3.  **Await Approval:** **STOP** all implementation work. Submit the plan for human review and wait for an explicit "approved" or "proceed" command.
4.  **Execute:** Once the plan is approved, implement the code and tests exactly as described in the plan.
5.  **Verify:** Run all tests within the provided environment (e.g., via Docker command) to ensure your changes are correct and have not introduced any regressions.
6.  **Submit Pull Request:** Once all tests pass, create a Pull Request. The description must include a link to the task and the approved implementation plan.
7.  **Update Task List:** After the Pull Request is merged by the human, mark the tasks as complete by prepending `X` in `TASK.md`.

---

## 4. Coding Principles & Practices

These rules govern the quality of the code you write.

-   **Simplicity:** Always prefer simple, clear, and maintainable solutions.
-   **Consistency:** Strictly adhere to the existing code style, formatting, and architectural patterns of the project.
-   **DRY (Don't Repeat Yourself):** Before writing new code, search the codebase for existing functionality that can be reused.
-   **Focused Changes:** Only modify code that is directly relevant to the assigned task. Do not perform large-scale refactoring unless explicitly instructed.
-   **Naming Conventions:** Use clear, descriptive, and consistent names for all variables, functions, classes, and files.
-   **Documentation:** Write clear, complete docstrings (using the project's specified format) for all public functions, methods, and classes. Avoid unnecessary inline comments for obvious code.
-   **Error Handling:** Implement robust error handling using try-except blocks for operations that can fail (e.g., I/O, network requests).
*   **Memory:** Use Agent Memory Protocol.
---

## 5. Testing Mandate

**Code without tests is considered incomplete and will be rejected.**

-   **Unit Tests:** All new business logic (functions, classes) MUST be accompanied by corresponding unit tests.
-   **E2E Tests:** All new features that impact a user workflow MUST be covered by an end-to-end test.
-   **CI is Law:** A task is only complete when the Pull Request passes all checks in the CI pipeline.

---

## 6. Agent Memory Protocol (AICODE Prefixes)

To maintain context and communicate effectively, you will use special prefixes in code comments. You must search for these prefixes before working on a file.

-   `AICODE-NOTE: [message]`
    -   **Purpose:** To leave a note for your future self or other agents explaining complex logic, design choices, or trade-offs.
    -   **Example:** `// AICODE-NOTE: This regex handles OSC escape sequences, which is a core part of the login overlay.`

-   `AICODE-TODO: [task]`
    -   **Purpose:** To break down a complex implementation into smaller, manageable sub-tasks for yourself within a single work session.
    -   **Example:** `// AICODE-TODO: Refactor this into a separate utility function after getting the main logic to pass tests.`

-   `AICODE-ASK: [question]`
    -   **Purpose:** To ask a clarifying question to the human supervisor when you encounter ambiguity that blocks your work.
    -   **Action:** When you write an `AICODE-ASK` comment, you must halt work on that specific part of the implementation and report the question.
	    -   **Example:** `// AICODE-ASK: The spec is unclear if this operation should be atomic. Should I implement a transaction lock?`