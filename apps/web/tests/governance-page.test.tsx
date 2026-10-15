import React from "react";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { ProductSessionProvider } from "../components/auth/session-provider";
import { GovernancePageContent } from "../components/governance/governance-page-content";
import * as api from "../lib/api";

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    refresh: vi.fn(),
    push: vi.fn(),
  }),
  usePathname: () => "/governance",
}));

vi.mock("../components/navigation/global-sidebar", () => ({
  GlobalSidebar: () => <nav data-testid="global-sidebar" />,
}));

vi.mock("../lib/api", async () => {
  const actual = await vi.importActual<typeof import("../lib/api")>("../lib/api");
  return {
    ...actual,
    getProductSession: vi.fn(),
    importGovernanceDocument: vi.fn(),
    reviewGovernanceRule: vi.fn(),
    updateGovernanceRuleLifecycle: vi.fn(),
  };
});

const adminSession: api.ProductSession = {
  session_token: "admin-token",
  actor: { id: 1, username: "admin@example.com" },
  current_owner_scope: "team-a",
  role: "admin",
  available_scopes: [{ owner_scope: "team-a", role: "admin" }],
};

describe("GovernancePageContent", () => {
  beforeEach(() => {
    vi.mocked(api.getProductSession).mockReset();
    vi.mocked(api.importGovernanceDocument).mockReset();
    vi.mocked(api.reviewGovernanceRule).mockReset();
    vi.mocked(api.updateGovernanceRuleLifecycle).mockReset();
    vi.mocked(api.getProductSession).mockResolvedValue(adminSession);
  });

  it("imports markdown and renders pending rule drafts", async () => {
    const user = userEvent.setup();
    vi.mocked(api.importGovernanceDocument).mockResolvedValue({
      document: {
        id: 1,
        owner_scope: "team-a",
        title: "Development Standards",
        document_type: "coding_guideline",
        scope: "all",
        status: "active",
        source_path: "docs/standards.md",
        content_hash: "abc",
      },
      drafts: [
        {
          id: 2,
          owner_scope: "team-a",
          document_id: 1,
          source_title: "Development Standards",
          title: "Rule: Every change has tests",
          description: "Every backend behavior change should include a targeted pytest.",
          severity: "warning",
          scope: "engine",
          source_excerpt: "## Rule: Every change has tests",
          rule_type: "standard",
          extraction_reason: "rule heading marker",
          lifecycle_status: "current",
          review_state: "pending",
          status: "draft",
        },
      ],
    });

    render(
      <ProductSessionProvider>
        <GovernancePageContent initialDocuments={[]} initialRules={[]} />
      </ProductSessionProvider>
    );

    expect(screen.getByText(/not automatic CI blockers yet/i)).toBeInTheDocument();
    await user.type(await screen.findByLabelText("Document title"), "Development Standards");
    await user.selectOptions(screen.getByLabelText("Document type"), "coding_guideline");
    await user.type(screen.getByLabelText("Markdown content"), "## Rule: Every change has tests\n\nMust test changes.");
    await user.click(screen.getByRole("button", { name: "Import governance Markdown" }));

    await waitFor(() => {
      expect(screen.getByText("Rule: Every change has tests")).toBeInTheDocument();
    });
    expect(screen.getByText("Imported Development Standards and created 1 rule drafts.")).toBeInTheDocument();
  });

  it("accepts pending rule drafts without a reload", async () => {
    const user = userEvent.setup();
    vi.mocked(api.reviewGovernanceRule).mockResolvedValue({
      id: 2,
      owner_scope: "team-a",
      document_id: 1,
      source_title: "Development Standards",
      title: "Rule: Every change has tests",
      description: "Every backend behavior change should include a targeted pytest.",
      severity: "warning",
      scope: "engine",
      source_excerpt: "## Rule: Every change has tests",
      rule_type: "standard",
      extraction_reason: "rule heading marker",
      review_state: "accepted",
      status: "active",
      review_rationale: "Clear validation rule.",
      lifecycle_status: "current",
      audit_history: [
        {
          id: 5,
          owner_scope: "team-a",
          workspace_id: null,
          actor_id: 1,
          actor_username: "reviewer@example.com",
          actor_role: "reviewer",
          target_type: "governance_rule",
          target_id: 2,
          action: "governance_rule_review_accepted",
          previous_state: { review_state: "pending" },
          new_state: { review_state: "accepted" },
          rationale: "Clear validation rule.",
          created_at: "2026-06-08T10:00:00",
        },
      ],
    });

    render(
      <ProductSessionProvider>
        <GovernancePageContent
          initialDocuments={[]}
          initialRules={[
            {
              id: 2,
              owner_scope: "team-a",
              document_id: 1,
              source_title: "Development Standards",
              title: "Rule: Every change has tests",
              description: "Every backend behavior change should include a targeted pytest.",
              severity: "warning",
              scope: "engine",
              source_excerpt: "## Rule: Every change has tests",
              rule_type: "standard",
              extraction_reason: "rule heading marker",
              review_state: "pending",
              status: "draft",
              lifecycle_status: "current",
            },
          ]}
        />
      </ProductSessionProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Accept rule" })).toBeInTheDocument();
    });
    await user.type(screen.getByLabelText("Review rationale"), "Clear validation rule.");
    await user.click(screen.getByRole("button", { name: "Accept rule" }));

    await waitFor(() => {
      expect(api.reviewGovernanceRule).toHaveBeenCalledWith(2, "accepted", "Clear validation rule.");
    });
    expect(screen.getAllByText(/Rule type/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/rule heading marker/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Clear validation rule/i).length).toBeGreaterThan(0);
    expect(screen.getByText("Review history")).toBeInTheDocument();
    expect(screen.getByText(/reviewer@example.com/)).toBeInTheDocument();
    expect(
      screen.getByText((_content, element) => {
        const text = element?.textContent ?? "";
        return element?.tagName.toLowerCase() === "p" && text.includes("Status") && text.includes("accepted");
      })
    ).toBeInTheDocument();
  });

  it("filters accepted rules by bounded metadata", async () => {
    const user = userEvent.setup();
    render(
      <ProductSessionProvider>
        <GovernancePageContent
          initialDocuments={[]}
          initialRules={[
            {
              id: 2,
              owner_scope: "team-a",
              document_id: 1,
              source_title: "Development Standards",
              title: "Rule: Engine changes need tests",
              description: "Every backend behavior change should include a targeted pytest.",
              severity: "warning",
              scope: "engine",
              source_excerpt: "## Rule: Engine changes need tests",
              rule_type: "standard",
              extraction_reason: "rule heading marker",
              review_state: "accepted",
              status: "active",
              review_rationale: "Accepted as validation baseline.",
              lifecycle_status: "current",
            },
            {
              id: 3,
              owner_scope: "team-a",
              document_id: 1,
              source_title: "Documentation Standards",
              title: "Rule: Docs mention known limits",
              description: "Document known limitations.",
              severity: "note",
              scope: "docs",
              source_excerpt: "## Rule: Docs mention known limits",
              rule_type: "standard",
              extraction_reason: "rule heading marker",
              review_state: "accepted",
              status: "active",
              lifecycle_status: "current",
            },
          ]}
        />
      </ProductSessionProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("Rule: Engine changes need tests")).toBeInTheDocument();
    });
    await user.selectOptions(screen.getByLabelText("Filter by scope"), "docs");

    expect(screen.queryByText("Rule: Engine changes need tests")).not.toBeInTheDocument();
    expect(screen.getByText("Rule: Docs mention known limits")).toBeInTheDocument();
  });

  it("marks accepted current rules stale with rationale without a reload", async () => {
    const user = userEvent.setup();
    vi.mocked(api.updateGovernanceRuleLifecycle).mockResolvedValue({
      id: 2,
      owner_scope: "team-a",
      document_id: 1,
      source_title: "Development Standards",
      title: "Rule: Engine changes need tests",
      description: "Every backend behavior change should include a targeted pytest.",
      severity: "warning",
      scope: "engine",
      source_excerpt: "## Rule: Engine changes need tests",
      rule_type: "standard",
      extraction_reason: "rule heading marker",
      review_state: "accepted",
      status: "active",
      review_rationale: "Accepted as validation baseline.",
      lifecycle_status: "stale",
      lifecycle_rationale: "Replaced by stricter validation evidence.",
    });

    render(
      <ProductSessionProvider>
        <GovernancePageContent
          initialDocuments={[]}
          initialRules={[
            {
              id: 2,
              owner_scope: "team-a",
              document_id: 1,
              source_title: "Development Standards",
              title: "Rule: Engine changes need tests",
              description: "Every backend behavior change should include a targeted pytest.",
              severity: "warning",
              scope: "engine",
              source_excerpt: "## Rule: Engine changes need tests",
              rule_type: "standard",
              extraction_reason: "rule heading marker",
              review_state: "accepted",
              status: "active",
              review_rationale: "Accepted as validation baseline.",
              lifecycle_status: "current",
            },
          ]}
        />
      </ProductSessionProvider>
    );

    await user.type(await screen.findByLabelText("Lifecycle rationale"), "Replaced by stricter validation evidence.");
    await user.click(screen.getByRole("button", { name: "Mark stale" }));

    await waitFor(() => {
      expect(api.updateGovernanceRuleLifecycle).toHaveBeenCalledWith(
        2,
        "stale",
        "Replaced by stricter validation evidence.",
        undefined
      );
    });
    expect(screen.getByText(/Lifecycle rationale:/i)).toBeInTheDocument();
    expect(screen.getByText(/Replaced by stricter validation evidence/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Mark stale" })).not.toBeInTheDocument();
  });

  it("supersedes accepted current rules with a selected replacement", async () => {
    const user = userEvent.setup();
    vi.mocked(api.updateGovernanceRuleLifecycle).mockResolvedValue({
      id: 2,
      owner_scope: "team-a",
      document_id: 1,
      source_title: "Development Standards",
      title: "Rule: Old validation wording",
      description: "Engine changes should mention validation.",
      severity: "warning",
      scope: "engine",
      source_excerpt: "## Rule: Old validation wording",
      rule_type: "standard",
      extraction_reason: "rule heading marker",
      review_state: "accepted",
      status: "active",
      lifecycle_status: "superseded",
      superseded_by_rule_id: 3,
      lifecycle_rationale: "Replacement is stricter.",
    });
    const rules: api.GovernanceRule[] = [
      {
        id: 2,
        owner_scope: "team-a",
        document_id: 1,
        source_title: "Development Standards",
        title: "Rule: Old validation wording",
        description: "Engine changes should mention validation.",
        severity: "warning",
        scope: "engine",
        source_excerpt: "## Rule: Old validation wording",
        rule_type: "standard",
        extraction_reason: "rule heading marker",
        review_state: "accepted",
        status: "active",
        lifecycle_status: "current",
      },
      {
        id: 3,
        owner_scope: "team-a",
        document_id: 1,
        source_title: "Development Standards",
        title: "Rule: Targeted validation evidence",
        description: "Engine changes must include targeted validation evidence.",
        severity: "blocker",
        scope: "engine",
        source_excerpt: "## Rule: Targeted validation evidence",
        rule_type: "standard",
        extraction_reason: "rule heading marker",
        review_state: "accepted",
        status: "active",
        lifecycle_status: "current",
      },
    ];

    render(
      <ProductSessionProvider>
        <GovernancePageContent initialDocuments={[]} initialRules={rules} />
      </ProductSessionProvider>
    );

    const oldRuleCard = (await screen.findByText("Rule: Old validation wording")).closest("article");
    expect(oldRuleCard).not.toBeNull();
    await user.type(within(oldRuleCard as HTMLElement).getByLabelText("Lifecycle rationale"), "Replacement is stricter.");
    await user.selectOptions(within(oldRuleCard as HTMLElement).getByLabelText("Replacement rule"), "3");
    await user.click(within(oldRuleCard as HTMLElement).getByRole("button", { name: "Mark superseded" }));

    await waitFor(() => {
      expect(api.updateGovernanceRuleLifecycle).toHaveBeenCalledWith(2, "superseded", "Replacement is stricter.", 3);
    });
    expect(screen.getByText(/Superseded by rule:/i)).toBeInTheDocument();
    expect(screen.getByText(/#3/i)).toBeInTheDocument();
  });
});
