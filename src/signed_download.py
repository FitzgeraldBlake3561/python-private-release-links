from dataclasses import dataclass

from infrai_client import InfraiClient


@dataclass(frozen=True)
class ReleaseArtifact:
    release_id: str
    object_key: str
    content_type: str


@dataclass(frozen=True)
class DownloadGrant:
    release_id: str
    url: str
    expires_seconds: int


class SignedDownloadService:
    def __init__(self, client: InfraiClient, bucket: str = "developer-releases"):
        self.client = client
        self.bucket = bucket

    def prepare_storage(self) -> None:
        self.client.create_bucket(self.bucket)

    def grant(self, artifact: ReleaseArtifact, expires_seconds: int = 300) -> DownloadGrant:
        data = self.client.presign_get(self.bucket, artifact.object_key, expires_seconds)
        return DownloadGrant(artifact.release_id, data["url"], expires_seconds)
