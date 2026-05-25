"use client";

import React from "react";

import { ProductSessionProvider } from "../components/auth/session-provider";
import { LanguageProvider } from "../components/i18n/language-provider";
import { ThemeProvider } from "../components/theme/theme-provider";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <LanguageProvider>
      <ThemeProvider>
        <ProductSessionProvider>{children}</ProductSessionProvider>
      </ThemeProvider>
    </LanguageProvider>
  );
}
