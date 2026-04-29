import { GovernancePageContent } from "../../components/governance/governance-page-content";
import { listGovernanceDocuments, listGovernanceRules } from "../../lib/api";

export default async function GovernancePage() {
  try {
    const [documents, rules] = await Promise.all([listGovernanceDocuments(), listGovernanceRules()]);
    return <GovernancePageContent initialDocuments={documents} initialRules={rules} />;
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to load governance state";
    return <main className="panel"><p>{message}</p></main>;
  }
}
