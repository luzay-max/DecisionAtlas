import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { DriftPageContent } from "../components/drift/drift-page-content";
import * as api from "../lib/api";

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    refresh: vi.fn(),
  }),
}));

vi.mock("../lib/api", async () => {
  const actual = await vi.importActual<typeof import("../lib/api")>("../lib/api");
  return {
    ...actual,
    updateDriftAlertDisposition: vi.fn(),
  };
});

describe("DriftPageContent", () => {
  beforeEach(() => {
    vi.mocked(api.updateDriftAlertDisposition).mockReset();
  });

  it("renders persisted alerts with decision and artifact context", () => {
    render(
      <DriftPageContent
        workspaceSlug="demo-workspace"
        drift={{
          workspace_mode: "demo",
          source_summary: "This workspace is using seeded demo data for a guided product walkthrough.",
          alerts: [
            {
              id: 1,
              alert_type: "possible_supersession",
              summary: "Artifact 'Replace Redis cache with Dragonfly' may supersede accepted decision 'Use Redis Cache'.",
              status: "open",
              confidence_label: "medium",
              created_at: "2026-03-18T10:00:00",
              decision: {
                id: 7,
                title: "Use Redis Cache",
                review_state: "accepted",
                chosen_option: "Use Redis as cache only",
              },
              artifact: {
                id: 12,
                type: "pull_request",
                title: "Persist sessions in Redis",
                url: "https://github.com/org/repo/pull/2",
              },
            },
          ],
        }}
      />
    );

    expect(screen.getByText("Possible decision drift")).toBeInTheDocument();
    expect(screen.getByText("possible supersession")).toBeInTheDocument();
    expect(
      screen.getByText(/may be replacing a prior accepted decision, but it still needs human confirmation/i)
    ).toBeInTheDocument();
    expect(screen.getByText(/Workspace Type/i)).toBeInTheDocument();
    expect(screen.getByText(/^Demo Workspace$/)).toBeInTheDocument();
    expect(screen.getByText(/The guided demo is complete/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Back to dashboard" })).toHaveAttribute(
      "href",
      "/workspaces/demo-workspace"
    );
    expect(screen.getByText("Use Redis Cache")).toBeInTheDocument();
    expect(screen.getByText("medium confidence")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Persist sessions in Redis" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Use Redis Cache" })).toHaveAttribute(
      "href",
      "/decisions/7?workspace=demo-workspace"
    );
  });

  it("does not crash when a legacy drift response is still an array", () => {
    render(
      <DriftPageContent
        workspaceSlug="demo-workspace"
        drift={[
          {
            id: 1,
            alert_type: "possible_supersession",
            summary: "Artifact 'Replace Redis cache with Dragonfly' may supersede accepted decision 'Use Redis Cache'.",
            status: "open",
            confidence_label: "medium",
            created_at: "2026-03-18T10:00:00",
            decision: {
              id: 7,
              title: "Use Redis Cache",
              review_state: "accepted",
              chosen_option: "Use Redis as cache only",
            },
            artifact: {
              id: 12,
              type: "pull_request",
              title: "Persist sessions in Redis",
              url: "https://github.com/org/repo/pull/2",
            },
          },
        ]}
      />
    );

    expect(screen.getByText("Use Redis Cache")).toBeInTheDocument();
    expect(screen.queryByText(/Workspace Type/i)).not.toBeInTheDocument();
  });

  it("shows imported evaluation state before alerts exist", () => {
    render(
      <DriftPageContent
        workspaceSlug="imported-workspace"
        drift={{
          workspace_mode: "imported",
          source_summary: "Imported repository data from GitHub-backed analysis.",
          evaluation: {
            state: "unevaluated",
            can_evaluate: true,
            next_action: "evaluate_drift",
            last_evaluated_at: null,
          },
          alerts: [],
        }}
      />
    );

    expect(screen.getByText("Drift has not been evaluated yet")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Evaluate drift now" })).toBeInTheDocument();
    expect(screen.getByText(/use the evaluation card above/i)).toBeInTheDocument();
  });

  it("renders grouped follow-up alerts as one compact review thread", () => {
    render(
      <DriftPageContent
        workspaceSlug="imported-workspace"
        drift={{
          workspace_mode: "imported",
          source_summary: "Imported repository data from GitHub-backed analysis.",
          evaluation: {
            state: "alerts_present",
            can_evaluate: true,
            next_action: "evaluate_drift",
            last_evaluated_at: "2026-04-01T08:00:00",
          },
          alerts: [
            {
              id: 3,
              alert_type: "needs_review",
              summary:
                "Artifact 'Evaluate remote browser cookie transfer for HTTP downloads' and 2 related follow-up artifacts appear connected to accepted decision 'Enable HTTP-based downloads for remote browsers with agent status tracking'. Review whether this newer work only continues the prior choice or introduces a real decision change. Closest prior choice: Use HTTP-based downloads with remote browser status tracking.",
              status: "open",
              confidence_label: "low",
              created_at: "2026-04-01T08:00:00",
              decision: {
                id: 9,
                title: "Enable HTTP-based downloads for remote browsers with agent status tracking",
                review_state: "accepted",
                chosen_option: "Use HTTP-based downloads with remote browser status tracking.",
              },
              artifact: {
                id: 21,
                type: "pull_request",
                title: "Evaluate remote browser cookie transfer for HTTP downloads",
                url: "https://github.com/browser-use/browser-use/pull/3901",
              },
            },
          ],
        }}
      />
    );

    expect(screen.getByText("needs review")).toBeInTheDocument();
    expect(screen.getByText(/related follow-up artifacts/i)).toBeInTheDocument();
    expect(
      screen.getByText(/condenses several related implementation follow-ups into one review thread/i)
    ).toBeInTheDocument();
  });

  it("updates drift disposition and shows returned audit history", async () => {
    const user = userEvent.setup();
    vi.mocked(api.updateDriftAlertDisposition).mockResolvedValue({
      alert: {
        id: 4,
        alert_type: "needs_review",
        summary: "Artifact 'Redis update' appears related to accepted decision 'Use Redis Cache'.",
        status: "resolved",
        confidence_label: "low",
        created_at: "2026-06-08T11:00:00",
        handled_by: "reviewer@example.com",
        handled_at: "2026-06-08T11:05:00",
        disposition_rationale: "No drift; this reinforces the existing decision.",
        audit_history: [
          {
            id: 8,
            owner_scope: "team-a",
            workspace_id: 1,
            actor_id: 2,
            actor_username: "reviewer@example.com",
            actor_role: "reviewer",
            target_type: "drift_alert",
            target_id: 4,
            action: "drift_alert_disposition_resolved",
            previous_state: { status: "open" },
            new_state: { status: "resolved" },
            rationale: "No drift; this reinforces the existing decision.",
            created_at: "2026-06-08T11:05:00",
          },
        ],
        decision: {
          id: 7,
          title: "Use Redis Cache",
          review_state: "accepted",
          chosen_option: "Use Redis as cache only",
        },
        artifact: {
          id: 12,
          type: "pull_request",
          title: "Redis update",
          url: "https://github.com/org/repo/pull/12",
        },
      },
      audit_event: {
        id: 8,
        owner_scope: "team-a",
        actor_username: "reviewer@example.com",
        actor_role: "reviewer",
        target_type: "drift_alert",
        target_id: 4,
        action: "drift_alert_disposition_resolved",
      },
    });

    render(
      <DriftPageContent
        workspaceSlug="imported-workspace"
        drift={{
          workspace_mode: "imported",
          source_summary: "Imported repository data from GitHub-backed analysis.",
          alerts: [
            {
              id: 4,
              alert_type: "needs_review",
              summary: "Artifact 'Redis update' appears related to accepted decision 'Use Redis Cache'.",
              status: "open",
              confidence_label: "low",
              created_at: "2026-06-08T11:00:00",
              decision: {
                id: 7,
                title: "Use Redis Cache",
                review_state: "accepted",
                chosen_option: "Use Redis as cache only",
              },
              artifact: {
                id: 12,
                type: "pull_request",
                title: "Redis update",
                url: "https://github.com/org/repo/pull/12",
              },
            },
          ],
        }}
      />
    );

    await user.type(screen.getByLabelText("Disposition rationale"), "No drift; this reinforces the existing decision.");
    await user.click(screen.getByRole("button", { name: "Resolve" }));

    await waitFor(() => {
      expect(api.updateDriftAlertDisposition).toHaveBeenCalledWith(
        4,
        "resolved",
        "No drift; this reinforces the existing decision."
      );
    });
    expect(screen.getByText(/handled by reviewer@example.com/)).toBeInTheDocument();
    expect(screen.getByText("Handling history")).toBeInTheDocument();
    expect(screen.getByText(/drift alert disposition resolved/)).toBeInTheDocument();
  });
});
