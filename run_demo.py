import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from infrai_client import InfraiClient
from release_service import BuildEvent, ReleaseCoordinator
from signed_download import ReleaseArtifact, SignedDownloadService


def main() -> None:
    if not os.environ.get("INFRAI_API_KEY"):
        raise SystemExit("Set INFRAI_API_KEY before running the demo")
    artifact = ReleaseArtifact("rel-2026-09-03", "cli/rel-2026-09-03.tar.gz", "application/gzip")
    event = BuildEvent("build-481", "a1b2c3d", artifact)
    bucket = f"developer-releases-{uuid.uuid4().hex[:12]}"
    downloads = SignedDownloadService(InfraiClient(), bucket=bucket)
    downloads.prepare_storage()
    coordinator = ReleaseCoordinator(downloads)
    operation = coordinator.publish(event, "release-manager")
    print(coordinator.diagnose(operation))
    print(coordinator.download_link(operation))


if __name__ == "__main__":
    main()
