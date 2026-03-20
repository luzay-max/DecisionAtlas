"use client";

import Link from "next/link";
import React from "react";

import { LanguageToggle } from "../i18n/language-toggle";
import { useI18n } from "../i18n/language-provider";

export function DemoWorkspaceNav({
  workspaceSlug,
  currentPath,
}: {
  workspaceSlug: string;
  currentPath: string;
}) {
  const { messages } = useI18n();

  const navItems = [
    { href: "/workspaces", label: messages.nav.dashboard },
    { href: "/review", label: messages.nav.review },
    { href: "/search", label: messages.nav.search },
    { href: "/timeline", label: messages.nav.timeline },
    { href: "/drift", label: messages.nav.drift },
  ];

  return (
    <nav className="demo-nav-shell" aria-label={messages.nav.workspaceNavigation}>
      <div className="demo-nav">
        {navItems.map((item) => {
          const href =
            item.href === "/workspaces"
              ? `/workspaces/${workspaceSlug}`
              : `${item.href}?workspace=${encodeURIComponent(workspaceSlug)}`;
          const isActive =
            item.href === "/workspaces" ? currentPath.startsWith("/workspaces/") : currentPath === item.href;

          return (
            <Link key={item.href} href={href} className={isActive ? "demo-nav-link active" : "demo-nav-link"}>
              {item.label}
            </Link>
          );
        })}
      </div>
      <LanguageToggle />
    </nav>
  );
}
