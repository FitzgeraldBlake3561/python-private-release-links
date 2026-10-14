import pytest

from release_service import BuildEvent, ReleaseCoordinator
from signed_download import ReleaseArtifact


class FakeDownloads:
    def grant(self, artifact, expires_seconds=300):
        return {"release_id": artifact.release_id, "url": "https://download.test/signed", "expires_seconds": expires_seconds}


def test_publish_requires_approval_and_diagnostics_are_ready():
    artifact = ReleaseArtifact("rel-1", "cli/rel-1.tar.gz", "application/gzip")
    service = ReleaseCoordinator(FakeDownloads())
    event = BuildEvent("build-1", "abc123", artifact)
    with pytest.raises(ValueError):
        service.publish(event, " ")
    operation = service.publish(event, "compliance-reviewer")
    diagnostic = service.diagnose(operation)
    assert diagnostic.ready is True
    assert "release approval recorded" in diagnostic.checks
