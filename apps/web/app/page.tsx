"use client";

import Link from "next/link";
import React from "react";

import { AdvancedControls } from "../components/guided-demo/advanced-controls";
import { GuidedDemoPanel } from "../components/guided-demo/guided-demo-panel";
import { LiveAnalysisForm } from "../components/home/live-analysis-form";
import { LanguageToggle } from "../components/i18n/language-toggle";
import { useI18n } from "../components/i18n/language-provider";
import { ProviderModeToggle } from "../components/runtime/provider-mode-toggle";

export default function HomePage() {
  const { messages } = useI18n();
  const guidedDemoSteps = messages.guidedDemo.steps;

  return (
    <main className="home">
      <div className="panel">
        <div className="action-row home-toolbar">
          <LanguageToggle />
        </div>
        <p className="eyebrow">{messages.home.eyebrow}</p>
        <h1>{messages.home.title}</h1>
        <p className="lede">{messages.home.lede}</p>
        <ul className="pill-row" aria-label={messages.home.conceptsLabel}>
          {messages.home.pills.map((pill) => (
            <li key={pill}>{pill}</li>
          ))}
        </ul>
        <ol>
          {messages.home.steps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
        <p>{messages.home.note}</p>
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
        <div className="action-row" aria-label={messages.guidedDemo.quickLinks}>
          <Link href="/review?workspace=demo-workspace" className="action-link">
            {messages.home.jumpReview}
          </Link>
          <Link href="/search?workspace=demo-workspace" className="action-link">
            {messages.home.jumpSearch}
          </Link>
          <Link href="/drift?workspace=demo-workspace" className="action-link">
            {messages.home.jumpDrift}
          </Link>
        </div>
        <AdvancedControls id="advanced-controls">
          <div className="action-row home-toolbar">
            <ProviderModeToggle />
          </div>
          <section className="stack">
            <p className="eyebrow">{messages.liveAnalysis.eyebrow}</p>
            <h2>{messages.liveAnalysis.title}</h2>
            <LiveAnalysisForm />
          </section>
        </AdvancedControls>
      </div>
    </main>
  );
}
