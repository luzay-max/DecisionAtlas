import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { ProductSessionProvider } from "../components/auth/session-provider";
import { TeamManagementPanel } from "../components/auth/team-management-panel";
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
    listTeamAccounts: vi.fn(),
    createTeamAccount: vi.fn(),
    disableTeamAccount: vi.fn(),
    resetTeamAccountPassword: vi.fn(),
    updateTeamAccountRole: vi.fn(),
    listWorkspaceMembers: vi.fn(),
    assignWorkspaceMember: vi.fn(),
    removeWorkspaceMember: vi.fn(),
  };
});

const adminSession: api.ProductSession = {
  session_token: "admin-token",
  actor: { id: 1, username: "admin@example.com", bootstrap: true },
  current_owner_scope: "team-a",
  role: "admin",
  available_scopes: [{ owner_scope: "team-a", role: "admin" }],
};

const reviewerSession: api.ProductSession = {
  ...adminSession,
  actor: { id: 2, username: "reviewer@example.com" },
  role: "reviewer",
  available_scopes: [{ owner_scope: "team-a", role: "reviewer" }],
};

describe("TeamManagementPanel", () => {
  beforeEach(() => {
    vi.mocked(api.getProductSession).mockReset();
    vi.mocked(api.listTeamAccounts).mockReset();
    vi.mocked(api.createTeamAccount).mockReset();
    vi.mocked(api.disableTeamAccount).mockReset();
    vi.mocked(api.resetTeamAccountPassword).mockReset();
    vi.mocked(api.updateTeamAccountRole).mockReset();
    vi.mocked(api.listWorkspaceMembers).mockReset();
    vi.mocked(api.assignWorkspaceMember).mockReset();
    vi.mocked(api.removeWorkspaceMember).mockReset();
  });

  it("lets admins create accounts and assign workspace members", async () => {
    vi.mocked(api.getProductSession).mockResolvedValue(adminSession);
    vi.mocked(api.listTeamAccounts).mockResolvedValue([
      { id: 1, username: "admin@example.com", display_name: null, status: "active", bootstrap: true, role: "admin" },
      { id: 2, username: "viewer@example.com", display_name: null, status: "active", bootstrap: false, role: "viewer" },
    ]);
    vi.mocked(api.createTeamAccount).mockResolvedValue({
      id: 3,
      username: "reviewer@example.com",
      display_name: null,
      status: "active",
      bootstrap: false,
      role: "reviewer",
    });
    vi.mocked(api.listWorkspaceMembers).mockResolvedValue([
      {
        workspace_id: 1,
        actor: { id: 2, username: "viewer@example.com", display_name: null, status: "active", bootstrap: false, role: "viewer" },
        role: "viewer",
      },
    ]);
    vi.mocked(api.assignWorkspaceMember).mockResolvedValue({
      workspace_id: 1,
      actor: { id: 2, username: "viewer@example.com", display_name: null, status: "active", bootstrap: false, role: "viewer" },
      role: "viewer",
    });

    const user = userEvent.setup();
    render(
      <ProductSessionProvider>
        <TeamManagementPanel />
      </ProductSessionProvider>
    );

    await waitFor(() => expect(screen.getByText(/Current actor:/)).toHaveTextContent("admin@example.com"));
    await user.type(screen.getByLabelText("Username"), "reviewer@example.com");
    await user.type(screen.getByLabelText("Initial password"), "password123");
    await user.selectOptions(screen.getByLabelText("Scope role"), "reviewer");
    await user.click(screen.getByRole("button", { name: "Create account" }));

    await waitFor(() =>
      expect(api.createTeamAccount).toHaveBeenCalledWith({
        username: "reviewer@example.com",
        password: "password123",
        display_name: undefined,
        role: "reviewer",
      })
    );

    await user.click(screen.getByRole("button", { name: "Load members" }));
    await waitFor(() => expect(api.listWorkspaceMembers).toHaveBeenCalledWith("demo-workspace"));
    await user.type(screen.getAllByLabelText("Actor ID")[1], "2");
    await user.click(screen.getByRole("button", { name: "Assign member" }));
    await waitFor(() => expect(api.assignWorkspaceMember).toHaveBeenCalledWith("demo-workspace", 2, "viewer"));
  });

  it("keeps team management admin-only", async () => {
    vi.mocked(api.getProductSession).mockResolvedValue(reviewerSession);
    vi.mocked(api.listTeamAccounts).mockResolvedValue([]);

    render(
      <ProductSessionProvider>
        <TeamManagementPanel />
      </ProductSessionProvider>
    );

    await waitFor(() =>
      expect(
        screen.getByText("Admin role required for team account and workspace permission management.")
      ).toBeInTheDocument()
    );
    expect(screen.queryByRole("button", { name: "Create account" })).not.toBeInTheDocument();
  });
});
