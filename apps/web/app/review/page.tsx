import React from "react";

import { getReviewQueue, ReviewDecision } from "../../lib/api";
import { ReviewPageContent } from "../../components/review/review-page-content";

export default async function ReviewPage({
  searchParams,
}: {
  searchParams?: Promise<{ workspace?: string }>;
}) {
  const params = (await searchParams) ?? {};
  const workspaceSlug = params.workspace ?? "demo-workspace";
  const decisions = await getReviewQueue(workspaceSlug);
  return <ReviewPageContent decisions={decisions} workspaceSlug={workspaceSlug} />;
}
