"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import React from "react";

import { AccountScopeSurface } from "../auth/account-scope-surface";
import { LanguageToggle } from "../i18n/language-toggle";
import { useI18n } from "../i18n/language-provider";
import { ThemeToggle } from "../theme/theme-toggle";

const GLOBAL_NAV_ITEMS = [
  { href: "/", labelKey: "home", icon: "◈" },
  { href: "/governance", labelKey: "governance", icon: "◇" },
  { href: "/team", labelKey: "team", icon: "◈" },
  { href: "/settings", labelKey: "settings", icon: "⚙" },
  { href: "/evidence", labelKey: "evidence", icon: "📊" },
] as const;

const WORKSPACE_NAV_ITEMS = [
  { path: "/workspaces", labelKey: "dashboard", icon: "□" },
  { path: "/review", labelKey: "review", icon: "◉" },
  { path: "/search", labelKey: "search", icon: "◎" },
  { path: "/timeline", labelKey: "timeline", icon: "◇" },
  { path: "/drift", labelKey: "drift", icon: "◆" },
] as const;

export function GlobalSidebar({ workspaceSlug }: { workspaceSlug?: string }) {
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
    dashboard: messages.nav.dashboard,
  };

  function isGlobalActive(href: string): boolean {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  }

  function isWorkspaceActive(path: string): boolean {
    if (path === "/workspaces") return pathname.startsWith("/workspaces/");
    return pathname.startsWith(path);
  }

  function workspaceHref(path: string): string {
    if (!workspaceSlug) return path;
    if (path === "/workspaces") return `/workspaces/${workspaceSlug}`;
    return `${path}?workspace=${encodeURIComponent(workspaceSlug)}`;
  }

  return (
    <aside className="global-sidebar" aria-label="Global navigation">
      <div className="sidebar-header">
        <Link href="/" className="sidebar-logo">
          <span className="sidebar-logo-icon">◈</span>
          <span className="sidebar-logo-text">DecisionAtlas</span>
        </Link>
      </div>

      {workspaceSlug ? (
        <div className="sidebar-section">
          <p className="sidebar-section-label">{workspaceSlug}</p>
          <nav className="sidebar-nav">
            {WORKSPACE_NAV_ITEMS.map((item) => (
              <Link
                key={item.path}
                href={workspaceHref(item.path)}
                className={`sidebar-nav-link${isWorkspaceActive(item.path) ? " active" : ""}`}
              >
                <span className="sidebar-nav-icon">{item.icon}</span>
                <span className="sidebar-nav-label">{navLabelMap[item.labelKey]}</span>
              </Link>
            ))}
          </nav>
        </div>
      ) : null}

      <div className="sidebar-section">
        <p className="sidebar-section-label">Navigation</p>
        <nav className="sidebar-nav">
          {GLOBAL_NAV_ITEMS.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`sidebar-nav-link${isGlobalActive(item.href) ? " active" : ""}`}
            >
              <span className="sidebar-nav-icon">{item.icon}</span>
              <span className="sidebar-nav-label">{navLabelMap[item.labelKey]}</span>
            </Link>
          ))}
        </nav>
      </div>

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
