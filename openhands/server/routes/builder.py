from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from openhands.server.dependencies import get_dependencies
from openhands.builder.orchestrator import BuilderOrchestrator
from openhands.builder.store import load_job, save_job
from openhands.builder.state import Job, Phase, JobState

app = APIRouter(prefix='/api/builder', dependencies=get_dependencies())

_orchestrator = BuilderOrchestrator()


def _validate_body(body: dict) -> tuple[str, dict, dict]:
    mode = body.get('mode')
    payload = body.get('payload', {})
    options = body.get('options', {})
    if mode not in ('url', 'figma', 'prompt'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid mode')
    # Basic payload validation per mode (MVP)
    if mode == 'url' and not isinstance(payload.get('startUrl'), str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='startUrl required for url mode')
    if mode == 'figma' and not isinstance(payload.get('fileKey'), str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='fileKey required for figma mode')
    if mode == 'prompt' and not isinstance(payload.get('brief'), str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='brief required for prompt mode')
    return mode, payload, options


@app.post('/jobs')
async def create_job(body: dict) -> JSONResponse:
    mode, payload, options = _validate_body(body)
    job: Job = _orchestrator.create_job(mode, payload, options)
    # Immediately schedule background execution
    try:
        import asyncio

        loop = asyncio.get_running_loop()
        loop.call_soon(_orchestrator.schedule, job.id)
    except RuntimeError:
        # Fallback if not in async context
        pass
    return JSONResponse({'jobId': job.id})


@app.get('/jobs/{job_id}/status')
async def get_status(job_id: str) -> JSONResponse:
    job = load_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Job not found')
    return JSONResponse(
        {
            'state': job.state,
            'phase': job.phase,
            'progress': job.progress,
            'approvals': job.approvalsNeeded,
            'lastError': job.lastError,
        }
    )


@app.get('/jobs/{job_id}/artifacts')
async def get_artifacts(job_id: str) -> JSONResponse:
    job = load_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Job not found')
    return JSONResponse(job.artifacts.model_dump())


@app.post('/jobs/{job_id}/approve')
async def approve(job_id: str, phase: Phase) -> JSONResponse:
    job = load_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Job not found')
    if job.state != JobState.AWAITING_APPROVAL:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No approval pending')
    # remove phase from approvals if present
    job.approvalsNeeded = [p for p in job.approvalsNeeded if p != phase]
    if not job.approvalsNeeded:
        job.state = JobState.RUNNING
    # track approval in context to allow orchestrator resume to skip this gate
    approved = set(job.context.get('approved_phases', []))
    approved.add(phase.value)
    job.context['approved_phases'] = list(approved)
    save_job(job)
    # resume execution
    try:
        import asyncio

        loop = asyncio.get_running_loop()
        loop.call_soon(_orchestrator.schedule, job.id)
    except RuntimeError:
        pass
    return JSONResponse({'ok': True})
