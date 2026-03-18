import Link from "next/link";
import React from "react";

const navItems = [
  { href: "/workspaces", label: "Dashboard" },
  { href: "/review", label: "Review" },
  { href: "/search", label: "Why Search" },
  { href: "/timeline", label: "Timeline" },
  { href: "/drift", label: "Drift" },
];

export function DemoWorkspaceNav({
  workspaceSlug,
  currentPath,
}: {
  workspaceSlug: string;
  currentPath: string;
}) {
  return (
    <nav className="demo-nav" aria-label="Workspace navigation">
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
    </nav>
  );
}
