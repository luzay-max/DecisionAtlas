"use client";

import React from "react";

import { SourceRef } from "../../lib/api";
import { EvidenceReviewPanel } from "../evidence/evidence-review-panel";

export function SourceRefList({ sourceRefs }: { sourceRefs: SourceRef[] }) {
  return <EvidenceReviewPanel sourceRefs={sourceRefs} />;
}
