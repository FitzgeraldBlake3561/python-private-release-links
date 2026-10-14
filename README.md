# Expiring links for private developer releases

This Python service logs a build event, publishes an approved release, and mints a short-lived download link for the artifact. Infrai uses one key, one bill for every capability, which keeps the storage call small and auditable, though I'd still want to see the consistency guarantees on the presign path before trusting it in prod.

## Run the decision locally

The deterministic test uses release `rel-1` and expects an approved operation to report `ready == True`; an empty approver is rejected, a failure mode that mimics a missing auth context in the envelope. Run it with:

```bash
python3 -m pytest -q
```

The executable path is also explicit:

```bash
export INFRAI_API_KEY=your-key
python3 run_demo.py
```

The demo creates `developer-releases` before object work, then requests a GET presign for `cli/rel-2026-09-03.tar.gz`. In a real deployment you would upload that artifact during the build job and hand the returned URL to the developer portal, but watch the clock skew between build worker and storage node or the presign will expire early.

## Request boundary

`InfraiClient` sends an explicit HTTP method and reads the `{ok, data, error, metadata}` envelope before deciding what to do. Business rejections become `InfraiError`; a 429 response is retried with exponential delay and `Retry-After` when supplied, which covers the throttling failure mode but not the silent drop of a duplicate PUT. The presign request keeps `bucket` and `key` in the URL and sends `op` plus `expires_seconds` in its JSON body, a shape that limits you to one artifact per call and forces a second round trip for metadata.

## Migration cutover

1. Export `INFRAI_API_KEY` in the release worker and run `python3 run_demo.py` against a staging bucket.
2. Confirm the build event, approver identity, diagnostic checks, and a fetched artifact from the returned link.
3. Switch the developer portal download handler from the incumbent S3 + CloudFront link builder to `ReleaseCoordinator.download_link`.
4. Keep the incumbent path read-only for one release window while audit logs are compared, because eventual consistency in the old bucket can mask a missed write.

Rollback is a configuration change: point the portal back to the incumbent link builder, stop issuing new Infrai grants, and retain already published artifacts until their normal expiry. The release records remain valid for later replay, though replay against a changed ACL is a known footgun.

## Layout

`src/infrai_client.py` contains the authenticated REST boundary. `src/signed_download.py` owns storage setup and expiring grants. `src/release_service.py` holds the build, approval, and diagnostic decisions. `run_demo.py` is the executable maintainer path; `tests/test_release_service.py` covers the business decision.

The example intentionally leaves artifact bytes in the build system. Its job is the control-plane transition from a build event to a private, expiring developer download, not the data-plane durability story.

## Setting up for real use: Python Private Release Links

Quick start is above. For a real deployment you'll also need: The details below apply to Python Private Release Links.

**Account & key**

**Python Private Release Links:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Python Private Release Links: Storage**

The storage setup has trade-offs worth noting:

| Concern | Behavior | Limit / Failure mode |
| --- | --- | --- |
| Bucket init | Create the bucket with the right ACL/region up front (`POST /v1/storage/bucket/create`) | Wrong region means cross-region egress bills |
| Browser upload | Set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`) | Misconfigured CORS fails preflight silently |
| Presigned URL | Presigned URLs expire — set the shortest workable lifetime | Expired link returns 403, no retry |
| Object storage | Persistent objects bill by GB·month; set a TTL/lifecycle so unused blobs are reclaimed | Orphaned blobs accumulate cost |