import React from "react";
import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import { ReviewPageContent } from "../components/review/review-page-content";

const sessionState = vi.hoisted(() => ({
  value: {
    session: { role: "reviewer" },
    status: "ready" as const,
    canReviewWorkspace: true,
    canManageWorkspace: false,
  },
}));

vi.mock("next/navigation", () => ({
  usePathname: () => "/review",
}));

vi.mock("../components/navigation/global-sidebar", () => ({
  GlobalSidebar: () => <nav data-testid="global-sidebar" />,
}));

vi.mock("../components/auth/session-provider", () => ({
  useProductSession: () => ({
    ...sessionState.value,
    error: null,
    refreshSession: async () => null,
    login: async () => {
      throw new Error("not used");
    },
    switchScope: async () => {
      throw new Error("not used");
    },
  }),
}));

const candidate = {
  id: 1,
  workspace_id: 1,
  title: "Use Redis Cache",
  status: "active",
  review_state: "candidate",
  problem: "Latency too high",
  context: "Read load increased",
  constraints: "Budget is limited",
  chosen_option: "Use Redis as cache only",
  tradeoffs: "Extra dependency",
  confidence: 0.88,
} as const;

describe("review audit UX", () => {
  it("shows reviewer role guidance and compact audit trail", () => {
    sessionState.value = {
      session: { role: "reviewer" },
      status: "ready",
      canReviewWorkspace: true,
      canManageWorkspace: false,
    };

    render(<ReviewPageContent workspaceSlug="demo-workspace" decisions={[candidate]} />);

    expect(screen.getByRole("heading", { name: /Current review role: reviewer/i })).toBeInTheDocument();
    expect(screen.getByText("review actions available")).toBeInTheDocument();
    expect(screen.getByText(/1 candidate decisions are waiting for human review/i)).toBeInTheDocument();
    expect(screen.getByLabelText("Recent review audit trail")).toHaveTextContent("Candidate queued for review");
    expect(screen.getByLabelText("Recent review audit trail")).toHaveTextContent("Use Redis Cache");
    expect(screen.getByRole("button", { name: "Accept" })).toBeInTheDocument();
  });

  it("shows viewer read-only guidance and no enabled review actions", () => {
    sessionState.value = {
      session: { role: "viewer" },
      status: "ready",
      canReviewWorkspace: false,
      canManageWorkspace: false,
    };

    render(<ReviewPageContent workspaceSlug="demo-workspace" decisions={[candidate]} />);

    expect(screen.getByRole("heading", { name: /Current review role: viewer/i })).toBeInTheDocument();
    expect(screen.getByText("read-only")).toBeInTheDocument();
    expect(screen.getByText(/cannot accept, reject, or supersede/i)).toBeInTheDocument();
    expect(screen.getByText(/ask a reviewer or admin/i)).toBeInTheDocument();
    expect(screen.getByText("Reviewer or admin role required for review actions.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Accept" })).not.toBeInTheDocument();
  });

  it("shows an audit empty state when no review records exist", () => {
    sessionState.value = {
      session: { role: "admin" },
      status: "ready",
      canReviewWorkspace: true,
      canManageWorkspace: true,
    };

    render(<ReviewPageContent workspaceSlug="imported-workspace" decisions={[]} />);

    expect(screen.getByText(/No review audit records are visible yet/i)).toBeInTheDocument();
  });
});
