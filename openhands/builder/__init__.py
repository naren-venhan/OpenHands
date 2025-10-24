"""Builder extension for OpenHands (VikrAI storefront builder).

Feature-flagged via [extended.builder] in config.toml. Contains:
- schemas: Pydantic models for typed artifacts
- state: job state machine enums and DTOs
- store: simple file-backed job store (MVP)
- orchestrator: phase runner (skeleton)
"""
