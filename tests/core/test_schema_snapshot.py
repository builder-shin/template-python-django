import json
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command

SNAPSHOT_PATH = Path(__file__).resolve().parent.parent / "snapshots" / "api_schema.json"


@pytest.mark.django_db
class TestApiSchemaSnapshot:
    def test_schema_matches_snapshot(self):
        """Current schema must match committed snapshot.
        Run `make update-schema` to regenerate after intentional changes."""
        assert SNAPSHOT_PATH.exists(), (
            f"Schema snapshot not found at {SNAPSHOT_PATH}. Run `make update-schema` to generate it."
        )
        out = StringIO()
        call_command("spectacular", "--format=openapi-json", stdout=out)
        current = json.loads(out.getvalue())
        snapshot = json.loads(SNAPSHOT_PATH.read_text())
        assert current == snapshot, (
            "API schema has changed. If intentional, run `make update-schema` to update the snapshot."
        )

    def test_schema_is_valid_openapi(self):
        """Schema must be valid JSON and contain required OpenAPI fields."""
        out = StringIO()
        call_command("spectacular", "--format=openapi-json", stdout=out)
        schema = json.loads(out.getvalue())
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
