#!/usr/bin/env python3
"""Shared path helpers for the AppleScout skill."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def tmp_dir() -> Path:
    path = repo_root() / ".tmp"
    path.mkdir(exist_ok=True)
    return path


def tmp_file(name: str) -> Path:
    return tmp_dir() / name


def directives_dir() -> Path:
    return repo_root() / "directives"


def prompts_dir() -> Path:
    return repo_root() / "applescout" / "prompts"


def references_dir() -> Path:
    return repo_root() / "applescout" / "references"
