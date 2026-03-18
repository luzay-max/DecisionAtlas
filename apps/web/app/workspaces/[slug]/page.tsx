import React from "react";

import { WorkspaceDashboardContent } from "../../../components/dashboard/workspace-dashboard-content";
import { DashboardSummary, getDashboardSummary } from "../../../lib/api";

export default async function WorkspaceDashboardPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const summary = await getDashboardSummary(slug);
  return <WorkspaceDashboardContent summary={summary} />;
}
