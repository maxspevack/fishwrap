# syntax=docker/dockerfile:1.7
#
# Fishwrap engine — release artifact per docs/adr/001-release-artifact.md.
#
# Build:   podman build -t fishwrap:dev .
# Run:     podman run --rm -v $(pwd)/demo:/cfg -v $(pwd)/output:/output \
#              fishwrap:dev fishwrap-build --config /cfg/config.py
#
# Architecture: linux/amd64 only. Production deploy targets (GH Actions
# runners, GH Pages) are x86_64; Mac local-dev runs fine via QEMU under
# Podman/Docker Desktop. arm64 publishing is intentionally out of scope
# until a real consumer needs it (manifesto rule 1).

FROM python:3.12-slim

# Runtime system packages.
# - libxml2 / libxslt1.1: lxml fallback when no wheel matches
# - libjpeg62-turbo / zlib1g: pillow runtime
# - tzdata: required by Python's zoneinfo (auditor + printer call ZoneInfo)
# - tini: PID 1 reaper so signals propagate cleanly to the Python process
RUN apt-get update && apt-get install -y --no-install-recommends \
        libxml2 \
        libxslt1.1 \
        libjpeg62-turbo \
        zlib1g \
        tzdata \
        tzdata-legacy \
        tini \
    && rm -rf /var/lib/apt/lists/*

# Non-root user (manifesto rule 6: defense in depth).
ARG UID=1000
ARG GID=1000
RUN groupadd -g "${GID}" fishwrap \
    && useradd -u "${UID}" -g "${GID}" -m -s /bin/bash fishwrap

WORKDIR /app

# Install Python dependencies. Layer cache: deps only invalidate on requirements.txt change.
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Pre-download NLTK data to /app/nltk_data — the path fishwrap/__init__.py
# already appends to nltk.data.path. Baking it in means no runtime network access.
# Match scripts/install_venv.sh (punkt only).
RUN mkdir -p /app/nltk_data \
    && python -m nltk.downloader -d /app/nltk_data punkt \
    && chmod -R a+rX /app/nltk_data

# Copy the engine itself.
COPY fishwrap /app/fishwrap

# Make the engine importable from any working directory.
# The consumer's CWD is intentionally not part of the contract — only the
# /cfg and /output mounts are. Without this, `python -m fishwrap.X` would
# only succeed when CWD happens to contain a fishwrap/ package on disk.
ENV PYTHONPATH=/app

# Entrypoint dispatcher and schema-init helper.
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY docker/init_db.py /usr/local/bin/init_db.py
RUN chmod +x /usr/local/bin/entrypoint.sh

# Documented mount points.
RUN mkdir -p /cfg /output \
    && chown fishwrap:fishwrap /cfg /output

# OCI labels — provenance breadcrumbs at the image level.
LABEL org.opencontainers.image.source="https://github.com/maxspevack/fishwrap" \
      org.opencontainers.image.description="Fishwrap — Glass Box news engine" \
      org.opencontainers.image.licenses="Apache-2.0"

USER fishwrap

# tini handles PID 1 duties; entrypoint.sh dispatches the documented CLI surface.
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
CMD ["fishwrap-build", "--help"]
