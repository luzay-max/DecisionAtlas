"""Only for Draft #B02+B03 composition CI, never a real source or review."""
from __future__ import annotations

from pathlib import Path
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

ENGINE_DIR = Path(__file__).resolve().parents[2] / "services" / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from app.config import get_settings
from app.db.models import Artifact, Decision, SourceRef, Workspace


def seed() -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url)
    with Session(engine) as session:
        slug = "ci-b02-b03-combined"
        ws = session.scalar(select(Workspace).where(Workspace.slug == slug))
        if ws is None:
            ws = Workspace(
                slug=slug, name="CI SYNTHETIC B02/B03 composed behavior",
                owner_scope=settings.default_owner_scope,
                repo_url="https://github.com/example/ci-b02-b03-synthetic",
                access_source_type="public",
            )
            session.add(ws)
            session.flush()

        quote = "使用 PostgreSQL 主库保证数据一致性，并保留事务审计证据。"
        artifact = session.scalar(
            select(Artifact).where(Artifact.workspace_id == ws.id, Artifact.source_id == "synthetic-b02-b03")
        )
        if artifact is None:
            artifact = Artifact(
                workspace_id=ws.id, type="doc", source_id="synthetic-b02-b03",
                title="CI 合成的 PostgreSQL 主库证据",
                repo="example/ci-b02-b03-synthetic", content=quote,
                url="https://github.com/example/ci-b02-b03-synthetic/blob/main/fictional.md",
                metadata_json={"ci_synthetic_fixture_only": True},
            )
            session.add(artifact)
            session.flush()

        decision = session.scalar(
            select(Decision).where(
                Decision.workspace_id == ws.id, Decision.title == "使用 PostgreSQL 主库"
            )
        )
        if decision is None:
            decision = Decision(
                workspace_id=ws.id, title="使用 PostgreSQL 主库",
                status="active", review_state="accepted",
                problem="必须保证业务数据一致性",
                context="事务审计需求", constraints="不能自动替换主库",
                chosen_option="继续使用 PostgreSQL 主数据库",
                tradeoffs="额外维护成本", confidence=0.91,
            )
            session.add(decision)
            session.flush()

        reference = session.scalar(select(SourceRef).where(SourceRef.decision_id == decision.id))
        if reference is None:
            session.add(SourceRef(
                decision_id=decision.id, artifact_id=artifact.id,
                span_start=0, span_end=len(quote), quote=quote,
                url=artifact.url, relevance_score=0.9,
            ))

        candidate = session.scalar(select(Decision).where(
            Decision.workspace_id == ws.id, Decision.title == "火星电梯未审核"
        ))
        if candidate is None:
            session.add(Decision(
                workspace_id=ws.id, title="火星电梯未审核", status="active",
                review_state="candidate", problem="只用于防泄漏负例",
                chosen_option="不得返回未审核候选", tradeoffs="未知",
                confidence=0.5,
            ))
        session.commit()
    engine.dispose()


if __name__ == "__main__":
    seed()
    print("Seeded isolated synthetic B02+B03 composition fixture.")
