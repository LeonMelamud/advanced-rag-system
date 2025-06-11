# ADVANCED RAG SYSTEM - BEST PRACTICES

## 🎯 CORE DEVELOPMENT PRINCIPLES - MANDATORY

### 🔄 DRY (Don't Repeat Yourself) - HIGHEST PRIORITY
**Never write the same code twice. Always extract common patterns.**

#### Implementation Guidelines:
- **Before writing ANY code:** Check if similar functionality exists
- **Extract immediately:** When you see duplication, extract to shared component
- **Use inheritance:** Create base classes for common functionality
- **Share configurations:** Use base config classes with inheritance
- **Reuse patterns:** API patterns, database models, validation logic
- **Document reusable components:** Make them discoverable for future use

#### Examples in Our System:
- ✅ `backend/Dockerfile.base` - Base Docker image for all services
- ✅ `backend/common/models.py` - Shared SQLAlchemy mixins and base classes
- ✅ `backend/common/config.py` - Base configuration classes
- ✅ `backend/common/api.py` - Shared API patterns and health routers
- ✅ `backend/common/auth.py` - Centralized authentication utilities

### 💎 KISS (Keep It Simple, Stupid) - HIGHEST PRIORITY
**Choose the simplest solution that works. Avoid unnecessary complexity.**

#### Implementation Guidelines:
- **Simple over clever:** Write clear, readable code over complex optimizations
- **Proven patterns:** Use well-established patterns and libraries
- **Minimal dependencies:** Only add dependencies that provide clear value
- **Clear naming:** Use descriptive names that explain purpose
- **Straightforward logic:** Avoid nested complexity and convoluted flows
- **Document complexity:** When complexity is necessary, document why

#### Examples in Our System:
- ✅ Simple health check patterns instead of complex monitoring
- ✅ Straightforward configuration inheritance over complex factory patterns
- ✅ Clear service separation over monolithic complexity
- ✅ Standard FastAPI patterns over custom frameworks

### 🏗️ REUSABILITY CHECKLIST - USE BEFORE EVERY IMPLEMENTATION
- [ ] **Duplication Check:** Does this functionality already exist?
- [ ] **Extraction Opportunity:** Can this be made reusable for other services?
- [ ] **Inheritance Opportunity:** Can this inherit from a base class?
- [ ] **Simplicity Check:** Is this the simplest approach that works?
- [ ] **Maintainability Check:** Will this be easy to understand in 6 months?
- [ ] **Documentation Check:** Is the reusable component properly documented?

## ARCHITECTURAL BEST PRACTICES

# Memory Bank System: Best Practices

This document provides best practices for effectively using the Cursor Memory Bank system, focusing on rule files and memory files. Following these guidelines will help maintain a structured workflow and ensure the system works optimally.

## Rule Files (`.cursor/rules/isolation_rules/`)

Rule files define the logic, flow, and specific instructions for each custom mode (VAN, PLAN, CREATIVE, IMPLEMENT). They are loaded Just-In-Time (JIT) based on the active mode.

**Best Practices:**

1.  **Understand JIT Loading:** Rules are isolated to specific modes and loaded only when that mode is active. This minimizes interference with standard Cursor usage. Don't expect rules from PLAN mode to be active when you're in IMPLEMENT mode unless explicitly loaded by the IMPLEMENT mode's instructions.
2.  **Modify with Caution:** Before editing existing rules, understand their purpose and how they fit into the mode's visual process map. Unintended changes can break the workflow. It's often better to create new, specialized rules if significant changes are needed.
3.  **Creating New Rules:**
    *   Follow the existing structure and naming conventions found in `isolation_rules/`.
    *   Place new rules in relevant subdirectories (e.g., `Core`, `Phases`, `LevelX`).
    *   Ensure your custom mode instructions (`custom_modes/*.md`) are updated to load your new rule files at the appropriate time using `read_file`.
    *   Keep rules focused on a specific aspect of the workflow.
4.  **Leverage Visual Maps:** The `.mdc` files in `visual-maps/` define the core flow for each mode. Refer to these maps (using Mermaid syntax) to understand the sequence of operations. Updates to the flow should ideally be reflected in these maps.
5.  **Modularity:** Design rules to be modular and reusable where possible. This makes the system easier to maintain and extend.
6.  **Version Control:** Treat the `.cursor/rules/` directory as code. Keep it under version control (e.g., Git) to track changes, revert if necessary, and collaborate if others use the system.

## Memory Files (`memory-bank/`)

Memory files store the state and context of your development process, allowing the AI to maintain persistence across different modes and sessions.

**Best Practices:**

1.  **`tasks.md` - The Single Source of Truth:**
    *   **Accuracy:** Keep this file meticulously updated. It's the primary reference for what needs to be done, complexity, and status.
    *   **Structure:** Maintain a clear structure (e.g., Project Requirements, Current Tasks with Complexity Levels, Completed Tasks). Use checkboxes `[ ]` and `[x]` for status.
    *   **Clarity:** Write task descriptions clearly and concisely. Link to relevant issues or specs if applicable.
2.  **`activeContext.md` - Current Focus:**
    *   This file should reflect the *current* specific task or component being worked on within the active mode.
    *   Ensure the AI updates this file accurately as you transition between sub-tasks or phases within a mode.
3.  **`progress.md` - Implementation Status:**
    *   Track the *detailed* progress of the *current* implementation phase here.
    *   Include notes on challenges encountered, solutions tried, and specific code sections modified.
    *   Reference commit hashes or branch names if helpful for tracking code changes related to the progress notes.
4.  **`creative-*.md` - Design Decisions:**
    *   Use descriptive file names (e.g., `creative-payment-processing-api.md`).
    *   Follow the structured format outlined in the CREATIVE mode instructions (requirements, options analysis, recommendation, guidelines).
    *   Clearly articulate the *why* behind design choices. This documentation is invaluable for future reference.
5.  **Regular Review:** Periodically review all memory files (`tasks.md`, `activeContext.md`, `progress.md`, `creative-*.md`) to ensure they accurately reflect the project state. Correct any inconsistencies.
6.  **Version Control:** Include the `memory-bank/` directory in your project's version control. This captures the evolution of tasks, decisions, and progress alongside your code. *Self-correction: Since these files are now in a global location, consider how best to manage their versions. Perhaps a separate Git repository for your MCP/tools directory?*

## General Workflow

1.  **Respect the Sequence:** Adhere to the intended VAN -> PLAN -> CREATIVE -> IMPLEMENT workflow for non-trivial tasks. Skipping modes (especially PLAN and CREATIVE for complex tasks) undermines the system's value.
2.  **Use Mode Commands:** Explicitly type `VAN`, `PLAN`, `CREATIVE`, `IMPLEMENT`, or `QA` to activate the corresponding mode's primary workflow and ensure the correct rules and visual maps are loaded.
3.  **Validate Setup:** Ensure the custom modes in the Cursor UI are configured *exactly* as per the README, including the correct tools and the *full* instruction content pasted into "Advanced options". Incorrect setup is the most common cause of issues.
4.  **Tailor Complexity:** Adjust how you define Level 1-4 tasks based on the specifics of your projects (e.g., within `onplanhealth-main`, a change in the core billing engine might be Level 4, while a UI tweak in a settings page might be Level 1).
5.  **Keep it Global (or Project-Specific):** You've placed this in `/Users/Leon.Melamud/Documents/Cline/MCP/`. Decide if you want one Memory Bank for all projects or if you prefer project-specific memory banks (which would involve copying this setup into each project's `.cursor/` or a designated project folder). The current setup is global. 