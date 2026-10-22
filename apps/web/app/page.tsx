"use client";

import Link from "next/link";
import React from "react";

import { AccountScopeSurface } from "../components/auth/account-scope-surface";
import { AdminOnly } from "../components/auth/role-gate";
import { GuidedDemoPanel } from "../components/guided-demo/guided-demo-panel";
import { AdvancedControls } from "../components/guided-demo/advanced-controls";
import { GitHubAppInstallationPanel } from "../components/github-app/github-app-installation-panel";
import { LiveAnalysisForm } from "../components/home/live-analysis-form";
import { LanguageToggle } from "../components/i18n/language-toggle";
import { PrivateRepoAccessPanel } from "../components/private-access/private-repo-access-panel";
import { useI18n } from "../components/i18n/language-provider";
import { ProviderModeToggle } from "../components/runtime/provider-mode-toggle";
import { ThemeToggle } from "../components/theme/theme-toggle";

export default function HomePage() {
  const { messages } = useI18n();
  const guidedDemoSteps = messages.guidedDemo.steps;

  return (
    <main className="home home-page" id="main-content">
      <div className="home-container">
        <header className="home-header">
          <Link href="/" className="home-brand">
            <span className="home-brand-symbol" aria-hidden="true">D<span>A</span></span>
            <span>DecisionAtlas</span>
          </Link>
          <div className="home-header-tools">
            <AccountScopeSurface compact />
            <LanguageToggle />
            <ThemeToggle />
          </div>
        </header>

        <section className="home-hero" aria-labelledby="home-title">
          <div className="home-hero-main">
            <p className="eyebrow">{messages.home.eyebrow}</p>
            <h1 id="home-title">{messages.home.title}</h1>
            <p className="lede">{messages.home.lede}</p>
            <div className="action-row home-hero-actions">
              <Link href="/workspaces/demo-workspace" className="action-link action-link-primary home-cta">
                {messages.home.openDemo} <span aria-hidden="true">→</span>
              </Link>
              <a href="#workflow" className="action-link home-secondary-cta">
                {messages.home.conceptsLabel} <span aria-hidden="true">↓</span>
              </a>
            </div>
            <p className="home-demo-caption">
              <span className="home-caption-dot" aria-hidden="true" />
              {messages.home.demoLabel}
            </p>
          </div>
          <aside className="home-path-preview" aria-label={messages.home.setupLabel}>
            <p className="home-path-kicker">{messages.home.setupLabel}</p>
            <ol>
              {messages.home.steps.map((step, index) => (
                <li key={step}>
                  <span className="home-path-number" aria-hidden="true">0{index + 1}</span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
          </aside>
        </section>

        <section className="home-workflow" id="workflow" aria-labelledby="home-workflow-title">
          <div className="home-section-heading">
            <div>
              <p className="eyebrow">{messages.home.conceptsLabel}</p>
              <h2 id="home-workflow-title">{messages.home.workflowHeading}</h2>
              <p className="muted">{messages.home.workflowHint}</p>
            </div>
            <ul className="pill-row" aria-label={messages.home.conceptsLabel}>
              {messages.home.pills.map((pill) => <li key={pill}>{pill}</li>)}
            </ul>
          </div>

          <div className="home-entry-grid">
            <div className="home-guided-card">
              <GuidedDemoPanel
                step={1}
                total={guidedDemoSteps.length}
                title={messages.guidedDemo.title}
                description={messages.guidedDemo.description}
                steps={guidedDemoSteps}
                status={messages.guidedDemo.demoSummary}
                nextHref="/workspaces/demo-workspace"
                nextLabel={messages.guidedDemo.openCta}
              />
            </div>

            <section className="home-shortcuts" aria-labelledby="home-shortcuts-title">
              <p className="eyebrow">{messages.guidedDemo.quickLinks}</p>
              <h2 id="home-shortcuts-title">{messages.home.quickActionsTitle}</h2>
              <p className="muted">{messages.home.quickActionsDescription}</p>
              <nav aria-label={messages.guidedDemo.quickLinks} className="home-shortcut-list">
                <Link href="/review?workspace=demo-workspace" className="home-shortcut-link">
                  {messages.home.jumpReview} <span aria-hidden="true">↗</span>
                </Link>
                <Link href="/search?workspace=demo-workspace" className="home-shortcut-link">
                  {messages.home.jumpSearch} <span aria-hidden="true">↗</span>
                </Link>
                <Link href="/drift?workspace=demo-workspace" className="home-shortcut-link">
                  {messages.home.jumpDrift} <span aria-hidden="true">↗</span>
                </Link>
                <Link href="/team" className="home-shortcut-link">
                  {messages.home.teamAdmin} <span aria-hidden="true">↗</span>
                </Link>
              </nav>
            </section>
          </div>
          <p className="home-product-note">{messages.home.note}</p>
        </section>

        <section className="home-experimental" aria-label={messages.advanced.summary}>
          <AdvancedControls id="advanced-controls">
            <div className="action-row home-toolbar">
              <ProviderModeToggle />
            </div>
            <section className="stack">
              <p className="eyebrow">{messages.liveAnalysis.eyebrow}</p>
              <h2>{messages.liveAnalysis.title}</h2>
              <AdminOnly>
                <LiveAnalysisForm />
              </AdminOnly>
              <GitHubAppInstallationPanel />
              <PrivateRepoAccessPanel />
            </section>
          </AdvancedControls>
        </section>
      </div>
    </main>
  );
}
