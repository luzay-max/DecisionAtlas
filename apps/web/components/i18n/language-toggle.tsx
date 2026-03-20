"use client";

import React from "react";

import { useI18n } from "./language-provider";

export function LanguageToggle() {
  const { language, toggleLanguage, messages } = useI18n();

  return (
    <button
      type="button"
      className="language-toggle"
      onClick={toggleLanguage}
      aria-label={messages.common.language}
      title={language === "en" ? messages.common.switchToChinese : messages.common.switchToEnglish}
    >
      <span className={language === "en" ? "language-toggle-active" : ""}>EN</span>
      <span aria-hidden="true">/</span>
      <span className={language === "zh" ? "language-toggle-active" : ""}>中文</span>
    </button>
  );
}
