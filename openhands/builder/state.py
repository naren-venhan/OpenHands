from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

from .schemas import (
    ThemeTokens,
    LayoutMap,
    Catalog,
    SEOReport,
    BuildArtifact,
)


class JobState(str, Enum):
    QUEUED = 'QUEUED'
    RUNNING = 'RUNNING'
    AWAITING_APPROVAL = 'AWAITING_APPROVAL'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'


class Phase(str, Enum):
    PLAN = 'PLAN'
    INGEST = 'INGEST'
    AUDIT = 'AUDIT'
    COMPOSE = 'COMPOSE'
    CODEGEN = 'CODEGEN'
    VERIFY = 'VERIFY'
    DEPLOY = 'DEPLOY'
    REPORT = 'REPORT'


class JobArtifacts(BaseModel):
    themeTokens: ThemeTokens | None = None
    layoutMap: LayoutMap | None = None
    catalog: Catalog | None = None
    seoReport: SEOReport | None = None
    buildArtifact: BuildArtifact | None = None


class Job(BaseModel):
    id: str
    state: JobState = JobState.QUEUED
    phase: Phase | None = None
    progress: float = 0.0
    approvalsNeeded: list[Phase] = Field(default_factory=list)
    lastError: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    artifacts: JobArtifacts = Field(default_factory=JobArtifacts)
