"use client";

import React from "react";

import { ProductSessionProvider } from "../components/auth/session-provider";
import { LanguageProvider } from "../components/i18n/language-provider";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <LanguageProvider>
      <ProductSessionProvider>{children}</ProductSessionProvider>
    </LanguageProvider>
  );
}
