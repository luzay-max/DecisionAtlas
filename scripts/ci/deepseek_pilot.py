"""Bounded DeepSeek compatibility pilot. DRY-RUN by default, network-free for AI.

Real DeepSeek calls require --live AND DEEPSEEK_PILOT_APPROVED AND an API key.
This is a two-PR adapter smoke experiment, NOT a full DecisionAtlas/Why/Drift
benchmark and not a money-denominated provider spending guarantee.
"""
from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import sys
from typing import Any
from urllib.request import Request, urlopen

import httpx

ENGINE = Path(__file__).resolve().parents[2] / "services" / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from app.llm.base import ExtractionRequest
from app.llm.openai_compatible import OpenAICompatibleProvider


MODEL = "deepseek-flash"
API_BASE = "https://api.deepseek.com"
REPOSITORY = "pallets/click"
PR_NUMBERS = (3877, 3884)
MAX_REQUESTS = 2
MAX_REQUEST_BYTES = 5000
MAX_OUTPUT_TOKENS = 768
MAX_ESTIMATED_USD = 0.10
# Conservative published October 2026 peak rates; prices can change.
PEAK_INPUT_USD_PER_M = 0.30
PEAK_OUTPUT_USD_PER_M = 1.20
APPROVAL = "YES_I_APPROVE_DEEPSEEK_API_CHARGES"

# These are static synthetic summaries ONLY for zero-network DRY-RUN.
# Live tests fetch the real public PR bodies and do not rely on these fixtures.
DRY_FIXTURES = {
    3877: {
        "title": "Parameter spec and name distinctions",
        "body": "The public declaration, readable help spec and internal parameter name serve different audiences. Separate them to avoid ambiguous semantics.",
        "decision": "Distinguish parameter names for different audiences.",
        "quote": "The public declaration, readable help spec and internal parameter name serve different audiences.",
    },
    3884: {
        "title": "Environment variable help text",
        "body": "Do not show an empty environment variable help label. List-valued environment variables should be rendered in human-readable form.",
        "decision": "Make environment variable help output readable.",
        "quote": "Do not show an empty environment variable help label.",
    },
}


class PilotGuardError(RuntimeError):
    pass


def get_public_pr(number: int, *, live: bool) -> dict[str, str]:
    if number not in PR_NUMBERS:
        raise PilotGuardError("Repository sample outside approved allowlist")
    url = f"https://github.com/pallets/click/pull/{number}"
    if not live:
        return {"number": number, "url": url, **DRY_FIXTURES[number], "source": "synthetic_dry_run"}
    request = Request(
        f"https://api.github.com/repos/pallets/click/pulls/{number}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "DecisionAtlas-DeepSeek-Pilot",
            **({"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"}
               if os.environ.get("GITHUB_TOKEN") else {}),
        },
    )
    with urlopen(request, timeout=15) as response:
        payload = json.load(response)
    if payload.get("number") != number or (payload.get("base") or {}).get("repo", {}).get("full_name") != REPOSITORY:
        raise PilotGuardError("GitHub PR identity did not match allowlist")
    return {
        "number": number, "url": url, "source": "live_public_github",
        "title": str(payload.get("title") or "")[:300],
        "body": str(payload.get("body") or "")[:3000],
    }


class GuardedChatClient:
    """Only permits bounded chat/completions calls; no retries or other endpoints."""

    def __init__(self, *, live: bool, api_key: str | None) -> None:
        self.live = live
        self.calls = 0
        self.estimated_upper_usd = 0.0
        self.observed_prompt_tokens = 0
        self.observed_completion_tokens = 0
        if live:
            if os.environ.get("DEEPSEEK_PILOT_APPROVED") != APPROVAL:
                raise PilotGuardError("Explicit paid API approval is missing")
            if not api_key:
                raise PilotGuardError("DeepSeek pilot API key is missing")
            self.client = httpx.Client(
                base_url=API_BASE, timeout=25, trust_env=False,
                follow_redirects=False,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            )
        else:
            def mock_chat(request: httpx.Request) -> httpx.Response:
                body = json.loads(request.content)
                text = body["messages"][1]["content"]
                number = 3877 if "PR #3877" in text else 3884
                fixture = DRY_FIXTURES[number]
                answer = json.dumps({
                    "decision": fixture["decision"], "support_quote": fixture["quote"],
                    "confidence_note": "Synthetic mock response, not a live model",
                })
                return httpx.Response(
                    200, request=request,
                    json={"choices": [{"message": {"content": answer}}],
                          "usage": {"prompt_tokens": 100, "completion_tokens": 100}},
                )
            self.client = httpx.Client(base_url=API_BASE, transport=httpx.MockTransport(mock_chat), trust_env=False)

    def post(self, path: str, *, json: dict) -> httpx.Response:
        if path != "/chat/completions":
            raise PilotGuardError("Only the chat-completions route is allowed")
        if json.get("model") != MODEL or json.get("max_tokens") != MAX_OUTPUT_TOKENS:
            raise PilotGuardError("Model and output limits must be fixed")
        if json.get("thinking") != {"type": "disabled"}:
            raise PilotGuardError("Non-thinking mode must be explicit")
        data = __import__("json").dumps(json, ensure_ascii=False).encode("utf-8")
        if len(data) > MAX_REQUEST_BYTES:
            raise PilotGuardError("Request size exceeds fixed preflight limit")
        if self.calls >= MAX_REQUESTS:
            raise PilotGuardError("Maximum paid request count exceeded")
        # A pessimistic *local estimate* for review, not a guaranteed dollar cap:
        # use 4 tokens per UTF-8 byte + max output and peak listed USD pricing.
        estimate = (
            len(data) * 4 * PEAK_INPUT_USD_PER_M +
            MAX_OUTPUT_TOKENS * PEAK_OUTPUT_USD_PER_M
        ) / 1_000_000
        if self.estimated_upper_usd + estimate > MAX_ESTIMATED_USD:
            raise PilotGuardError("Estimated experiment budget exceeded")
        self.calls += 1  # count the attempt before any network I/O
        self.estimated_upper_usd += estimate
        response = self.client.post(path, json=json)
        try:
            usage = response.json().get("usage") or {}
            self.observed_prompt_tokens += max(0, int(usage.get("prompt_tokens") or 0))
            self.observed_completion_tokens += max(0, int(usage.get("completion_tokens") or 0))
        except (ValueError, TypeError, AttributeError):
            pass
        return response

    def close(self) -> None:
        self.client.close()


PROMPT = (
    "You are evaluating evidence of software engineering decisions. Respond ONLY "
    "with a JSON object with keys decision, support_quote, confidence_note. "
    "If this PR does not substantiate an accepted decision, set decision to null "
    "and explain this in confidence_note. support_quote must be an EXACT contiguous "
    "substring of the provided PR body or an empty string. Never invent sources."
)


def safe_text(value: Any, limit: int = 350) -> str:
    return " ".join(str(value or "").split())[:limit]


def run(*, live: bool, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": "live" if live else "dry_run_mock",
        "provider": "DeepSeek",
        "model": MODEL,
        "base_url": API_BASE,
        "repository": REPOSITORY,
        "status": "blocked",
        "evaluates": "two public PR adapter smoke tests only",
        "human_review": "not_run",
        "why_search": "not_run",
        "drift": "not_run",
        "billing": {
            "paid_calls_attempted": 0, "estimated_upper_usd": 0,
            "estimated_not_guaranteed": True,
            "max_allowed_calls": MAX_REQUESTS, "max_output_tokens_per_call": MAX_OUTPUT_TOKENS,
            "max_request_bytes": MAX_REQUEST_BYTES,
        },
        "samples": [],
    }
    guarded = None
    try:
        guarded = GuardedChatClient(live=live, api_key=os.environ.get("DEEPSEEK_API_KEY"))
        provider = OpenAICompatibleProvider(
            api_key="managed-only-by-guarded-client",
            model=MODEL, base_url=API_BASE, client=guarded,
            max_output_tokens=MAX_OUTPUT_TOKENS, disable_thinking=True,
        )
        for number in PR_NUMBERS:
            pr = get_public_pr(number, live=live)
            prompt = f"GitHub public PR #{number}\nTitle: {pr['title']}\nBody:\n{pr['body']}"
            answer = provider.extract_candidate(ExtractionRequest(
                artifact_id=number, artifact_title=pr["title"],
                artifact_content=prompt, prompt=PROMPT,
                artifact_family="pull_request",
            ))
            try:
                candidate = json.loads(answer or "")
            except (ValueError, TypeError):
                candidate = None
            if not isinstance(candidate, dict):
                report["samples"].append({
                    "pr": number, "url": pr["url"], "source": pr["source"], "result": "invalid_json",
                    "human_assessment": "not_reviewed",
                })
                continue
            quote = safe_text(candidate.get("support_quote"), 280)
            report["samples"].append({
                "pr": number, "url": pr["url"], "source": pr["source"],
                "model_decision": safe_text(candidate.get("decision")),
                "support_quote": quote,
                "quote_exactly_in_input": bool(quote and quote in prompt),
                "human_assessment": "not_reviewed",
            })
        report["status"] = "mock_format_pass" if not live else "live_adapter_completed_not_graded"
    except Exception as exc:
        report["status"] = "blocked"
        report["error_category"] = type(exc).__name__  # Never print secrets or upstream payloads.
    finally:
        if guarded is not None:
            report["billing"]["paid_calls_attempted"] = guarded.calls if live else 0
            report["billing"]["estimated_upper_usd"] = round(guarded.estimated_upper_usd, 6) if live else 0
            report["billing"]["reported_prompt_tokens"] = guarded.observed_prompt_tokens if live else 0
            report["billing"]["reported_completion_tokens"] = guarded.observed_completion_tokens if live else 0
            guarded.close()
        (output_dir / "deepseek-pilot-summary.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        summary = [
            "# DeepSeek DecisionAtlas experiment",
            "",
            f"- Mode: **{report['mode']}**",
            f"- Status: **{report['status']}**",
            f"- Calls attempted: **{report['billing']['paid_calls_attempted']}**",
            "- No automatic claims of real decision correctness, Why Search, or Drift accuracy",
            "- A local USD estimate is not a provider-side billing limit",
            "",
        ]
        for sample in report["samples"]:
            summary += [
                f"- [PR #{sample['pr']}]({sample['url']}): "
                f"source=`{sample['source']}`, human_review=`not_reviewed`",
            ]
        (output_dir / "deepseek-pilot-summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="No-cost DeepSeek dry-run by default")
    parser.add_argument("--live", action="store_true", help="Enable billable API only with separate explicit approval")
    parser.add_argument("--output-dir", type=Path, default=Path(".tmp/deepseek-pilot"))
    args = parser.parse_args()
    result = run(live=args.live, output_dir=args.output_dir)
    print(f"DeepSeek pilot: mode={result['mode']} status={result['status']} "
          f"paid_calls_attempted={result['billing']['paid_calls_attempted']}")
    return 0 if result["status"] in ("mock_format_pass", "live_adapter_completed_not_graded") else 1


if __name__ == "__main__":
    raise SystemExit(main())
