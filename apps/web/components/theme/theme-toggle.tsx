"use client";

import React from "react";
import { useTheme } from "./theme-provider";
import { useI18n } from "../i18n/language-provider";

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const { language } = useI18n();

  const label =
    language === "zh"
      ? theme === "dark"
        ? "深色模式"
        : "浅色模式"
      : theme === "dark"
      ? "Dark Mode"
      : "Light Mode";

  return (
    <button
      onClick={toggleTheme}
      className="theme-toggle"
      aria-label={label}
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        gap: "8px",
        padding: "8px 16px",
        borderRadius: "999px",
        cursor: "pointer",
        transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        fontWeight: 600,
        fontSize: "0.85rem",
      }}
    >
      <span
        style={{
          display: "inline-block",
          position: "relative",
          width: "18px",
          height: "18px",
          transition: "transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)",
          transform: theme === "dark" ? "rotate(0deg)" : "rotate(360deg)",
        }}
      >
        {theme === "dark" ? (
          // 太阳图标 - 深色模式下用于切换至浅色
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{ width: "100%", height: "100%", color: "#fbbf24" }}
          >
            <circle cx="12" cy="12" r="4" />
            <path d="M12 2v2" />
            <path d="M12 20v2" />
            <path d="m4.93 4.93 1.41 1.41" />
            <path d="m17.66 17.66 1.41 1.41" />
            <path d="M2 12h2" />
            <path d="M20 12h2" />
            <path d="m6.34 17.66-1.41 1.41" />
            <path d="m19.07 4.93-1.41 1.41" />
          </svg>
        ) : (
          // 月亮图标 - 浅色模式下用于切换至深色
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{ width: "100%", height: "100%", color: "#6366f1" }}
          >
            <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
          </svg>
        )}
      </span>
      <span style={{ fontSize: "0.85rem" }}>{label}</span>
    </button>
  );
}
