import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { AccountScopeSurface } from "../components/auth/account-scope-surface";
import { LoginPanel } from "../components/auth/login-panel";
import { ProductSessionProvider } from "../components/auth/session-provider";
import { ScopedUnavailable } from "../components/auth/scoped-unavailable";
import * as api from "../lib/api";

const push = vi.fn();
const refresh = vi.fn();
let searchParams = new URLSearchParams();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push,
    refresh,
  }),
  useSearchParams: () => searchParams,
}));

vi.mock("../lib/api", async () => {
  const actual = await vi.importActual<typeof import("../lib/api")>("../lib/api");
  return {
    ...actual,
    getProductSession: vi.fn(),
    loginProductSession: vi.fn(),
    switchProductScope: vi.fn(),
  };
});

const bootstrapSession: api.ProductSession = {
  session_token: "boot-token",
  actor: { id: 1, username: "local-admin", bootstrap: true },
  current_owner_scope: "local-default",
  role: "admin",
  available_scopes: [{ owner_scope: "local-default", role: "admin" }],
};

const multiScopeSession: api.ProductSession = {
  session_token: "team-token",
  actor: { id: 2, username: "operator@example.com" },
  current_owner_scope: "team-a",
  role: "admin",
  available_scopes: [
    { owner_scope: "team-a", role: "admin" },
    { owner_scope: "team-b", role: "reviewer" },
  ],
};

describe("auth session product flow", () => {
  beforeEach(() => {
    window.localStorage.clear();
    vi.mocked(api.getProductSession).mockReset();
    vi.mocked(api.loginProductSession).mockReset();
    vi.mocked(api.switchProductScope).mockReset();
    push.mockReset();
    refresh.mockReset();
    searchParams = new URLSearchParams();
  });

  it("recovers and displays the local bootstrap session", async () => {
    vi.mocked(api.getProductSession).mockResolvedValue(bootstrapSession);

    render(
      <ProductSessionProvider>
        <AccountScopeSurface />
      </ProductSessionProvider>
    );

    expect(screen.getByText("Recovering session...")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("local-admin")).toBeInTheDocument());
    expect(screen.getByText("local bootstrap")).toBeInTheDocument();
    expect(screen.getByText(/Role: admin · Scope: local-default/)).toBeInTheDocument();
    expect(window.localStorage.getItem("decisionatlas-session-token")).toBe("boot-token");
  });

  it("shows login-required UI when session recovery returns 401", async () => {
    vi.mocked(api.getProductSession).mockRejectedValue(new api.ApiError("Authentication required", 401));

    render(
      <ProductSessionProvider>
        <AccountScopeSurface />
      </ProductSessionProvider>
    );

    await waitFor(() => expect(screen.getByText("Authentication required")).toBeInTheDocument());
    expect(screen.getByRole("link", { name: "Login" })).toHaveAttribute("href", "/login");
    expect(window.localStorage.getItem("decisionatlas-session-token")).toBeNull();
  });

  it("switches to an available owner scope and refreshes product state", async () => {
    const switchedSession = {
      ...multiScopeSession,
      current_owner_scope: "team-b",
      role: "reviewer",
    };
    vi.mocked(api.getProductSession).mockResolvedValue(multiScopeSession);
    vi.mocked(api.switchProductScope).mockResolvedValue(switchedSession);

    const user = userEvent.setup();
    render(
      <ProductSessionProvider>
        <AccountScopeSurface />
      </ProductSessionProvider>
    );

    await waitFor(() => expect(screen.getByText("operator@example.com")).toBeInTheDocument());
    await user.selectOptions(screen.getByLabelText(/Switch scope/i), "team-b");

    await waitFor(() => expect(api.switchProductScope).toHaveBeenCalledWith("team-b"));
    expect(refresh).toHaveBeenCalled();
    await waitFor(() => expect(screen.getByText(/Role: reviewer · Scope: team-b/)).toBeInTheDocument());
    expect(window.localStorage.getItem("decisionatlas-session-token")).toBe("team-token");
  });

  it("logs in and returns to the requested page", async () => {
    searchParams = new URLSearchParams({ next: "/workspaces/imported-workspace" });
    vi.mocked(api.getProductSession).mockRejectedValue(new api.ApiError("Authentication required", 401));
    vi.mocked(api.loginProductSession).mockResolvedValue(multiScopeSession);

    const user = userEvent.setup();
    render(
      <ProductSessionProvider>
        <LoginPanel />
      </ProductSessionProvider>
    );

    await user.type(screen.getByLabelText("Username"), "operator@example.com");
    await user.type(screen.getByLabelText("Password"), "secret");
    await user.click(screen.getByRole("button", { name: "Sign in" }));

    await waitFor(() =>
      expect(api.loginProductSession).toHaveBeenCalledWith("operator@example.com", "secret")
    );
    expect(window.localStorage.getItem("decisionatlas-session-token")).toBe("team-token");
    expect(push).toHaveBeenCalledWith("/workspaces/imported-workspace");
  });

  it("explains scoped unavailable workspace state", () => {
    render(<ScopedUnavailable workspaceSlug="team-a-private-repo" message="Failed to load dashboard summary" />);

    expect(screen.getByText("Workspace unavailable in current scope")).toBeInTheDocument();
    expect(screen.getByText("team-a-private-repo")).toBeInTheDocument();
    expect(screen.getByText(/Switch scope from the account panel/i)).toBeInTheDocument();
  });
});
