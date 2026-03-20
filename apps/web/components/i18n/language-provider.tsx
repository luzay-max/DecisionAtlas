"use client";

import React, { createContext, useContext, useEffect, useMemo, useState } from "react";

import { Language, messages } from "./messages";

const STORAGE_KEY = "decisionatlas-language";

type LanguageContextValue = {
  language: Language;
  setLanguage: (language: Language) => void;
  toggleLanguage: () => void;
  messages: (typeof messages)[Language];
};

const fallbackContext: LanguageContextValue = {
  language: "en",
  setLanguage: () => {},
  toggleLanguage: () => {},
  messages: messages.en,
};

const LanguageContext = createContext<LanguageContextValue | null>(null);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<Language>("en");

  useEffect(() => {
    const storedLanguage = window.localStorage.getItem(STORAGE_KEY);
    if (storedLanguage === "en" || storedLanguage === "zh") {
      setLanguageState(storedLanguage);
    }
  }, []);

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, language);
    document.documentElement.lang = language;
  }, [language]);

  const value = useMemo<LanguageContextValue>(
    () => ({
      language,
      setLanguage: setLanguageState,
      toggleLanguage: () => {
        setLanguageState((current) => (current === "en" ? "zh" : "en"));
      },
      messages: messages[language],
    }),
    [language]
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useI18n() {
  return useContext(LanguageContext) ?? fallbackContext;
}
