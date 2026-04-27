"use client";

import React from "react";

import { useProductSession } from "./session-provider";

export function AdminOnly({
  children,
  fallback = "Admin role required for import and workspace management actions.",
}: {
  children: React.ReactNode;
  fallback?: string;
}) {
  const { status, session, canManageWorkspace } = useProductSession();

  if (status === "loading") {
    return <p className="guided-demo-status">Checking workspace permissions...</p>;
  }

  if (session && !canManageWorkspace) {
    return <p className="guided-demo-status">{fallback}</p>;
  }

  return <>{children}</>;
}

export function ReviewOnly({
  children,
  fallback = "Reviewer or admin role required for review actions.",
}: {
  children: React.ReactNode;
  fallback?: string;
}) {
  const { status, session, canReviewWorkspace } = useProductSession();

  if (status === "loading") {
    return <p className="guided-demo-status">Checking workspace permissions...</p>;
  }

  if (session && !canReviewWorkspace) {
    return <p className="guided-demo-status">{fallback}</p>;
  }

  return <>{children}</>;
}
