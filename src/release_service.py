from dataclasses import dataclass
from typing import List

from signed_download import DownloadGrant, ReleaseArtifact, SignedDownloadService


@dataclass(frozen=True)
class BuildEvent:
    build_id: str
    commit: str
    artifact: ReleaseArtifact


@dataclass(frozen=True)
class ReleaseOperation:
    release_id: str
    approved_by: str
    artifact: ReleaseArtifact


@dataclass(frozen=True)
class Diagnostic:
    release_id: str
    checks: List[str]
    ready: bool


class ReleaseCoordinator:
    def __init__(self, downloads: SignedDownloadService):
        self.downloads = downloads

    def publish(self, event: BuildEvent, approved_by: str) -> ReleaseOperation:
        if not approved_by.strip():
            raise ValueError("approved_by is required")
        return ReleaseOperation(event.artifact.release_id, approved_by, event.artifact)

    def diagnose(self, operation: ReleaseOperation) -> Diagnostic:
        checks = ["build recorded", "release approval recorded", "artifact key present"]
        return Diagnostic(operation.release_id, checks, bool(operation.artifact.object_key))

    def download_link(self, operation: ReleaseOperation) -> DownloadGrant:
        return self.downloads.grant(operation.artifact)
