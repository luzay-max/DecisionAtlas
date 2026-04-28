import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { ProductSessionProvider } from "../components/auth/session-provider";
import { GitHubAppInstallationPanel } from "../components/github-app/github-app-installation-panel";
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
    bindGithubAppInstallation: vi.fn(),
  };
});

const adminSession: api.ProductSession = {
  session_token: "admin-token",
  actor: { id: 1, username: "admin@example.com" },
  current_owner_scope: "team-a",
  role: "admin",
  available_scopes: [{ owner_scope: "team-a", role: "admin" }],
};

const reviewerSession: api.ProductSession = {
  ...adminSession,
  role: "reviewer",
  available_scopes: [{ owner_scope: "team-a", role: "reviewer" }],
};

describe("GitHubAppInstallationPanel", () => {
  beforeEach(() => {
    vi.mocked(api.getProductSession).mockReset();
    vi.mocked(api.bindGithubAppInstallation).mockReset();
  });

  it("binds a repository to a GitHub App installation for the current scope", async () => {
    vi.mocked(api.getProductSession).mockResolvedValue(adminSession);
    vi.mocked(api.bindGithubAppInstallation).mockResolvedValue({
      owner_scope: "team-a",
      repo: "org/repo",
      repo_url: "https://github.com/org/repo",
      workspace_exists: true,
      workspace_slug: "github-org-repo",
      has_successful_import: false,
      can_incremental_sync: false,
      has_running_import: false,
      latest_import: null,
      access_source_type: "github_app_installation",
      access_source_label: "GitHub App installation #12345",
    });

    const user = userEvent.setup();
    render(
      <ProductSessionProvider>
        <GitHubAppInstallationPanel />
      </ProductSessionProvider>
    );

    await waitFor(() => expect(screen.getByText(/Current owner scope:/)).toHaveTextContent("team-a"));
    await user.type(screen.getByLabelText("Repository"), "org/repo");
    await user.type(screen.getByLabelText("Installation ID"), "12345");
    await user.type(screen.getByLabelText("Account login"), "org");
    await user.type(screen.getByLabelText("Account type"), "Organization");
    await user.click(screen.getByRole("button", { name: "Bind GitHub App installation" }));

    await waitFor(() =>
      expect(api.bindGithubAppInstallation).toHaveBeenCalledWith({
        repo: "org/repo",
        installation_id: "12345",
        account_login: "org",
        account_type: "Organization",
      })
    );
    expect(screen.getByText("GitHub App installation bound to this owner scope.")).toBeInTheDocument();
    expect(screen.getByText("GitHub App installation #12345")).toBeInTheDocument();
    expect(
      screen.getByText(/Open the workspace dashboard to review latest sync origin, active webhook sync state/i)
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Open workspace" })).toHaveAttribute(
      "href",
      "/workspaces/github-org-repo"
    );
    expect(screen.getByRole("link", { name: "Review sync state" })).toHaveAttribute(
      "href",
      "/workspaces/github-org-repo"
    );
  });

  it("shows bounded binding errors without rendering a result", async () => {
    vi.mocked(api.getProductSession).mockResolvedValue(adminSession);
    vi.mocked(api.bindGithubAppInstallation).mockRejectedValue(new Error("Invalid installation binding payload"));

    const user = userEvent.setup();
    render(
      <ProductSessionProvider>
        <GitHubAppInstallationPanel />
      </ProductSessionProvider>
    );

    await user.type(await screen.findByLabelText("Repository"), "org/repo");
    await user.type(screen.getByLabelText("Installation ID"), "bad");
    await user.click(screen.getByRole("button", { name: "Bind GitHub App installation" }));

    await waitFor(() => expect(screen.getByText("Invalid installation binding payload")).toBeInTheDocument());
    expect(screen.queryByRole("link", { name: "Open workspace" })).not.toBeInTheDocument();
  });

  it("keeps installation setup admin-only", async () => {
    vi.mocked(api.getProductSession).mockResolvedValue(reviewerSession);

    render(
      <ProductSessionProvider>
        <GitHubAppInstallationPanel />
      </ProductSessionProvider>
    );

    await waitFor(() =>
      expect(screen.getByText("Admin role required for GitHub App installation setup.")).toBeInTheDocument()
    );
    expect(screen.queryByRole("button", { name: "Bind GitHub App installation" })).not.toBeInTheDocument();
  });
});
