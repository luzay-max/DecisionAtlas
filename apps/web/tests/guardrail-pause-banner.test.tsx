import React from "react";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { GuardrailPauseBanner } from "../components/governance/guardrail-pause-banner";

const getGovernanceGuardrail = vi.fn();

vi.mock("../lib/api", async () => {
  const actual = await vi.importActual<typeof import("../lib/api")>("../lib/api");
  return {
    ...actual,
    getGovernanceGuardrail: (...args: unknown[]) => getGovernanceGuardrail(...args),
  };
});

vi.mock("../components/i18n/language-provider", () => ({
  useI18n: () => ({ language: "en", messages: {} }),
}));

describe("GuardrailPauseBanner", () => {
  beforeEach(() => {
    getGovernanceGuardrail.mockReset();
  });

  it("renders canonical recurrence metadata for grouped drift signals", async () => {
    getGovernanceGuardrail.mockResolvedValue({
      agent_status: "caution",
      summary: "Governance drift needs review.",
      required_tests: [],
      human_decisions_needed: [],
      recommended_next_actions: [],
      human_questions: [],
      findings: [],
      signals: [
        {
          id: "repeated-postmortem-a",
          type: "repeated_postmortem_issue",
          title: "Recent context resembles a historical issue",
          occurrence_count: 9,
          source_count: 7,
          recommended_next_action: "Review the historical issue.",
        },
      ],
    });

    render(<GuardrailPauseBanner workspaceSlug="github-jazzband-pip-tools" />);

    expect(await screen.findByText("Repeated 9 times · 7 sources")).toBeInTheDocument();
    expect(screen.getByText("Recent context resembles a historical issue")).toBeInTheDocument();
  });

  it("keeps legacy single-signal payloads free of recurrence noise", async () => {
    getGovernanceGuardrail.mockResolvedValue({
      agent_status: "caution",
      summary: "Governance drift needs review.",
      required_tests: [],
      human_decisions_needed: [],
      recommended_next_actions: [],
      human_questions: [],
      findings: [],
      signals: [
        {
          id: "spec-gap-a",
          type: "spec_gap",
          title: "Missing spec",
        },
      ],
    });

    render(<GuardrailPauseBanner workspaceSlug="legacy-workspace" />);

    expect(await screen.findByText("Missing spec")).toBeInTheDocument();
    expect(screen.queryByText(/Repeated .* times/)).not.toBeInTheDocument();
  });
});
