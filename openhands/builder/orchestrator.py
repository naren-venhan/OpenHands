from __future__ import annotations

import uuid
from typing import Any

from .state import Job, JobState, Phase
from .store import save_job


class BuilderOrchestrator:
    def __init__(self) -> None:
        pass

    def create_job(self, mode: str, payload: dict[str, Any], options: dict[str, Any] | None = None) -> Job:
        job = Job(id=str(uuid.uuid4()), state=JobState.QUEUED, phase=Phase.PLAN)
        job.context = {"mode": mode, "payload": payload, "options": options or {}}
        save_job(job)
        return job
