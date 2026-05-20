import React from "react";

import { AccountScopeSurface } from "../../components/auth/account-scope-surface";
import { TeamManagementPanel } from "../../components/auth/team-management-panel";

export default function TeamPage() {
  return (
    <main className="page-shell">
      <div className="panel">
        <AccountScopeSurface />
        <TeamManagementPanel />
      </div>
    </main>
  );
}
