import run_demo


class FakeClient:
    pass


class FakeDownloads:
    buckets = []

    def __init__(self, client, bucket):
        self.buckets.append(bucket)

    def prepare_storage(self):
        pass

    def grant(self, artifact, expires_seconds=300):
        return {"url": "https://download.test/signed"}


def test_demo_uses_a_unique_bucket_name(monkeypatch):
    monkeypatch.setenv("INFRAI_API_KEY", "test-key")
    monkeypatch.setattr(run_demo, "InfraiClient", FakeClient)
    monkeypatch.setattr(run_demo, "SignedDownloadService", FakeDownloads)

    run_demo.main()
    run_demo.main()

    assert len(set(FakeDownloads.buckets)) == 2
    assert all(name.startswith("developer-releases-") for name in FakeDownloads.buckets)
    assert all(len(name) == 31 for name in FakeDownloads.buckets)
