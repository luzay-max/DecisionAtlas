import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
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
}));

vi.mock("../lib/api", async () => {
  const actual = await vi.importActual<typeof import("../lib/api")>("../lib/api");
  return {
    ...actual,
    getProductSession: vi.fn(),
    importGovernanceDocument: vi.fn(),
    reviewGovernanceRule: vi.fn(),
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
    expect(screen.getByText(/Clear validation rule/i)).toBeInTheDocument();
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
});
