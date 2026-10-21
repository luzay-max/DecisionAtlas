"use client";

import Link from "next/link";
import React from "react";

import { AdvancedControls } from "../guided-demo/advanced-controls";
import { AccountScopeSurface } from "../auth/account-scope-surface";
import { LanguageToggle } from "../i18n/language-toggle";
import { useI18n } from "../i18n/language-provider";
import { ProviderModeToggle } from "../runtime/provider-mode-toggle";
import { ThemeToggle } from "../theme/theme-toggle";

export function DemoWorkspaceNav({
  workspaceSlug,
  currentPath,
}: {
  workspaceSlug: string;
  currentPath: string;
}) {
  const { messages } = useI18n();
  const isDemoWorkspace = workspaceSlug === "demo-workspace";

  const navItems = [
    { href: "/workspaces", label: messages.nav.dashboard },
    { href: "/review", label: messages.nav.review },
    { href: "/search", label: messages.nav.search },
    { href: "/timeline", label: messages.nav.timeline },
    { href: "/drift", label: messages.nav.drift },
  ];

  return (
    <nav className="demo-nav-shell workspace-nav-shell" aria-label={messages.nav.workspaceNavigation}>
      <div className="workspace-nav-primary">
        <div className="workspace-nav-context">
          <div>
            <p className="eyebrow">{isDemoWorkspace ? messages.guidedDemo.demoBadge : messages.nav.workspaceNavigation}</p>
            <p className="workspace-nav-name">{isDemoWorkspace ? messages.guidedDemo.title : workspaceSlug}</p>
            <p className="workspace-nav-description muted">
              {isDemoWorkspace ? messages.guidedDemo.demoSummary : messages.common.liveVsDemo}
            </p>
          </div>
          <div className="action-row workspace-nav-context-actions">
            <Link href="/" className="action-link">{messages.nav.home}</Link>
            {!isDemoWorkspace ? (
              <Link href="/workspaces/demo-workspace" className="action-link">{messages.nav.backToDemo}</Link>
            ) : null}
          </div>
        </div>
        <div className="demo-nav workspace-nav-tabs">
          {navItems.map((item) => {
            const href = item.href === "/workspaces"
              ? `/workspaces/${encodeURIComponent(workspaceSlug)}`
              : `${item.href}?workspace=${encodeURIComponent(workspaceSlug)}`;
            const isActive = item.href === "/workspaces"
              ? currentPath.startsWith("/workspaces/")
              : currentPath === item.href;

            return (
              <Link
                key={item.href}
                href={href}
                className={isActive ? "demo-nav-link active" : "demo-nav-link"}
                aria-current={isActive ? "page" : undefined}
              >
                {item.label}
              </Link>
            );
          })}
        </div>
      </div>
      <div className="workspace-nav-tools">
        <AccountScopeSurface />
        <div className="workspace-nav-switches">
          <LanguageToggle />
          <ThemeToggle />
        </div>
        <AdvancedControls>
          <ProviderModeToggle />
        </AdvancedControls>
      </div>
    </nav>
  );
}
