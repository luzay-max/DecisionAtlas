import React from "react";

import { GlobalSidebar } from "../../components/navigation/global-sidebar";
import { TeamManagementPanel } from "../../components/auth/team-management-panel";

export default function TeamPage() {
  return (
    <>
      <GlobalSidebar />
      <main className="page-with-sidebar">
        <div className="panel">
          <TeamManagementPanel />
        </div>
      </main>
    </>
  );
}
