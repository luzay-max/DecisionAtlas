"use client";

import Link from "next/link";
import React from "react";

import { LiveAnalysisForm } from "../components/home/live-analysis-form";
import { LanguageToggle } from "../components/i18n/language-toggle";
import { useI18n } from "../components/i18n/language-provider";

export default function HomePage() {
  const { messages } = useI18n();

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
        <p>
          <Link href="/workspaces/demo-workspace">{messages.home.openDemo}</Link>
        </p>
        <section className="card stack">
          <p className="eyebrow">{messages.liveAnalysis.eyebrow}</p>
          <h2>{messages.liveAnalysis.title}</h2>
          <LiveAnalysisForm />
        </section>
        <div className="action-row">
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
      </div>
    </main>
  );
}
