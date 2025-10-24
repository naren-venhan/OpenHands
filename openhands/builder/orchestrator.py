from __future__ import annotations

import asyncio
import uuid
from typing import Any

from .state import Job, JobState, Phase
from .store import save_job, load_job


PHASES: list[Phase] = [
    Phase.PLAN,
    Phase.INGEST,
    Phase.AUDIT,
    Phase.COMPOSE,
    Phase.CODEGEN,
    Phase.VERIFY,
    Phase.DEPLOY,
    Phase.REPORT,
]


def _get_builder_settings() -> dict[str, Any]:
    try:
        from openhands.server.shared import config as _config  # lazy import

        ext = getattr(_config, 'extended', None)
        if not ext:
            return {}
        # ExtendedConfig supports attribute access
        builder_cfg = getattr(ext, 'builder', {})
        if isinstance(builder_cfg, dict):
            return builder_cfg
        return {}
    except Exception:
        return {}


class BuilderOrchestrator:
    def __init__(self) -> None:
        self._tasks: dict[str, asyncio.Task] = {}

    def create_job(
        self, mode: str, payload: dict[str, Any], options: dict[str, Any] | None = None
    ) -> Job:
        job = Job(id=str(uuid.uuid4()), state=JobState.QUEUED, phase=Phase.PLAN)
        job.context = {
            'mode': mode,
            'payload': payload,
            'options': options or {},
            'approved_phases': [],
        }
        save_job(job)
        return job

    def schedule(self, job_id: str) -> None:
        # Avoid duplicate tasks
        if job_id in self._tasks and not self._tasks[job_id].done():
            return
        task = asyncio.create_task(self._run(job_id))
        self._tasks[job_id] = task

    async def _run(self, job_id: str) -> None:
        job = load_job(job_id)
        if not job:
            return
        # Resume from current phase
        start_index = PHASES.index(job.phase or Phase.PLAN)
        job.state = JobState.RUNNING
        save_job(job)

        settings = _get_builder_settings()
        approvals = set()
        try:
            approvals_list = settings.get('require_approvals', [])
            approvals = {Phase(p.upper()) if isinstance(p, str) else p for p in approvals_list}
        except Exception:
            approvals = set()

        approved_phases: list[str] = job.context.get('approved_phases', [])

        for idx in range(start_index, len(PHASES)):
            phase = PHASES[idx]
            job.phase = phase
            job.progress = round((idx) / (len(PHASES) - 1), 3)
            save_job(job)

            # Gate if required and not already approved
            if phase in approvals and phase.value not in approved_phases:
                job.state = JobState.AWAITING_APPROVAL
                if phase not in job.approvalsNeeded:
                    job.approvalsNeeded.append(phase)
                save_job(job)
                return  # stop runner; will be resumed on approval

            # Simulate work for MVP (no external tools yet)
            await asyncio.sleep(0.05)

        # Completed all phases
        job.state = JobState.SUCCESS
        job.progress = 1.0
        save_job(job)
