"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { getGovernanceGuardrail, AgentGuardrailResult } from "../../lib/api";
import { useI18n } from "../i18n/language-provider";

export function GuardrailPauseBanner({ workspaceSlug }: { workspaceSlug: string }) {
  const { language, messages } = useI18n();
  const isZh = language === "zh";
  const [guardrail, setGuardrail] = useState<AgentGuardrailResult | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isDismissed, setIsDismissed] = useState<boolean>(false);

  useEffect(() => {
    async function loadGuardrail() {
      try {
        setLoading(true);
        const result = await getGovernanceGuardrail();
        setGuardrail(result);
      } catch (err) {
        // Fallback for demo-workspace or network-isolated modes
        console.warn("Failed to fetch guardrail status:", err);
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setLoading(false);
      }
    }
    loadGuardrail();
  }, [workspaceSlug]);

  if (isDismissed || loading || error || !guardrail) {
    return null;
  }

  const { agent_status, summary, findings = [], signals = [], human_questions = [] } = guardrail;

  const translations: Record<string, string> = {
    "Governance guardrail requires human review before the agent continues.": "治理守卫要求在智能体继续前进行人工审核。",
    "Governance guardrail found advisory concerns; the agent may continue only after addressing recommended actions.": "治理守卫发现建议性问题；智能体在处理完推荐操作后方可继续。",
    "The AI agent has automatically paused code execution because current changes violate established architecture policies or active OpenSpec specifications. Human intervention is required.": "AI 智能体已自动暂停代码执行，因为当前修改违反了既定的架构策略或生效的 OpenSpec 规范。需要人类介入评估。",
    "Advisory rules or non-blocking drift detected. You may proceed, but addressing the recommendations is highly advised before merge.": "检测到建议性规则或非阻塞性漂移。您可以继续执行，但强烈建议在合并前处理这些建议。",
    "Code changes need OpenSpec context": "代码变更需要 OpenSpec 上下文",
    "Validation evidence is missing": "缺失验证证据",
    "Should this behavior change get OpenSpec context before implementation continues?": "在继续实现之前，此行为变更是否需要 OpenSpec 上下文？",
    "What validation evidence is required before the agent may continue or claim completion?": "在智能体继续或声明完成之前，需要什么验证证据？",
  };

  const t = (text: string) => {
    if (!isZh || !text) return text;
    if (translations[text]) return translations[text];
    if (text.startsWith("Current code changes have no active OpenSpec change. Affected paths:")) {
      return text.replace("Current code changes have no active OpenSpec change. Affected paths:", "当前代码变更没有活跃的 OpenSpec 变更。受影响的路径：");
    }
    if (text.startsWith("Code paths changed, but no test, fixture, or spec-test paths were changed in the current diff.")) {
      return text.replace("Code paths changed, but no test, fixture, or spec-test paths were changed in the current diff.", "代码路径已更改，但在当前 diff 中未更改任何测试、fixture 或 spec-test 路径。");
    }
    return text;
  };

  // We only show the blocker/caution banner if it is not "continue"
  if (agent_status === "continue") {
    return null;
  }

  const isPause = agent_status === "pause";
  const theme = isPause
    ? {
        bgColor: "rgba(239, 68, 68, 0.08)",
        borderColor: "#ef4444",
        glowColor: "rgba(239, 68, 68, 0.4)",
        badgeColor: "#ef4444",
        badgeText: "AI GOVERNANCE: PAUSED (治理阻断)",
        titleColor: "#fecaca",
        actionBtnColor: "#ef4444",
      }
    : {
        bgColor: "rgba(245, 158, 11, 0.08)",
        borderColor: "#f59e0b",
        glowColor: "rgba(245, 158, 11, 0.4)",
        badgeColor: "#f59e0b",
        badgeText: "AI GOVERNANCE: CAUTION (治理劝诫)",
        titleColor: "#fef3c7",
        actionBtnColor: "#f59e0b",
      };

  return (
    <div style={{ ...styles.card, backgroundColor: theme.bgColor, borderColor: theme.borderColor, boxShadow: `0 0 20px ${theme.glowColor}` }}>
      <style dangerouslySetInnerHTML={{ __html: styles.keyframes }} />
      
      {/* Frosted Glass Background & Saturator overlay */}
      <div style={styles.frostedOverlay} />

      <div style={styles.contentContainer}>
        {/* Pulsating Indicator Badge */}
        <div style={styles.header}>
          <div style={styles.badgeWrapper}>
            <span style={{ ...styles.badge, backgroundColor: theme.badgeColor }}>
              {theme.badgeText}
            </span>
            <span style={{ ...styles.pulsingRing, borderColor: theme.badgeColor }} />
          </div>
          <button style={styles.closeBtn} onClick={() => setIsDismissed(true)}>
            {isZh ? "忽略" : "Dismiss"} ×
          </button>
        </div>

        {/* Core Summary Text */}
        <h3 style={{ ...styles.title, color: theme.titleColor }}>{t(summary)}</h3>
        
        <p style={styles.intro}>
          {isPause
            ? t("The AI agent has automatically paused code execution because current changes violate established architecture policies or active OpenSpec specifications. Human intervention is required.")
            : t("Advisory rules or non-blocking drift detected. You may proceed, but addressing the recommendations is highly advised before merge.")}
        </p>

        {/* Evidence & Diff Block Section */}
        {findings.length > 0 && (
          <div style={styles.section}>
            <h4 style={styles.sectionTitle}>🔍 证据溯源与偏差段落 (Evidence Code Excerpts & Diff)</h4>
            <div style={styles.findingsGrid}>
              {findings.map((finding, idx) => (
                <div key={`finding-${idx}`} style={styles.findingItem}>
                  <div style={styles.findingHead}>
                    <span style={styles.findingSeverity}>{finding.severity.toUpperCase()}</span>
                    <strong style={styles.findingTitle}>{t(finding.title)}</strong>
                  </div>
                  <p style={styles.findingDetail}>{t(finding.detail)}</p>
                  
                  {finding.source?.excerpt && (
                    <pre style={styles.codeSnippet}>
                      <code>{finding.source.excerpt}</code>
                    </pre>
                  )}
                  {finding.source?.title && (
                    <div style={styles.sourceRef}>
                      Source: <span style={styles.sourcePath}>{finding.source.title}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Drift Signals Section */}
        {signals.length > 0 && (
          <div style={styles.section}>
            <h4 style={styles.sectionTitle}>⚠️ 检测到决策漂移信号 (Detected Decision Drift)</h4>
            <div style={styles.signalsList}>
              {signals.map((signal, idx) => (
                <div key={`signal-${idx}`} style={styles.signalItem}>
                  <div style={styles.signalHead}>
                    <span style={styles.signalType}>{signal.type}</span>
                    <span style={styles.signalTitle}>{t(signal.title)}</span>
                    {(signal.occurrence_count ?? 1) > 1 ? (
                      <span style={styles.signalRecurrence}>
                        {isZh
                          ? "重复 " + signal.occurrence_count + " 次 · " + (signal.source_count ?? 1) + " 个来源"
                          : "Repeated " + signal.occurrence_count + " times · " + (signal.source_count ?? 1) + " sources"}
                      </span>
                    ) : null}
                  </div>
                  {signal.recommended_next_action && (
                    <p style={styles.signalAction}>
                      👉 <strong>Action:</strong> {signal.recommended_next_action}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Human Decisions Needed Section */}
        {human_questions.length > 0 && (
          <div style={styles.section}>
            <h4 style={styles.sectionTitle}>🙋 需要人类拍板的具体问题 (Decisions Required by Human)</h4>
            <ul style={styles.questionsList}>
              {human_questions.map((question) => (
                <li key={question.id} style={styles.questionItem}>
                  <input type="checkbox" id={question.id} style={styles.checkbox} />
                  <label htmlFor={question.id} style={styles.questionLabel}>
                    {t(question.question)}
                    {question.evidence_summary && (
                      <span style={styles.questionSub}>{t(question.evidence_summary)}</span>
                    )}
                  </label>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Interactive resolution links */}
        <div style={styles.footer}>
          <Link
            href={`/governance?workspace=${encodeURIComponent(workspaceSlug)}`}
            style={{ ...styles.resolveBtn, backgroundColor: theme.badgeColor }}
          >
            Review Governance Rules & Decisions / 前往治理审阅页 →
          </Link>
          <div style={styles.cliHelp}>
            {isZh ? "本地运行预检：" : "Run preflight locally:"} <code>python scripts/governance/agent_guardrail.py --agent</code>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  card: {
    position: "relative" as const,
    border: "1px solid",
    borderRadius: "12px",
    padding: "24px",
    marginTop: "20px",
    marginBottom: "24px",
    overflow: "hidden" as const,
    boxShadow: "0 10px 30px -5px rgba(0, 0, 0, 0.5)",
  },
  frostedOverlay: {
    position: "absolute" as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(11, 19, 41, 0.4)",
    backdropFilter: "blur(12px) saturate(180%)",
    zIndex: 1,
  },
  contentContainer: {
    position: "relative" as const,
    zIndex: 2,
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "16px",
  },
  badgeWrapper: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    position: "relative" as const,
  },
  badge: {
    fontSize: "11px",
    fontWeight: "bold" as const,
    color: "#fff",
    padding: "4px 10px",
    borderRadius: "20px",
    letterSpacing: "0.5px",
  },
  pulsingRing: {
    position: "absolute" as const,
    left: "0",
    top: "0",
    right: "0",
    bottom: "0",
    border: "1px solid",
    borderRadius: "20px",
    animation: "topology-pulse 2s infinite ease-in-out",
    pointerEvents: "none" as const,
  },
  closeBtn: {
    backgroundColor: "transparent",
    border: "none",
    color: "#94a3b8",
    fontSize: "12px",
    cursor: "pointer",
    padding: "4px 8px",
    borderRadius: "4px",
    transition: "color 0.2s",
  },
  title: {
    fontSize: "18px",
    fontWeight: "600" as const,
    margin: "0 0 10px 0",
    lineHeight: "1.4",
  },
  intro: {
    fontSize: "13px",
    color: "#cbd5e1",
    lineHeight: "1.6",
    margin: "0 0 20px 0",
  },
  section: {
    marginTop: "20px",
    borderTop: "1px solid rgba(148, 163, 184, 0.15)",
    paddingTop: "16px",
  },
  sectionTitle: {
    fontSize: "12.5px",
    fontWeight: "600" as const,
    color: "#f8fafc",
    margin: "0 0 12px 0",
    letterSpacing: "0.3px",
  },
  findingsGrid: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "14px",
  },
  findingItem: {
    backgroundColor: "rgba(15, 23, 42, 0.7)",
    borderRadius: "8px",
    padding: "14px",
    border: "1px solid rgba(148, 163, 184, 0.1)",
  },
  findingHead: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    marginBottom: "8px",
  },
  findingSeverity: {
    fontSize: "9px",
    fontWeight: "bold" as const,
    backgroundColor: "#ef4444",
    color: "#fff",
    padding: "2px 6px",
    borderRadius: "4px",
  },
  findingTitle: {
    fontSize: "13px",
    color: "#f1f5f9",
  },
  findingDetail: {
    fontSize: "12px",
    color: "#cbd5e1",
    margin: "0 0 10px 0",
    lineHeight: "1.5",
  },
  codeSnippet: {
    backgroundColor: "#050b18",
    padding: "10px 14px",
    borderRadius: "6px",
    border: "1px solid #1e293b",
    fontSize: "11px",
    color: "#64ffda",
    overflowX: "auto" as const,
    fontFamily: "monospace",
    margin: "0 0 8px 0",
  },
  sourceRef: {
    fontSize: "11px",
    color: "#94a3b8",
  },
  sourcePath: {
    color: "#f8fafc",
    fontWeight: "500" as const,
  },
  signalRecurrence: {
    display: "inline-flex",
    alignItems: "center",
    border: "1px solid rgba(245, 158, 11, 0.45)",
    borderRadius: "999px",
    padding: "2px 8px",
    fontSize: "11px",
    color: "#fef3c7",
    whiteSpace: "nowrap",
  },
  signalsList: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "8px",
  },
  signalItem: {
    backgroundColor: "rgba(15, 23, 42, 0.5)",
    borderLeft: "3px solid #ff9f43",
    padding: "10px 14px",
    borderRadius: "0 6px 6px 0",
  },
  signalHead: {
    display: "flex",
    gap: "10px",
    alignItems: "center",
    marginBottom: "4px",
  },
  signalType: {
    fontSize: "9px",
    fontWeight: "bold" as const,
    color: "#ff9f43",
    textTransform: "uppercase" as const,
  },
  signalTitle: {
    fontSize: "12px",
    fontWeight: "600" as const,
    color: "#f1f5f9",
  },
  signalAction: {
    fontSize: "11.5px",
    color: "#cbd5e1",
    margin: 0,
  },
  questionsList: {
    listStyle: "none",
    padding: 0,
    margin: 0,
    display: "flex",
    flexDirection: "column" as const,
    gap: "10px",
  },
  questionItem: {
    display: "flex",
    alignItems: "flex-start",
    gap: "10px",
  },
  checkbox: {
    marginTop: "4px",
    accentColor: "#ef4444",
    cursor: "pointer",
  },
  questionLabel: {
    fontSize: "12.5px",
    color: "#f1f5f9",
    lineHeight: "1.5",
    cursor: "pointer",
    display: "flex",
    flexDirection: "column" as const,
    gap: "2px",
  },
  questionSub: {
    fontSize: "11px",
    color: "#94a3b8",
  },
  footer: {
    marginTop: "24px",
    display: "flex",
    flexDirection: "column" as const,
    gap: "12px",
    alignItems: "flex-start",
  },
  resolveBtn: {
    padding: "10px 20px",
    borderRadius: "6px",
    color: "#fff",
    fontSize: "12.5px",
    fontWeight: "600" as const,
    textDecoration: "none",
    transition: "transform 0.15s, opacity 0.2s",
    boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.2)",
    cursor: "pointer",
  },
  cliHelp: {
    fontSize: "11px",
    color: "#94a3b8",
    display: "flex",
    alignItems: "center",
    gap: "6px",
  },
  keyframes: `
    @keyframes topology-pulse {
      0%, 100% {
        transform: scale(1);
        opacity: 0.8;
      }
      50% {
        transform: scale(1.08);
        opacity: 0.3;
      }
    }
  `
};
