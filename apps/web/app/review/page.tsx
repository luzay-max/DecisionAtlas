import React from "react";

import { ScopedUnavailable } from "../../components/auth/scoped-unavailable";
import { getReviewQueue, ReviewDecision } from "../../lib/api";
import { ReviewPageContent } from "../../components/review/review-page-content";

export default async function ReviewPage({
  searchParams,
}: {
  searchParams?: Promise<{ workspace?: string }>;
}) {
  const params = (await searchParams) ?? {};
  const workspaceSlug = params.workspace ?? "demo-workspace";
  try {
    const decisions = await getReviewQueue(workspaceSlug);
    return <ReviewPageContent decisions={decisions} workspaceSlug={workspaceSlug} />;
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to load review queue";
    return <ScopedUnavailable workspaceSlug={workspaceSlug} message={message} />;
  }
}
