"use client";

import Link from "next/link";
import React from "react";

import { AdvancedControls } from "../components/guided-demo/advanced-controls";
import { AdminOnly } from "../components/auth/role-gate";
import { GuidedDemoPanel } from "../components/guided-demo/guided-demo-panel";
import { GitHubAppInstallationPanel } from "../components/github-app/github-app-installation-panel";
import { LiveAnalysisForm } from "../components/home/live-analysis-form";
import { RepositoryImportFlowGuide } from "../components/home/repository-import-flow-guide";
import { RoleAwareWorkbench } from "../components/home/role-aware-workbench";
import { GlobalSidebar } from "../components/navigation/global-sidebar";
import { PrivateRepoAccessPanel } from "../components/private-access/private-repo-access-panel";
import { useI18n } from "../components/i18n/language-provider";
import { ProviderModeToggle } from "../components/runtime/provider-mode-toggle";

export default function HomePage() {
  const { messages } = useI18n();
  const guidedDemoSteps = messages.guidedDemo.steps;

  return (
    <>
      <GlobalSidebar />
      <main className="page-with-sidebar">
        <div className="panel" style={{ background: "transparent", backdropFilter: "none", WebkitBackdropFilter: "none", boxShadow: "none", border: "none", maxWidth: "960px" }}>
        
        {/* Hero Section */}
        <div style={{ textAlign: "center", marginBottom: "80px", position: "relative" }}>
          {/* Animated Glow Behind Hero */}
          <div style={{
            position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)",
            width: "60vw", height: "60vw", maxWidth: "800px", maxHeight: "800px", 
            background: "radial-gradient(circle, var(--accent-glow) 0%, transparent 60%)",
            filter: "blur(60px)", zIndex: -1, pointerEvents: "none"
          }}></div>
          
          <p className="eyebrow" style={{ fontSize: "0.85rem", letterSpacing: "0.2em", marginBottom: "20px" }}>{messages.home.eyebrow}</p>
          <h1 style={{ fontSize: "clamp(2.5rem, 5vw, 4.5rem)", lineHeight: 1.1, letterSpacing: "-0.04em", marginBottom: "24px" }}>
            {messages.home.title}
          </h1>
          <p className="lede" style={{ fontSize: "1.25rem", maxWidth: "600px", margin: "0 auto" }}>
            {messages.home.lede}
          </p>
        </div>

        {/* Bento Grid for Concepts & Steps */}
        <div className="bento-grid" style={{ marginBottom: "48px" }}>
          {/* Getting Started Box */}
          <div className="bento-item" style={{ animationDelay: "0ms", gridColumn: "span 2" }}>
            <h3 style={{ fontSize: "1.5rem", marginBottom: "8px" }}>{messages.home.gettingStarted}</h3>
            <p className="muted" style={{ marginBottom: "20px", lineHeight: 1.6 }}>{messages.home.gettingStartedDescription}</p>
            <div style={{ display: "grid", gap: "16px" }}>
              {[
                { title: messages.home.step1Title, desc: messages.home.step1Description },
                { title: messages.home.step2Title, desc: messages.home.step2Description },
                { title: messages.home.step3Title, desc: messages.home.step3Description },
                { title: messages.home.step4Title, desc: messages.home.step4Description },
              ].map((step) => (
                <div key={step.title} style={{ padding: "12px 16px", background: "var(--card-bg)", borderRadius: "12px", border: "1px solid var(--line)" }}>
                  <p style={{ fontWeight: 600, marginBottom: "4px" }}>{step.title}</p>
                  <p className="muted" style={{ fontSize: "0.9rem", margin: 0 }}>{step.desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Concepts Box */}
          <div className="bento-item" style={{ animationDelay: "0ms" }}>
            <h3 style={{ fontSize: "1.5rem", marginBottom: "8px" }}>{messages.home.conceptsLabel}</h3>
            <ul className="pill-row" aria-label={messages.home.conceptsLabel} style={{ marginTop: "16px" }}>
              {messages.home.pills.map((pill) => (
                <li key={pill}>{pill}</li>
              ))}
            </ul>
          </div>

          {/* Steps Box - spans multiple rows or columns depending on grid */}
          <div className="bento-item" style={{ animationDelay: "100ms", gridRow: "span 2" }}>
            <h3 style={{ fontSize: "1.5rem", marginBottom: "16px" }}>How it works</h3>
            <ol style={{ paddingLeft: "24px", display: "flex", flexDirection: "column", gap: "16px" }}>
              {messages.home.steps.map((step) => (
                <li key={step} style={{ color: "var(--muted)", lineHeight: 1.6 }}>
                  {step}
                </li>
              ))}
            </ol>
            <p style={{ marginTop: "auto", paddingTop: "16px", color: "var(--accent)", fontWeight: 500 }}>
              {messages.home.note}
            </p>
          </div>

          {/* Quick Links Box */}
          <div className="bento-item" style={{ animationDelay: "200ms" }}>
            <h3 style={{ fontSize: "1.5rem", marginBottom: "16px" }}>Quick Actions</h3>
            <div className="action-row" style={{ flexWrap: "wrap", gap: "12px" }} aria-label={messages.guidedDemo.quickLinks}>
              <Link href="/review?workspace=demo-workspace" className="action-link shimmer-btn" style={{ padding: "12px 24px", minWidth: "44px", minHeight: "44px", display: "flex", alignItems: "center", borderRadius: "99px" }}>
                {messages.home.jumpReview}
              </Link>
              <Link href="/search?workspace=demo-workspace" className="action-link shimmer-btn" style={{ padding: "12px 24px", minWidth: "44px", minHeight: "44px", display: "flex", alignItems: "center", borderRadius: "99px" }}>
                {messages.home.jumpSearch}
              </Link>
              <Link href="/drift?workspace=demo-workspace" className="action-link shimmer-btn" style={{ padding: "12px 24px", minWidth: "44px", minHeight: "44px", display: "flex", alignItems: "center", borderRadius: "99px" }}>
                {messages.home.jumpDrift}
              </Link>
              <Link href="/evidence" className="action-link shimmer-btn" style={{ padding: "12px 24px", minWidth: "44px", minHeight: "44px", display: "flex", alignItems: "center", borderRadius: "99px" }}>
                Evidence Center
              </Link>
            </div>
          </div>
        </div>

        <div style={{ animation: "enterFromBottom 0.6s cubic-bezier(0.16, 1, 0.3, 1) backwards", animationDelay: "250ms", marginBottom: "48px" }}>
          <RoleAwareWorkbench />
        </div>

        <div style={{ animation: "enterFromBottom 0.6s cubic-bezier(0.16, 1, 0.3, 1) backwards", animationDelay: "275ms", marginBottom: "48px" }}>
          <RepositoryImportFlowGuide />
        </div>

        {/* Guided Demo Panel - Takes full width below bento grid */}
        <div style={{ animation: "enterFromBottom 0.6s cubic-bezier(0.16, 1, 0.3, 1) backwards", animationDelay: "300ms", marginBottom: "48px" }}>
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
        
        <div style={{ animation: "enterFromBottom 0.6s cubic-bezier(0.16, 1, 0.3, 1) backwards", animationDelay: "400ms" }}>
          <AdvancedControls id="advanced-controls">
            <div className="action-row home-toolbar" style={{ marginBottom: "24px" }}>
              <ProviderModeToggle />
            </div>
            <section className="stack">
              <p className="eyebrow">{messages.liveAnalysis.eyebrow}</p>
              <h2>{messages.liveAnalysis.title}</h2>
              <AdminOnly>
                <LiveAnalysisForm />
                <GitHubAppInstallationPanel />
                <PrivateRepoAccessPanel />
              </AdminOnly>
            </section>
          </AdvancedControls>
        </div>

        {/* Next Steps Section */}
        <div style={{ animation: "enterFromBottom 0.6s cubic-bezier(0.16, 1, 0.3, 1) backwards", animationDelay: "500ms", marginTop: "48px" }}>
          <div className="card" style={{ textAlign: "center", padding: "32px" }}>
            <h3 style={{ fontSize: "1.3rem", marginBottom: "8px" }}>{messages.home.nextSteps}</h3>
            <p className="muted" style={{ marginBottom: "20px" }}>{messages.home.nextStepsDescription}</p>
            <div className="action-row" style={{ justifyContent: "center", flexWrap: "wrap", gap: "12px" }}>
              <Link href="/#advanced-controls" className="action-link shimmer-btn" style={{ padding: "12px 24px", borderRadius: "99px" }}>
                {messages.home.analyzeRepo}
              </Link>
              <Link href="/settings" className="action-link shimmer-btn" style={{ padding: "12px 24px", borderRadius: "99px" }}>
                {messages.home.viewSettings}
              </Link>
              <Link href="/evidence" className="action-link shimmer-btn" style={{ padding: "12px 24px", borderRadius: "99px" }}>
                {messages.home.viewEvidence}
              </Link>
            </div>
          </div>
        </div>
      </div>
      </main>
    </>
  );
}
