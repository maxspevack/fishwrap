# Fishwrap Release Runbook

The procedural runbook the active maintainer follows to cut a fishwrap release.

The active maintainer is currently AI, working under direct authorization from Max. Future-AI reading this when asked to ship a release: follow these steps in order.

A release moves a new version through three places:

1. `RELEASE_NOTES.md` gets a new section.
2. `fishwrap/__init__.py` gets a new `__version__`.
3. A signed git tag is pushed; CI publishes the OCI image.

A fourth, optional step is creating a curated GitHub Release for stable versions only.

---

## Before You Touch Anything

Pause. Confirm the following with Max in the conversation, *before any tags fly*:

- Which version is this — patch, minor, major, or pre-release? (Consult [VERSIONING.md](VERSIONING.md) if uncertain.)
- What's the codename? Past examples: *The Foundation*, *The Glass Box*, *The Synchronization*. Pick something that anchors "what release was that, again?"
- Are there any final code changes that need to land first?
- Is this stable (`v2.1.0`) or pre-release (`v2.1.0-rc1`)?

Do not proceed without explicit "yes, cut it" from Max.

---

## Step 1 — Write the `RELEASE_NOTES.md` Entry

Edit `docs/RELEASE_NOTES.md`. Add a new section at the **top**, following the existing convention:

```markdown
## vX.Y.Z (Codename) - YYYY-MM-DD

One-paragraph summary of what this release does and why someone would want it.

### 🚀 New Features
*   ...

### 🐛 Bug Fixes
*   ...

### 🛠️ Release Engineering
*   ...
```

The date is absolute (Klausner discipline: no "today" or "this week"). Pick subsection headers that match what's actually in this release; not every release has all three categories.

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

## Step 5 — Verify the Published Image

```bash
podman pull ghcr.io/maxspevack/fishwrap:X.Y.Z
podman run --rm ghcr.io/maxspevack/fishwrap:X.Y.Z fishwrap-version
# expected stdout: X.Y.Z (or X.Y.Z-rc1, etc.)
```

If `fishwrap-version` doesn't match the tag, the workflow lied: the build claimed success but the image is wrong. Diagnose via `podman inspect` and the workflow logs. Don't proceed to Step 7.

---

## Step 6 — First Release of the Package? Ask Max to Flip Visibility

This applies *only the first time* the package is created on GHCR. Once flipped, it persists. After the first release, skip this step.

If this is the first release ever (or the first since the package was deleted), the package is created as **private**. CI cannot change this.

Tell Max, verbatim:

> The image is published. The GHCR package is currently private. Visit https://github.com/users/maxspevack/packages/container/fishwrap/settings → "Danger Zone" → "Change package visibility" → set to Public. Without this, downstream consumers can't `docker pull` it.

Wait for Max to confirm the flip is done before continuing.

---

## Step 7 — Stable Release? Curate the GitHub Release

Pre-releases (anything matching `-rc`, `-alpha`, `-beta`) historically do not receive GitHub Releases. **Skip this step for them.**

For stable releases, the GitHub Release body is a Keep-a-Changelog-style digest of the `RELEASE_NOTES.md` entry, suitable for the GitHub UI's "Releases" panel. Translate the emoji-headed sections in `RELEASE_NOTES.md` into `Added` / `Changed` / `Fixed`.

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

## Step 8 — Close the Loop

Tell Max:

> Release vX.Y.Z (Codename) is published. Image at `ghcr.io/maxspevack/fishwrap:X.Y.Z` and `:X.Y` (floating). GitHub Release at https://github.com/maxspevack/fishwrap/releases/tag/vX.Y.Z.

If anything notable happened during the release (had to re-run a step, manual fix, etc.), call it out so it lands in his memory of the release.

---

## Recovery

### The workflow failed after the tag was pushed

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
