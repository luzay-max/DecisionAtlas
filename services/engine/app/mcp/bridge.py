"""Read-only, workspace-bound adapter for exposing reviewed decisions to MCP.

MCP clients never supply a workspace, authorization credential, or upstream URL
as a tool argument. An operator configures all three before launching stdio.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from urllib.parse import urlsplit

import httpx

_SESSION_HEADER = "x-decisionatlas-session-token"
_WORKSPACE = re.compile(r"^[A-Za-z0-9_-]{1,120}$")
_MAX_RESPONSE_BYTES = 2_000_000


class BridgeConfigurationError(ValueError):
    """An invalid local MCP configuration; contains no credential values."""


class DecisionServiceError(RuntimeError):
    """A sanitized backend error; never includes tokens or raw source data."""


@dataclass(frozen=True)
class BridgeSettings:
    api_url: str
    workspace_slug: str
    session_token: str

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> "BridgeSettings":
        env = os.environ if environ is None else environ
        api_url = env.get("DECISIONATLAS_MCP_API_URL", "http://127.0.0.1:8000")
        workspace = env.get("DECISIONATLAS_MCP_WORKSPACE", "")
        token = env.get("DECISIONATLAS_MCP_SESSION_TOKEN", "")
        try:
            parsed = urlsplit(api_url)
            port = parsed.port
        except ValueError:
            raise BridgeConfigurationError("Invalid local DecisionAtlas API URL") from None
        if (
            parsed.scheme != "http"
            or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path not in {"", "/"}
            or parsed.query or parsed.fragment
            or port is None or not 1 <= port <= 65535
        ):
            raise BridgeConfigurationError("MCP v0 supports only an explicit loopback HTTP API URL with port")
        if not _WORKSPACE.fullmatch(workspace):
            raise BridgeConfigurationError("Set a valid DECISIONATLAS_MCP_WORKSPACE")
        if not token or token != token.strip() or any(ord(ch) < 33 or ord(ch) == 127 for ch in token):
            raise BridgeConfigurationError("Set DECISIONATLAS_MCP_SESSION_TOKEN via a protected environment")
        return cls(api_url=api_url.rstrip("/"), workspace_slug=workspace, session_token=token)


class DecisionBridge:
    """A minimal consumer of existing Engine endpoints; never writes or imports."""

    def __init__(self, settings: BridgeSettings, *, client: httpx.Client | None = None) -> None:
        self.settings = settings
        self.client = client or httpx.Client(
            base_url=settings.api_url,
            timeout=8.0,
            follow_redirects=False,
            trust_env=False,
        )

    def _get(self, route: str, *, params: dict | None = None):
        if not route.startswith("/") or route.startswith("//"):
            raise ValueError("Invalid internal API route")
        try:
            response = self.client.get(
                route,
                params=params,
                headers={_SESSION_HEADER: self.settings.session_token},
                follow_redirects=False,
            )
        except httpx.RequestError:
            raise DecisionServiceError("Local DecisionAtlas API is unavailable") from None
        if response.is_redirect:
            raise DecisionServiceError("Local DecisionAtlas API redirected unexpectedly") from None
        if response.status_code == 401:
            raise DecisionServiceError("DecisionAtlas session is missing, expired, or invalid") from None
        if response.status_code in {403, 404}:
            raise DecisionServiceError("Workspace or decision not available to this identity") from None
        if response.status_code >= 400:
            raise DecisionServiceError(f"DecisionAtlas API error (HTTP {response.status_code})") from None
        if len(response.content) > _MAX_RESPONSE_BYTES:
            raise DecisionServiceError("DecisionAtlas API response exceeded the safety limit") from None
        try:
            return response.json()
        except ValueError:
            raise DecisionServiceError("DecisionAtlas API returned invalid JSON") from None

    def _accepted(self) -> list[dict]:
        items = self._get("/decisions", params={
            "workspace_slug": self.settings.workspace_slug,
            "review_state": "accepted",
        })
        if not isinstance(items, list):
            raise DecisionServiceError("DecisionAtlas API returned an invalid decision list")
        # Invariant: an accepted-only list is enforced both by the API and locally.
        return [d for d in items if isinstance(d, dict) and d.get("review_state") == "accepted"]

    @staticmethod
    def _summary(d: dict) -> dict:
        refs = d.get("review_evidence") if isinstance(d.get("review_evidence"), dict) else {}
        return {
            "decision_id": d.get("id"),
            "title": d.get("title"),
            "review_state": "accepted",
            "problem": d.get("problem"),
            "chosen_option": d.get("chosen_option"),
            "constraints": d.get("constraints"),
            "evidence_status": "accepted_with_source_refs" if refs.get("source_ref_count", 0) else "accepted_sources_missing",
            "source_ref_preview": refs.get("source_ref_preview", []),
        }

    def project_status(self) -> dict:
        decisions = self._accepted()
        return {
            "workspace_slug": self.settings.workspace_slug,
            "status": "accepted_decisions_available" if decisions else "no_accepted_decisions",
            "accepted_count": len(decisions),
            "read_only": True,
            "source": "DecisionAtlas authenticated Engine API",
            "note": "No accepted decisions does not prove that the repository was never imported.",
        }

    def list_project_decisions(self, limit: int = 20) -> dict:
        if limit < 1 or limit > 50:
            raise ValueError("limit must be between 1 and 50")
        accepted = self._accepted()
        return {
            "workspace_slug": self.settings.workspace_slug,
            "accepted_count": len(accepted),
            "items": [self._summary(d) for d in accepted[:limit]],
            "advisory_only": True,
            "note": "Accepted review state alone does not verify the quoted source evidence.",
        }

    def search_project_decisions(self, query: str, limit: int = 10) -> dict:
        if not query or len(query) > 500 or not query.strip() or not 1 <= limit <= 30:
            raise ValueError("Provide a non-empty question up to 500 characters and a limit of 1-30")
        # Lexical candidate ranking only; does not invoke paid models or claim semantic search.
        tokens = [tok.casefold() for tok in re.findall(r"\w+", query) if len(tok) > 1]
        if not tokens:
            return {"workspace_slug": self.settings.workspace_slug, "status": "insufficient_query", "items": []}
        scored = []
        for item in self._accepted():
            text = " ".join(str(item.get(key) or "") for key in
                            ("title", "problem", "context", "constraints", "chosen_option", "tradeoffs")).casefold()
            rank = sum(text.count(token) for token in set(tokens))
            if rank:
                scored.append((rank, item))
        scored.sort(key=lambda row: (-row[0], str(row[1].get("id"))))
        return {
            "workspace_slug": self.settings.workspace_slug,
            "status": "matched_accepted" if scored else "insufficient_evidence",
            "ranking": "basic_lexical_only",
            "items": [self._summary(item) for _, item in scored[:limit]],
            "advisory_only": True,
        }

    def get_decision_evidence(self, decision_id: int) -> dict:
        if decision_id < 1:
            raise ValueError("decision_id must be positive")
        # Resolve within the configured workspace BEFORE fetching a numeric ID.
        accepted_ids = {d.get("id") for d in self._accepted()}
        if decision_id not in accepted_ids:
            return {"status": "not_accepted_or_not_visible", "workspace_slug": self.settings.workspace_slug}
        decision = self._get(f"/decisions/{decision_id}")
        if not isinstance(decision, dict) or decision.get("review_state") != "accepted":
            return {"status": "not_accepted_or_not_visible", "workspace_slug": self.settings.workspace_slug}
        refs = decision.get("source_refs")
        if not isinstance(refs, list):
            refs = []
        return {
            "workspace_slug": self.settings.workspace_slug,
            "decision_id": decision_id,
            "review_state": "accepted",
            "status": "accepted_with_source_refs" if refs else "accepted_sources_missing",
            "problem": decision.get("problem"),
            "context": decision.get("context"),
            "constraints": decision.get("constraints"),
            "chosen_option": decision.get("chosen_option"),
            "tradeoffs": decision.get("tradeoffs"),
            "source_refs": [{
                "url": ref.get("url"),
                "quote": ref.get("quote"),
                "artifact_id": ref.get("artifact_id"),
                "span_start": ref.get("span_start"),
                "span_end": ref.get("span_end"),
            } for ref in refs[:15] if isinstance(ref, dict)],
            "advisory_only": True,
            "note": "The review state is human acceptance; independently verify the original sources before treating it as a hard constraint.",
        }
