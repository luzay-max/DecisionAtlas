"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import {
  ApiError,
  ProductSession,
  getProductSession,
  loginProductSession,
  switchProductScope,
} from "../../lib/api";

type SessionStatus = "loading" | "ready" | "unauthenticated" | "error";

type ProductSessionContextValue = {
  session: ProductSession | null;
  status: SessionStatus;
  error: string | null;
  refreshSession: () => Promise<ProductSession | null>;
  login: (username: string, password: string) => Promise<ProductSession>;
  switchScope: (ownerScope: string) => Promise<ProductSession>;
  canManageWorkspace: boolean;
  canReviewWorkspace: boolean;
};

const ProductSessionContext = createContext<ProductSessionContextValue | null>(null);

function canManage(session: ProductSession | null) {
  return session?.role === "admin";
}

function canReview(session: ProductSession | null) {
  return session?.role === "admin" || session?.role === "reviewer";
}

export function ProductSessionProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [session, setSession] = useState<ProductSession | null>(null);
  const [status, setStatus] = useState<SessionStatus>("loading");
  const [error, setError] = useState<string | null>(null);

  async function refreshSession() {
    setError(null);
    try {
      const nextSession = await getProductSession();
      setSession(nextSession);
      setStatus("ready");
      return nextSession;
    } catch (refreshError) {
      setSession(null);
      if (refreshError instanceof ApiError && refreshError.status === 401) {
        setStatus("unauthenticated");
        setError("Authentication required");
        return null;
      }
      setStatus("error");
      setError(refreshError instanceof Error ? refreshError.message : "Failed to recover session");
      return null;
    }
  }

  async function login(username: string, password: string) {
    const nextSession = await loginProductSession(username, password);
    setSession(nextSession);
    setStatus("ready");
    setError(null);
    router.refresh();
    return nextSession;
  }

  async function switchScope(ownerScope: string) {
    const nextSession = await switchProductScope(ownerScope);
    setSession(nextSession);
    setStatus("ready");
    setError(null);
    router.refresh();
    return nextSession;
  }

  useEffect(() => {
    void refreshSession();
  }, []);

  return (
    <ProductSessionContext.Provider
      value={{
        session,
        status,
        error,
        refreshSession,
        login,
        switchScope,
        canManageWorkspace: canManage(session),
        canReviewWorkspace: canReview(session),
      }}
    >
      {children}
    </ProductSessionContext.Provider>
  );
}

export function useProductSession() {
  const value = useContext(ProductSessionContext);
  if (value) {
    return value;
  }

  return {
    session: null,
    status: "ready" as const,
    error: null,
    refreshSession: async () => null,
    login: async () => {
      throw new Error("Product session provider is not mounted");
    },
    switchScope: async () => {
      throw new Error("Product session provider is not mounted");
    },
    canManageWorkspace: true,
    canReviewWorkspace: true,
  };
}
