import React from "react";

import { DriftPageContent } from "../../components/drift/drift-page-content";
import { getDriftAlerts } from "../../lib/api";

export default async function DriftPage() {
  const alerts = await getDriftAlerts("demo-workspace");
  return <DriftPageContent alerts={alerts} />;
}
