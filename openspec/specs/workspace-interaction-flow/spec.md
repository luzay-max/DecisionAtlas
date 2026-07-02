## Purpose

Define the role-aware, workspace-centered frontend interaction flow for DecisionAtlas so users can move from setup to review, discovery, drift, evidence, and decision detail without losing context.

## Requirements

### Requirement: Role-aware landing flow
The frontend SHALL route authenticated users toward the most relevant next action for their role and current workspace context.

#### Scenario: Admin lands on setup or workspace operation
- **WHEN** an admin signs in and has no active imported workspace
- **THEN** the product MUST guide them toward repository connection, provider configuration, and team setup before review work

#### Scenario: Reviewer lands on pending review work
- **WHEN** a reviewer signs in and at least one workspace has reviewable decision candidates
- **THEN** the product MUST provide a direct path to the pending review queue without requiring the reviewer to start from import settings

#### Scenario: Viewer lands on read-only decision discovery
- **WHEN** a viewer signs in
- **THEN** the product MUST provide read-only paths to decisions, search, timeline, drift status, and evidence without exposing management actions

### Requirement: Workspace-centered navigation
The frontend SHALL keep dashboard, review, search, timeline, drift, governance context, and evidence access anchored to the active workspace.

#### Scenario: Workspace links preserve context
- **WHEN** a user navigates from a workspace dashboard to review, search, timeline, or drift
- **THEN** each destination MUST retain the active workspace context and provide an obvious path back to the workspace dashboard

#### Scenario: Global and workspace navigation are visually and behaviorally separated
- **WHEN** the sidebar is displayed inside a workspace
- **THEN** workspace-specific links MUST be grouped separately from global administration and product-level links

### Requirement: Repository import is a guided task flow
The frontend SHALL present repository import as a guided task flow rather than a hidden advanced homepage control.

#### Scenario: New repository import
- **WHEN** an admin enters a public or private Git repository
- **THEN** the product MUST validate access, explain any missing access requirements, start import when allowed, show progress, and navigate to the resulting workspace

#### Scenario: Existing workspace reuse
- **WHEN** a repository already has a workspace
- **THEN** the product MUST offer opening the existing workspace, incremental sync, or full rerun as distinct choices with clear consequences

### Requirement: Decision detail is the core object page
The frontend SHALL make the decision detail page the primary place to understand one decision's status, evidence, review history, drift relationship, and source references.

#### Scenario: User opens a decision from review or search
- **WHEN** a user opens a decision from review, search, timeline, or drift
- **THEN** the decision detail page MUST show enough context to continue the task without forcing the user to manually reconstruct where the decision came from

#### Scenario: Reviewer completes a decision action
- **WHEN** a reviewer accepts, rejects, or supersedes a decision candidate
- **THEN** the product MUST provide a clear next step to continue reviewing, inspect evidence, or return to the workspace dashboard

### Requirement: Evidence Center supports release and operator work
The frontend SHALL present evidence as an operator-facing center for guardrail, benchmark, hosted readiness, release evidence, and audit history.

#### Scenario: Operator reviews release readiness
- **WHEN** an operator opens Evidence Center
- **THEN** the product MUST summarize current guardrail status, benchmark comparison, hosted readiness, and release evidence availability

#### Scenario: Evidence is unavailable
- **WHEN** no evidence has been generated yet
- **THEN** the product MUST explain the missing evidence and provide the next action to generate or collect it
