"use client";

import React, { useState, useMemo } from "react";
import Link from "next/link";
import { TimelineItem } from "../../lib/api";

type Node = {
  id: number;
  title: string;
  reviewState: string;
  problem: string;
  chosenOption: string;
  tradeoffs: string;
  createdAt: string | null;
  x: number;
  y: number;
  scope: "engine" | "api" | "frontend" | "docs" | "other";
  color: string;
};

type ScopeNode = {
  name: string;
  label: string;
  x: number;
  y: number;
  color: string;
  desc: string;
};

export function DecisionTopologyMap({ items, workspaceSlug }: { items: TimelineItem[]; workspaceSlug: string }) {
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [hoveredNode, setHoveredNode] = useState<number | null>(null);

  // Define scope anchor nodes
  const scopes: ScopeNode[] = useMemo(() => [
    { name: "engine", label: "services/engine", x: 150, y: 80, color: "#ff9f43", desc: "FastAPI Engine, pgvector & drift computation" },
    { name: "api", label: "apps/api", x: 450, y: 70, color: "#00d2d3", desc: "Fastify Edge API & owner boundary" },
    { name: "frontend", label: "apps/web", x: 750, y: 90, color: "#a55eea", desc: "Next.js Web UI & interactive maps" },
    { name: "docs", label: "docs/ADRs", x: 450, y: 330, color: "#10ac84", desc: "OpenSpec specifications & roadmap documents" }
  ], []);

  // Compute positions of decision nodes dynamically clustered under scopes
  const nodes: Node[] = useMemo(() => {
    const sorted = [...items].sort((a, b) => {
      const ta = a.created_at ? new Date(a.created_at).getTime() : 0;
      const tb = b.created_at ? new Date(b.created_at).getTime() : 0;
      return ta - tb;
    });

    return sorted.map((item, index) => {
      // Classify scope based on title/problem content
      const text = `${item.title} ${item.problem} ${item.chosen_option}`.lowerCaseSafe();
      let scopeType: "engine" | "api" | "frontend" | "docs" | "other" = "other";
      if (text.includes("engine") || text.includes("python") || text.includes("vector") || text.includes("drift")) {
        scopeType = "engine";
      } else if (text.includes("api") || text.includes("fastify") || text.includes("auth") || text.includes("session")) {
        scopeType = "api";
      } else if (text.includes("web") || text.includes("next") || text.includes("ui") || text.includes("page") || text.includes("timeline")) {
        scopeType = "frontend";
      } else if (text.includes("doc") || text.includes("spec") || text.includes("rule") || text.includes("adr")) {
        scopeType = "docs";
      }

      // Base anchor coordinate from scope
      const anchor = scopes.find(s => s.name === scopeType) || { x: 450, y: 200, color: "#ff9f43" };

      // Calculate an offset clustered around the anchor chronologically
      const count = sorted.length || 1;
      const angle = (index / count) * 2 * Math.PI + (scopeType === "engine" ? 0.5 : 2.5);
      const radius = 65 + (index % 2) * 15; // varying radiuses to avoid overlaps

      const x = Math.min(Math.max(anchor.x + Math.cos(angle) * radius, 60), 840);
      const y = Math.min(Math.max(anchor.y + Math.sin(angle) * radius, 140), 290);

      // Map color by review state
      let color = "#ff9f43"; // candidate: amber
      if (item.review_state === "accepted") color = "#00d2d3"; // accepted: cyan/teal
      else if (item.review_state === "superseded") color = "#a55eea"; // superseded: purple
      else if (item.review_state === "rejected") color = "#ee5253"; // rejected: red

      return {
        id: item.id,
        title: item.title,
        reviewState: item.review_state,
        problem: item.problem,
        chosenOption: item.chosen_option,
        tradeoffs: item.tradeoffs,
        createdAt: item.created_at,
        x,
        y,
        scope: scopeType,
        color
      };
    });
  }, [items, scopes]);

  // Compute connections chronologically between nodes within the same scope
  const chronologicalLinks = useMemo(() => {
    const links: Array<{ from: Node; to: Node; color: string }> = [];
    // Link nodes of same scope chronologically
    scopes.forEach(scope => {
      const scopeNodes = nodes.filter(n => n.scope === scope.name);
      for (let i = 0; i < scopeNodes.length - 1; i++) {
        links.push({
          from: scopeNodes[i],
          to: scopeNodes[i + 1],
          color: scope.color
        });
      }
    });
    return links;
  }, [nodes, scopes]);

  return (
    <div className="topology-card" style={styles.container}>
      <style dangerouslySetInnerHTML={{ __html: styles.keyframes }} />
      <div style={styles.header}>
        <h2 style={styles.headerTitle}>🔗 Decision Topology Map / 决策网络拓扑图</h2>
        <p style={styles.headerSub}>
          Interactive spatial map showing how architectural decisions cluster under codebase modules and connect chronologically.
        </p>
      </div>

      <div style={styles.canvasWrapper}>
        <svg
          viewBox="0 0 900 380"
          style={styles.svg}
          onClick={() => setSelectedNode(null)}
        >
          {/* Neon glow filters */}
          <defs>
            <filter id="neon-glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="5" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            <filter id="soft-shadow" x="-10%" y="-10%" width="120%" height="120%">
              <feDropShadow dx="0" dy="4" stdDeviation="4" floodColor="#000" floodOpacity="0.4" />
            </filter>
            <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
              <path d="M 30 0 L 0 0 0 30" fill="none" stroke="var(--topology-grid-stroke, #222f3e)" strokeWidth="0.5" />
            </pattern>
          </defs>

          {/* Grid Background */}
          <rect width="100%" height="100%" fill="url(#grid)" />

          {/* Grid Subtle Center Glow */}
          <circle cx="450" cy="190" r="280" fill="radial-gradient(circle, rgba(16,172,132,0.03) 0%, transparent 70%)" pointerEvents="none" />

          {/* Scope Anchor Connections (Scopes -> Center Anchor) */}
          {scopes.map((scope, idx) => (
            <line
              key={`scope-line-${idx}`}
              x1="450"
              y1="190"
              x2={scope.x}
              y2={scope.y}
              stroke="var(--line, #2d3748)"
              strokeWidth="1.5"
              strokeDasharray="4, 4"
            />
          ))}

          {/* Chronological Links */}
          {chronologicalLinks.map((link, idx) => {
            const isSelected = selectedNode?.id === link.from.id || selectedNode?.id === link.to.id;
            const isHovered = hoveredNode === link.from.id || hoveredNode === link.to.id;
            
            // Draw flowing cubic or quadratic bezier curve
            const midX = (link.from.x + link.to.x) / 2;
            const midY = (link.from.y + link.to.y) / 2 - 15;
            const pathData = `M ${link.from.x} ${link.from.y} Q ${midX} ${midY} ${link.to.x} ${link.to.y}`;

            return (
              <g key={`link-${idx}`}>
                {/* Background thicker glow when hovered */}
                {(isHovered || isSelected) && (
                  <path
                    d={pathData}
                    fill="none"
                    stroke={link.color}
                    strokeWidth="4"
                    opacity="0.3"
                    filter="url(#neon-glow)"
                  />
                )}
                {/* Core animated curve line */}
                <path
                  d={pathData}
                  fill="none"
                  stroke={link.color}
                  strokeWidth={isHovered || isSelected ? 2 : 1.2}
                  opacity={isSelected ? 1 : isHovered ? 0.8 : 0.25}
                  className="flow-line"
                  style={{
                    strokeDasharray: (isHovered || isSelected) ? "6, 4" : "none",
                    animation: (isHovered || isSelected) ? "topology-flow 1.5s linear infinite" : "none"
                  }}
                />
              </g>
            );
          })}

          {/* Scope Anchor Nodes */}
          {scopes.map((scope, idx) => (
            <g key={`scope-${idx}`} style={{ cursor: "default" }}>
              <circle
                cx={scope.x}
                cy={scope.y}
                r="10"
                fill="var(--topology-canvas-bg, #1a202c)"
                stroke={scope.color}
                strokeWidth="2.5"
                filter="url(#soft-shadow)"
              />
              <circle
                cx={scope.x}
                cy={scope.y}
                r="4"
                fill={scope.color}
                filter="url(#neon-glow)"
              />
              <text
                x={scope.x}
                y={scope.y - 18}
                textAnchor="middle"
                fill="var(--topology-text-main, #f7fafc)"
                fontSize="11"
                fontWeight="600"
                letterSpacing="0.5px"
                style={{ textShadow: "0 2px 4px var(--bg)" }}
              >
                {scope.label}
              </text>
            </g>
          ))}

          {/* Central Hub Core */}
          <g>
            <circle cx="450" cy="190" r="14" fill="var(--topology-canvas-bg, #0f172a)" stroke="#10ac84" strokeWidth="2" filter="url(#neon-glow)" />
            <circle cx="450" cy="190" r="6" fill="#10ac84" />
            <text x="450" y="222" textAnchor="middle" fill="#10ac84" fontSize="10" fontWeight="bold" letterSpacing="1px">
              DECISION ATLAS
            </text>
          </g>

          {/* Decision Nodes */}
          {nodes.map((node) => {
            const isHovered = hoveredNode === node.id;
            const isSelected = selectedNode?.id === node.id;
            
            // Outer dynamic connecting lines to scopes
            const anchor = scopes.find(s => s.name === node.scope) || { x: 450, y: 190 };
            
            return (
              <g
                key={`node-${node.id}`}
                transform={`translate(${node.x}, ${node.y})`}
                style={{ cursor: "pointer" }}
                onMouseEnter={() => setHoveredNode(node.id)}
                onMouseLeave={() => setHoveredNode(null)}
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedNode(node);
                }}
              >
                {/* Thin connection line back to scope anchor */}
                <line
                  x1={anchor.x - node.x}
                  y1={anchor.y - node.y}
                  x2="0"
                  y2="0"
                  stroke={node.color}
                  strokeWidth="0.8"
                  opacity={isSelected ? 0.7 : isHovered ? 0.5 : 0.15}
                  strokeDasharray="2, 2"
                />

                {/* Pulsating glowing ring on hover or select */}
                {(isHovered || isSelected) && (
                  <circle
                    r={isSelected ? "14" : "11"}
                    fill="none"
                    stroke={node.color}
                    strokeWidth="2"
                    opacity="0.5"
                    filter="url(#neon-glow)"
                    style={{
                      animation: "topology-pulse 2s infinite ease-in-out"
                    }}
                  />
                )}

                {/* Node main dot */}
                <circle
                  r={isSelected ? "8" : "6"}
                  fill="var(--topology-canvas-bg, #0f172a)"
                  stroke={node.color}
                  strokeWidth={isSelected ? "3" : "2"}
                  filter="url(#soft-shadow)"
                />

                {/* Small indicator inner center */}
                <circle r="2.5" fill={node.color} opacity={isSelected ? 1 : 0.7} />

                {/* Floating Node Label */}
                {(isHovered || isSelected) && (
                  <g transform="translate(0, -18)">
                    <rect
                      x="-80"
                      y="-12"
                      width="160"
                      height="20"
                      rx="4"
                      fill="var(--topology-panel-bg, #1e293b)"
                      stroke="var(--line, #475569)"
                      strokeWidth="0.5"
                      opacity="0.95"
                    />
                    <text
                      textAnchor="middle"
                      fill="var(--topology-text-main, #f1f5f9)"
                      fontSize="9"
                      fontWeight="500"
                      y="1"
                    >
                      {node.title.length > 30 ? `${node.title.substring(0, 27)}...` : node.title}
                    </text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>

        {/* Legend overlays */}
        <div style={styles.legend}>
          <div style={styles.legendItem}>
            <span style={{ ...styles.legendDot, backgroundColor: "#00d2d3" }} />
            <span style={styles.legendText}>Accepted (已采纳)</span>
          </div>
          <div style={styles.legendItem}>
            <span style={{ ...styles.legendDot, backgroundColor: "#ff9f43" }} />
            <span style={styles.legendText}>Candidate (候选)</span>
          </div>
          <div style={styles.legendItem}>
            <span style={{ ...styles.legendDot, backgroundColor: "#a55eea" }} />
            <span style={styles.legendText}>Superseded (已废弃/替换)</span>
          </div>
          <div style={styles.legendItem}>
            <span style={{ ...styles.legendDot, backgroundColor: "#ee5253" }} />
            <span style={styles.legendText}>Rejected (已驳回)</span>
          </div>
        </div>
      </div>

      {/* Floating Side Info Panel when a Node is Clicked */}
      {selectedNode && (
        <div style={styles.panelCard}>
          <div style={styles.panelHeader}>
            <div style={styles.panelTitleWrapper}>
              <span style={{ ...styles.panelBadge, backgroundColor: selectedNode.color }}>
                {selectedNode.reviewState.toUpperCase()}
              </span>
              <h3 style={styles.panelTitle}>{selectedNode.title}</h3>
            </div>
            <button style={styles.closeBtn} onClick={() => setSelectedNode(null)}>×</button>
          </div>
          
          <div style={styles.panelBody}>
            <div style={styles.panelItem}>
              <span style={styles.panelLabel}>Scope (所属范围):</span>
              <span style={styles.panelVal}>{selectedNode.scope.toUpperCase()}</span>
            </div>
            {selectedNode.createdAt && (
              <div style={styles.panelItem}>
                <span style={styles.panelLabel}>Date (沉淀日期):</span>
                <span style={styles.panelVal}>{new Date(selectedNode.createdAt).toLocaleDateString()}</span>
              </div>
            )}
            <div style={styles.panelBlock}>
              <span style={styles.panelLabel}>Problem Context (背景问题):</span>
              <p style={styles.panelText}>{selectedNode.problem}</p>
            </div>
            <div style={styles.panelBlock}>
              <span style={styles.panelLabel}>Chosen Option (最终决定):</span>
              <p style={styles.panelText}>{selectedNode.chosenOption}</p>
            </div>
            {selectedNode.tradeoffs && (
              <div style={styles.panelBlock}>
                <span style={styles.panelLabel}>Tradeoffs (权衡取舍):</span>
                <p style={styles.panelText}>{selectedNode.tradeoffs}</p>
              </div>
            )}
            
            <div style={styles.actions}>
              <Link
                href={`/decisions/${selectedNode.id}?workspace=${encodeURIComponent(workspaceSlug)}`}
                style={{ ...styles.viewBtn, borderColor: selectedNode.color }}
              >
                View Full Decision & Evidence / 查看完整证据 →
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Extension to string to avoid typescript error on lowercase
declare global {
  interface String {
    lowerCaseSafe(): string;
  }
}
String.prototype.lowerCaseSafe = function() {
  return this ? this.toLowerCase() : "";
};

const styles = {
  container: {
    position: "relative" as const,
    backgroundColor: "var(--topology-container-bg, #0b1329)",
    border: "1px solid var(--line, #1e293b)",
    borderRadius: "12px",
    padding: "20px",
    marginTop: "24px",
    marginBottom: "24px",
    boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.4)",
    overflow: "hidden" as const,
  },
  header: {
    marginBottom: "15px",
  },
  headerTitle: {
    fontSize: "16px",
    fontWeight: "600" as const,
    color: "var(--topology-text-main, #f8fafc)",
    margin: 0,
  },
  headerSub: {
    fontSize: "12px",
    color: "var(--topology-text-sub, #94a3b8)",
    margin: "4px 0 0 0",
  },
  canvasWrapper: {
    position: "relative" as const,
    backgroundColor: "var(--topology-canvas-bg, #050b18)",
    borderRadius: "8px",
    border: "1px solid var(--line, #0f172a)",
    overflow: "hidden" as const,
  },
  svg: {
    width: "100%",
    height: "auto",
    display: "block",
  },
  legend: {
    position: "absolute" as const,
    bottom: "10px",
    left: "10px",
    display: "flex",
    flexWrap: "wrap" as const,
    gap: "12px",
    backgroundColor: "var(--topology-legend-bg, rgba(15, 23, 42, 0.8))",
    padding: "6px 12px",
    borderRadius: "6px",
    backdropFilter: "blur(4px)",
    border: "1px solid var(--line, #1e293b)",
  },
  legendItem: {
    display: "flex",
    alignItems: "center",
    gap: "6px",
  },
  legendDot: {
    width: "7px",
    height: "7px",
    borderRadius: "50%",
    display: "inline-block",
  },
  legendText: {
    fontSize: "9px",
    color: "var(--topology-text-sub, #cbd5e1)",
    fontWeight: "500" as const,
  },
  panelCard: {
    position: "absolute" as const,
    top: "80px",
    right: "20px",
    width: "320px",
    maxHeight: "280px",
    overflowY: "auto" as const,
    backgroundColor: "var(--topology-panel-bg, rgba(15, 23, 42, 0.95))",
    backdropFilter: "blur(12px)",
    borderRadius: "8px",
    border: "1px solid var(--line, #334155)",
    boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.6)",
    padding: "16px",
    zIndex: 10,
    animation: "topology-slide-in 0.3s cubic-bezier(0.16, 1, 0.3, 1)",
  },
  panelHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    borderBottom: "1px solid var(--line, #1e293b)",
    paddingBottom: "10px",
    marginBottom: "12px",
  },
  panelTitleWrapper: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "6px",
    maxWidth: "250px",
  },
  panelBadge: {
    alignSelf: "flex-start",
    fontSize: "8px",
    fontWeight: "bold" as const,
    color: "#fff",
    padding: "2px 6px",
    borderRadius: "4px",
    letterSpacing: "0.5px",
  },
  panelTitle: {
    fontSize: "13px",
    fontWeight: "600" as const,
    color: "var(--topology-text-main, #f8fafc)",
    margin: 0,
    lineHeight: "1.4",
  },
  closeBtn: {
    border: "none",
    background: "none",
    color: "#94a3b8",
    fontSize: "18px",
    cursor: "pointer",
    padding: "0 4px",
  },
  panelBody: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "10px",
  },
  panelItem: {
    display: "flex",
    justifyContent: "space-between",
    fontSize: "10px",
  },
  panelLabel: {
    color: "var(--topology-text-sub, #94a3b8)",
    fontWeight: "500" as const,
  },
  panelVal: {
    color: "var(--topology-text-main, #cbd5e1)",
    fontWeight: "600" as const,
  },
  panelBlock: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "3px",
  },
  panelText: {
    fontSize: "10.5px",
    color: "var(--topology-text-main, #e2e8f0)",
    margin: 0,
    lineHeight: "1.4",
    backgroundColor: "var(--card-bg, #0f172a)",
    padding: "6px 8px",
    borderRadius: "4px",
    border: "1px solid var(--line, #1e293b)",
  },
  actions: {
    marginTop: "6px",
  },
  viewBtn: {
    display: "block",
    width: "100%",
    padding: "8px 10px",
    borderRadius: "6px",
    backgroundColor: "var(--card-bg, #1e293b)",
    border: "1px solid var(--line, transparent)",
    color: "var(--topology-text-main, #f8fafc)",
    fontSize: "10px",
    fontWeight: "600" as const,
    textAlign: "center" as const,
    textDecoration: "none",
    transition: "all 0.2s",
  },
  keyframes: `
    @keyframes topology-flow {
      to {
        stroke-dashoffset: -20;
      }
    }
    @keyframes topology-pulse {
      0%, 100% {
        transform: scale(1);
        opacity: 0.5;
      }
      50% {
        transform: scale(1.15);
        opacity: 0.25;
      }
    }
    @keyframes topology-slide-in {
      from {
        transform: translateX(30px);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
  `
};
