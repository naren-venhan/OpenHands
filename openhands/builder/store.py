from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from .state import Job


def _base_dir() -> Path:
    root = os.path.expanduser('~/.openhands/builder/jobs')
    path = Path(root)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_job(job: Job) -> None:
    path = _base_dir() / f'{job.id}.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(job.model_dump(), f, indent=2)


def load_job(job_id: str) -> Optional[Job]:
    path = _base_dir() / f'{job_id}.json'
    if not path.exists():
        return None
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return Job(**data)
