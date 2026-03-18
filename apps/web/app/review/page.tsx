import React from "react";

import { getReviewQueue, ReviewDecision } from "../../lib/api";
import { ReviewPageContent } from "../../components/review/review-page-content";

export default async function ReviewPage() {
  const decisions = await getReviewQueue("demo-workspace");
  return <ReviewPageContent decisions={decisions} />;
}
