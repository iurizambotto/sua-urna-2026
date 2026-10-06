"""Shared fixtures: real TSE files captured on 2026-10-06 for one section of Macapá."""

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def bu_bytes() -> bytes:
    return (FIXTURES / "ap-06050-0002-0069.bu").read_bytes()


@pytest.fixture
def aux_json() -> dict:
    return json.loads((FIXTURES / "ap-06050-0002-0069-aux.json").read_text(encoding="utf-8"))


@pytest.fixture
def municipio_json() -> dict:
    return json.loads((FIXTURES / "ap06050-u.json").read_text(encoding="utf-8"))


@pytest.fixture
def cs_json() -> dict:
    return json.loads((FIXTURES / "ap-cs.json").read_text(encoding="utf-8"))
