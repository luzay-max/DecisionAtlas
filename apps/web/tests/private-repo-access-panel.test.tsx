import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { ProductSessionProvider } from "../components/auth/session-provider";
import { PrivateRepoAccessPanel } from "../components/private-access/private-repo-access-panel";
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
    bindGitSource: vi.fn(),
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

describe("PrivateRepoAccessPanel", () => {
  beforeEach(() => {
    vi.mocked(api.getProductSession).mockReset();
    vi.mocked(api.bindGitSource).mockReset();
  });

  it("binds private repository access for the current scope", async () => {
    vi.mocked(api.getProductSession).mockResolvedValue(adminSession);
    vi.mocked(api.bindGitSource).mockResolvedValue({
      owner_scope: "team-a",
      repo: "org/private-repo",
      repo_url: "https://github.com/org/private-repo",
      workspace_exists: true,
      workspace_slug: "github-org-private-repo",
      has_successful_import: false,
      can_incremental_sync: true,
      has_running_import: false,
      latest_import: null,
      provider: "github",
      access_mode: "token",
      setup_outcome: "authorized",
      access_source_type: "github_token",
      access_source_label: "Private GitHub source team private repo",
      access_source_status: "authorized",
      access_source_status_detail: null,
    });

    const user = userEvent.setup();
    render(
      <ProductSessionProvider>
        <PrivateRepoAccessPanel />
      </ProductSessionProvider>
    );

    await waitFor(() => expect(screen.getByText(/Current owner scope:/)).toHaveTextContent("team-a"));
    expect(screen.getByText(/Use a GitHub token with the minimum repository read access needed/)).toBeInTheDocument();
    expect(screen.getByLabelText("Git provider")).toHaveValue("github");
    expect(screen.getByLabelText("Access mode")).toHaveValue("token");
    await user.type(screen.getByLabelText("Repository"), "org/private-repo");
    await user.type(screen.getByLabelText("GitHub token"), "ghp-private-token");
    await user.type(screen.getByLabelText("Source label"), "team private repo");
    await user.click(screen.getByRole("button", { name: "Bind Git source access" }));

    await waitFor(() =>
      expect(api.bindGitSource).toHaveBeenCalledWith({
        provider: "github",
        access_mode: "token",
        repo: "org/private-repo",
        token: "ghp-private-token",
        source_ref: "org/private-repo",
        source_label: "team private repo",
      })
    );
    expect(screen.getByText("Git source access bound to this owner scope.")).toBeInTheDocument();
    expect(screen.getByText("Private GitHub source team private repo")).toBeInTheDocument();
    expect(screen.getByText(/Provider/)).toHaveTextContent("github");
    expect(screen.getByText(/Provider/)).toHaveTextContent("token");
    expect(screen.getByText(/Authorization status:/)).toHaveTextContent("authorized");
    expect(screen.getByText("This source is currently authorized.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Open workspace" })).toHaveAttribute(
      "href",
      "/workspaces/github-org-private-repo"
    );
    expect(screen.queryByText("ghp-private-token")).not.toBeInTheDocument();
    expect(screen.getByLabelText("GitHub token")).toHaveValue("");
  });

  it("shows bounded binding errors and clears submitted token material", async () => {
    vi.mocked(api.getProductSession).mockResolvedValue(adminSession);
    vi.mocked(api.bindGitSource).mockRejectedValue(new Error("Private access source is unauthorized"));

    const user = userEvent.setup();
    render(
      <ProductSessionProvider>
        <PrivateRepoAccessPanel />
      </ProductSessionProvider>
    );

    await user.type(await screen.findByLabelText("Repository"), "org/private-repo");
    await user.type(screen.getByLabelText("GitHub token"), "ghp-private-token");
    await user.click(screen.getByRole("button", { name: "Bind Git source access" }));

    await waitFor(() => expect(screen.getByText("Private access source is unauthorized")).toBeInTheDocument());
    expect(screen.queryByRole("link", { name: "Open workspace" })).not.toBeInTheDocument();
    expect(screen.queryByText("ghp-private-token")).not.toBeInTheDocument();
    expect(screen.getByLabelText("GitHub token")).toHaveValue("");
  });

  it("shows actionable recovery copy for unauthorized private access results", async () => {
    vi.mocked(api.getProductSession).mockResolvedValue(adminSession);
    vi.mocked(api.bindGitSource).mockResolvedValue({
      owner_scope: "team-a",
      repo: "org/private-repo",
      repo_url: "https://github.com/org/private-repo",
      workspace_exists: true,
      workspace_slug: "github-org-private-repo",
      has_successful_import: false,
      can_incremental_sync: false,
      has_running_import: false,
      latest_import: null,
      provider: "github",
      access_mode: "token",
      setup_outcome: "authorized",
      access_source_type: "github_token",
      access_source_label: "Private GitHub source team private repo",
      access_source_status: "unauthorized",
      access_source_status_detail: "GitHub token is unauthorized, expired, revoked, or lacks access to this repository.",
    });

    const user = userEvent.setup();
    render(
      <ProductSessionProvider>
        <PrivateRepoAccessPanel />
      </ProductSessionProvider>
    );

    await user.type(await screen.findByLabelText("Repository"), "org/private-repo");
    await user.type(screen.getByLabelText("GitHub token"), "ghp-private-token");
    await user.click(screen.getByRole("button", { name: "Bind Git source access" }));

    await waitFor(() => expect(screen.getByText(/Authorization status:/)).toHaveTextContent("unauthorized"));
    expect(screen.getByText(/Rotate the token or grant it access to this repository/)).toBeInTheDocument();
    expect(screen.queryByText("ghp-private-token")).not.toBeInTheDocument();
  });

  it("records unsupported Git providers as operator-guided without echoing token material", async () => {
    vi.mocked(api.getProductSession).mockResolvedValue(adminSession);
    vi.mocked(api.bindGitSource).mockResolvedValue({
      owner_scope: "team-a",
      repo: "group/private-repo",
      repo_url: null,
      workspace_exists: false,
      workspace_slug: null,
      has_successful_import: false,
      can_incremental_sync: false,
      has_running_import: false,
      latest_import: null,
      provider: "gitlab",
      access_mode: "token",
      setup_outcome: "provider_unsupported",
      next_action: "plan_provider_importer",
      access_source_type: "gitlab_token",
      access_source_label: "GitLab token source group private repo",
      access_source_status: "not_implemented",
    });

    const user = userEvent.setup();
    render(
      <ProductSessionProvider>
        <PrivateRepoAccessPanel />
      </ProductSessionProvider>
    );

    await user.selectOptions(await screen.findByLabelText("Git provider"), "gitlab");
    await user.type(screen.getByLabelText("Repository"), "group/private-repo");
    await user.type(screen.getByLabelText("Provider token"), "glpat-private-token");
    await user.click(screen.getByRole("button", { name: "Bind Git source access" }));

    await waitFor(() =>
      expect(api.bindGitSource).toHaveBeenCalledWith({
        provider: "gitlab",
        access_mode: "token",
        repo: "group/private-repo",
        token: "glpat-private-token",
        source_ref: "group/private-repo",
      })
    );
    expect(screen.getByText(/operator-guided until its importer is implemented/)).toBeInTheDocument();
    expect(screen.getByText(/outcome/)).toHaveTextContent("provider_unsupported");
    expect(screen.getByText(/Next action:/)).toHaveTextContent("plan_provider_importer");
    expect(screen.queryByText("glpat-private-token")).not.toBeInTheDocument();
    expect(screen.getByLabelText("Provider token")).toHaveValue("");
  });

  it("records local path setup as server-operator-guided without requiring a token", async () => {
    vi.mocked(api.getProductSession).mockResolvedValue(adminSession);
    vi.mocked(api.bindGitSource).mockResolvedValue({
      owner_scope: "team-a",
      repo: "local_path",
      repo_url: null,
      workspace_exists: false,
      workspace_slug: null,
      has_successful_import: false,
      can_incremental_sync: false,
      has_running_import: false,
      latest_import: null,
      provider: "local",
      access_mode: "local_path",
      setup_outcome: "local_path_unavailable",
      next_action: "configure_server_local_path_import",
      access_source_type: "local_path",
      access_source_label: "Local path source server repo",
      access_source_status: "operator_guided",
    });

    const user = userEvent.setup();
    render(
      <ProductSessionProvider>
        <PrivateRepoAccessPanel />
      </ProductSessionProvider>
    );

    await user.selectOptions(await screen.findByLabelText("Git provider"), "local");
    expect(screen.queryByLabelText("GitHub token")).not.toBeInTheDocument();
    await user.type(screen.getByLabelText("Server local path label"), "server repo");
    await user.click(screen.getByRole("button", { name: "Bind Git source access" }));

    await waitFor(() =>
      expect(api.bindGitSource).toHaveBeenCalledWith({
        provider: "local",
        access_mode: "local_path",
        repo: "server repo",
        source_ref: "server repo",
      })
    );
    expect(screen.getByText(/server-operator-guided/)).toBeInTheDocument();
    expect(screen.getByText(/outcome/)).toHaveTextContent("local_path_unavailable");
  });

  it("keeps private access setup admin-only", async () => {
    vi.mocked(api.getProductSession).mockResolvedValue(reviewerSession);

    render(
      <ProductSessionProvider>
        <PrivateRepoAccessPanel />
      </ProductSessionProvider>
    );

    await waitFor(() =>
      expect(screen.getByText("Admin role required for private repository access setup.")).toBeInTheDocument()
    );
    expect(screen.queryByRole("button", { name: "Bind Git source access" })).not.toBeInTheDocument();
  });
});
