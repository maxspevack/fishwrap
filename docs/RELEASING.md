# Fishwrap Release Runbook

The procedural runbook the active maintainer follows to cut a fishwrap release.

The active maintainer is currently AI, working under direct authorization from Max. Future-AI reading this when asked to ship a release: follow these steps in order.

A release moves a new version through three places:

1. `RELEASE_NOTES.md` gets a new section.
2. `fishwrap/__init__.py` gets a new `__version__`.
3. A signed git tag is pushed; CI publishes the OCI image.

A fourth, optional step is creating a curated GitHub Release for stable versions only.

**Note on what `release.yml` does and does not update:** the release workflow publishes the OCI image to GHCR. It does **not** update `fishwrap.org`. The site is updated by `.github/workflows/demos.yml`, which runs on a daily cron (12:00 UTC) and publishes via `actions/deploy-pages`. Step 7 below covers triggering a manual demos refresh after a release so the new `RELEASE_NOTES.html` is live promptly instead of waiting up to 24 hours for the next cron.

---

## Before You Touch Anything

Pause. Confirm the following with Max in the conversation, *before any tags fly*:

- Which version is this — patch, minor, major, or pre-release? (Consult [VERSIONING.md](VERSIONING.md) if uncertain.)
- What's the codename? Past examples: *The Foundation*, *The Glass Box*, *The Synchronization*, *The Newsstand*. Pick something that anchors "what release was that, again?"
- Are there any final code changes that need to land first?
- Is this stable (`v2.1.0`) or pre-release (`v2.1.0-rc1`)?

Do not proceed without explicit "yes, cut it" from Max.

---

## Step 1 — Write the `RELEASE_NOTES.md` Entry

Edit `docs/RELEASE_NOTES.md`. Add a new section at the **top**, following the existing convention:

```markdown
## vX.Y.Z (Codename) - Mon DD, YYYY

One-paragraph summary of what this release does and why someone would want it.

### 🚀 New Features
*   ...

### 🐛 Bug Fixes
*   ...

### 🛠️ Release Engineering
*   ...
```

The date is absolute and matches existing convention: `Mon DD, YYYY` (e.g., `May 5, 2026` — not `2026-05-05`). Pick subsection headers that match what's actually in this release; not every release has all three categories.

**Show Max the proposed entry before committing.**

---

## Step 2 — Bump `fishwrap/__init__.py`

Update `__version__` to the new string:

```python
__version__ = "X.Y.Z"          # for stable
__version__ = "X.Y.Z-rc1"      # for pre-release
```

The string here is exactly what `fishwrap-version` (the CLI inside the published image) will print to stdout. Consumers read it.

---

## Step 3 — Commit, Tag, Push (Single Pass)

```bash
cd ~/gemini/fishwrap
git add docs/RELEASE_NOTES.md fishwrap/__init__.py
git commit -m "release: vX.Y.Z (Codename)"
git tag -a vX.Y.Z -m "vX.Y.Z (Codename)"
git push origin main vX.Y.Z
```

Do not commit and tag in separate cycles. The tag must point at the release commit, and the release commit must contain the version bump.

---

## Step 4 — Watch the Workflow

The tag push triggered `.github/workflows/release.yml`. Watch it:

```bash
sleep 5
RUN_ID=$(gh run list --repo maxspevack/fishwrap --workflow=release.yml --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch "$RUN_ID" --repo maxspevack/fishwrap --exit-status
```

A green run means the image is live at GHCR.

If it fails, see *Recovery* below.

---

## Step 5 — Verify the Image (Visibility and Content)

Two checks: visibility (downstream consumers can pull) and content (the image runs correctly).

### 5a. Verify the package is publicly readable

The GHCR package may default to private on a fresh publish, may inherit visibility from prior history, or may follow a user-level default. Verify directly rather than assume:

```bash
TOKEN=$(curl -s "https://ghcr.io/token?service=ghcr.io&scope=repository:maxspevack/fishwrap:pull" | jq -r .token)
curl -sI -H "Authorization: Bearer $TOKEN" \
    -H "Accept: application/vnd.oci.image.index.v1+json" \
    "https://ghcr.io/v2/maxspevack/fishwrap/manifests/X.Y.Z" | head -1
```

A `HTTP/2 200` means the package is public. Anything else (commonly `401`) means it isn't, and you need to ask Max to flip it. Tell Max:

> The image is published but the GHCR package is private. Visit https://github.com/users/maxspevack/packages/container/fishwrap/settings → "Danger Zone" → "Change package visibility" → set to Public. Without this, downstream consumers can't `docker pull` it.

Wait for Max to confirm the flip is done before continuing.

### 5b. Verify the image runs correctly

```bash
podman pull ghcr.io/maxspevack/fishwrap:X.Y.Z
podman run --rm ghcr.io/maxspevack/fishwrap:X.Y.Z fishwrap-version
# expected stdout: X.Y.Z (or X.Y.Z-rc1, etc.)
```

If `fishwrap-version` doesn't match the tag, the workflow lied: the build claimed success but the image is wrong. Diagnose via `podman inspect` and the workflow logs. Don't proceed.

---

## Step 6 — Stable Release? Curate the GitHub Release

Pre-releases (anything matching `-rc`, `-alpha`, `-beta`) historically do not receive GitHub Releases. **Skip this step for them.**

For stable releases, the GitHub Release body is a Keep-a-Changelog-style digest of the `RELEASE_NOTES.md` entry, suitable for the GitHub UI's "Releases" panel. Translate the emoji-headed sections in `RELEASE_NOTES.md` into `Added` / `Changed` / `Fixed` / `Removed`.

```bash
gh release create vX.Y.Z \
    --repo maxspevack/fishwrap \
    --title "Fishwrap vX.Y.Z" \
    --notes "$(cat <<'EOF'
> One-line tagline.

## What Changed

### Added
- ...

### Changed
- ...

### Fixed
- ...

---

**Full release notes:** [RELEASE_NOTES.md](https://github.com/maxspevack/fishwrap/blob/vX.Y.Z/docs/RELEASE_NOTES.md)
EOF
)"
```

**Show Max the proposed body before running `gh release create`.**

---

## Step 7 — Close the Loop

Two things happen in this step: push the new release notes to fishwrap.org, then summarize for Max.

### 7a. Trigger demos.yml so fishwrap.org reflects the new release

GitHub Pages is in "GitHub Actions" mode; the only thing that updates the live site is `.github/workflows/demos.yml`. To get the new `RELEASE_NOTES.html` (and any other docs/ changes from the release commit) live without waiting for the next 12:00 UTC cron, trigger demos.yml manually:

```bash
gh workflow run demos.yml --repo maxspevack/fishwrap
sleep 5
RUN_ID=$(gh run list --repo maxspevack/fishwrap --workflow=demos.yml --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch "$RUN_ID" --repo maxspevack/fishwrap --exit-status
```

After the run completes, verify:

```bash
curl -s "https://fishwrap.org/RELEASE_NOTES.html?$(date +%s)" | grep -oE "v[0-9]+\.[0-9]+\.[0-9]+ \([^)]+\)" | head -1
# expected: vX.Y.Z (Codename)
```

If the demos workflow fails or the site doesn't show the new version, see *Recovery* below.

### 7b. Tell Max

> Release vX.Y.Z (Codename) is published. Image at `ghcr.io/maxspevack/fishwrap:X.Y.Z` and `:X.Y` (floating). GitHub Release at https://github.com/maxspevack/fishwrap/releases/tag/vX.Y.Z. fishwrap.org/RELEASE_NOTES.html is current.

If anything notable happened during the release (had to re-run a step, manual fix, etc.), call it out so it lands in his memory of the release.

---

## Recovery

### The release workflow failed after the tag was pushed

The tag is on the repo but no image was published. Common causes: Dockerfile regression, action version glitch, GHCR transient.

In the Actions UI, identify which step failed.

- **Transient (network, GHCR rate-limit, runner glitch):** re-run via "Re-run all jobs" in the UI. Buildx is atomic on push; a successful re-run produces the same artifact.
- **Real bug fixed by a new commit:** two paths.
  - *Move the tag* (force-tag-update): `git tag -f vX.Y.Z <new-sha> && git push --force-with-lease origin vX.Y.Z`. Force-pushes are visible in `git log`; downstream consumers who somehow already pulled the broken pre-fix tag would need to repull.
  - *Bump to the next patch version* and cut that. Cleaner archaeology — the broken tag stays as a tombstone, the next tag is the working release.

The second option is usually preferable. Suggest it to Max first.

### A bad image is at GHCR and consumers should not pull it

1. Delete the offending version via the GHCR UI: https://github.com/users/maxspevack/packages/container/fishwrap/versions
2. Cut a corrected patch release (`vX.Y.Z+1`). Consumers' floating-minor pins (`:X.Y`) move forward to the working image.

### The git tag was pushed, the workflow failed, and the workflow was fixed in a later commit on `main`

The tag doesn't move automatically. You have to choose: force-update the tag to the new SHA (visible in `git log`) or bump to the next patch version (cleaner). Suggest the bump to Max.

### demos.yml failed during step 7a

If the demos workflow failed, the site stays at last-good (the previous successful demos.yml deploy). The release itself is still complete — the image is live, the GitHub Release exists. Only fishwrap.org is stale.

Common causes:
- One of the four demos failed to build (a feed went 404, an error in fetching). With `fail-fast: false`, this blocks the deploy step (deploy is all-or-nothing). Diagnose the specific vertical's logs, fix, re-run via `gh workflow run demos.yml`.
- The Pages source isn't set to "GitHub Actions" mode. Check repo settings → Pages → Source. Should be "GitHub Actions" not "Deploy from a branch."
- `actions/deploy-pages` permissions issue. The workflow needs `pages: write` and `id-token: write` (already in the workflow file).
