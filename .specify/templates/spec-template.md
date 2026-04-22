# Feature Specification: [FEATURE NAME]

**Feature Branch**: [BRANCH_NAME]
**Created**: [DATE]
**Status**: Draft
**Input**: User description: "[USER_DESCRIPTION]"

## Execution Flow (main)
```
1. Parse user description from Input
   → If empty: ERROR "No feature description provided"
2. Extract key concepts from description
   → Identify: actors, actions, data, constraints
3. For unclear aspects:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
   → If no clear user flow: ERROR "Cannot determine user scenarios"
5. Generate Functional Requirements
   → Each requirement must be testable
6. Identify Key Entities (if data involved)
7. Return: SUCCESS (spec ready for planning)
```

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
[Describe the main user journey in plain language]

### Acceptance Scenarios
1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

### Edge Cases
- What happens when [edge case 1]?
- What happens when [edge case 2]?

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST [capability]
- **FR-002**: System MUST [capability]
- **FR-003**: System MUST [capability]

### Key Entities *(include if feature involves data)*
- **[Entity Name]**: [Description and key attributes]

### Success Criteria *(mandatory)*
- [Measurable outcome 1]
- [Measurable outcome 2]

## Assumptions
- [Assumption 1]
- [Assumption 2]

## Dependencies
- [Dependency 1]

## Out of Scope
- [Item explicitly not included in this feature]
