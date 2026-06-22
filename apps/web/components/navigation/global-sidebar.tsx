"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import React from "react";

import { AccountScopeSurface } from "../auth/account-scope-surface";
import { LanguageToggle } from "../i18n/language-toggle";
import { useI18n } from "../i18n/language-provider";
import { ThemeToggle } from "../theme/theme-toggle";

const NAV_ITEMS = [
  { href: "/", labelKey: "home", icon: "◈" },
  { href: "/review", labelKey: "review", icon: "◉" },
  { href: "/search", labelKey: "search", icon: "◎" },
  { href: "/timeline", labelKey: "timeline", icon: "◇" },
  { href: "/drift", labelKey: "drift", icon: "◆" },
  { href: "/governance", labelKey: "governance", icon: "◇" },
  { href: "/team", labelKey: "team", icon: "◈" },
  { href: "/settings", labelKey: "settings", icon: "⚙" },
  { href: "/evidence", labelKey: "evidence", icon: "📊" },
] as const;

export function GlobalSidebar() {
  const pathname = usePathname();
  const { messages } = useI18n();

  const navLabelMap: Record<string, string> = {
    home: messages.nav.home,
    review: messages.nav.review,
    search: messages.nav.search,
    timeline: messages.nav.timeline,
    drift: messages.nav.drift,
    governance: messages.governance?.title || "Governance",
    team: "Team",
    settings: "Settings",
    evidence: "Evidence",
  };

  function isActive(href: string): boolean {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  }

  return (
    <aside className="global-sidebar" aria-label="Global navigation">
      <div className="sidebar-header">
        <Link href="/" className="sidebar-logo">
          <span className="sidebar-logo-icon">◈</span>
          <span className="sidebar-logo-text">DecisionAtlas</span>
        </Link>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`sidebar-nav-link${isActive(item.href) ? " active" : ""}`}
          >
            <span className="sidebar-nav-icon">{item.icon}</span>
            <span className="sidebar-nav-label">{navLabelMap[item.labelKey]}</span>
          </Link>
        ))}
      </nav>

      <div className="sidebar-footer">
        <AccountScopeSurface />
        <div className="sidebar-controls">
          <LanguageToggle />
          <ThemeToggle />
        </div>
      </div>
    </aside>
  );
}
