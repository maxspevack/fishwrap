#!/usr/bin/env bash
#
# Fishwrap container entrypoint dispatcher.
#
# Implements the documented CLI surface from docs/adr/001-release-artifact.md:
#   fishwrap-build [--config <path>]   run the full pipeline
#   fishwrap-version                   print __version__ to stdout
#
# fishwrap-validate-config is a future feature (issue #4) and is intentionally
# not dispatched here yet; running it falls through to the generic exec branch
# and produces a "command not found" error, which is more honest than a stub
# that pretends to be a real validator.
#
# Falls through to `exec "$@"` so other invocations (debugging shells,
# diagnostic commands) work too. The generic-Python invocation pattern
# (`podman run --entrypoint python ... script.py`) bypasses this script
# entirely by overriding the image's ENTRYPOINT.
set -euo pipefail

usage() {
    cat >&2 <<EOF
fishwrap container entrypoint

Usage:
  fishwrap-build --config <path>      Run the full pipeline against <path>
  fishwrap-version                    Print the running version (semver)

Other commands are exec'd directly (e.g. \`bash\` for a debugging shell).
EOF
}

cmd="${1:-}"
[ $# -gt 0 ] && shift

case "${cmd}" in
    fishwrap-build)
        config_path=""
        while [ $# -gt 0 ]; do
            case "$1" in
                --config)
                    if [ $# -lt 2 ]; then
                        echo "fishwrap-build: --config requires a path argument" >&2
                        exit 2
                    fi
                    config_path="$2"
                    shift 2
                    ;;
                -h|--help)
                    cat >&2 <<EOF
Usage: fishwrap-build --config <path>

  --config <path>   Absolute path to the config.py the engine should run
                    against. Typically /cfg/config.py when invoked from
                    a containerized consumer.
EOF
                    exit 0
                    ;;
                *)
                    echo "fishwrap-build: unrecognized argument: $1" >&2
                    exit 2
                    ;;
            esac
        done

        if [ -z "${config_path}" ]; then
            echo "fishwrap-build: --config <path> is required" >&2
            exit 2
        fi
        if [ ! -f "${config_path}" ]; then
            echo "fishwrap-build: config file not found: ${config_path}" >&2
            exit 2
        fi

        export FISHWRAP_CONFIG="${config_path}"
        # The engine bootstraps its own schema during _initialize_engine
        # (see fishwrap/db/repository.py); no separate init step needed.
        python -m fishwrap.fetcher
        python -m fishwrap.editor
        python -m fishwrap.enhancer
        python -m fishwrap.printer
        ;;

    fishwrap-version)
        # Stable contract: stdout is exactly one semver line, no banner, no whitespace.
        python -c 'import fishwrap; print(fishwrap.__version__)'
        ;;

    ""|-h|--help)
        usage
        # Empty/help invocation exits 0 so it composes cleanly in scripts.
        exit 0
        ;;

    *)
        # Generic fallthrough for debugging and ad-hoc invocations.
        exec "${cmd}" "$@"
        ;;
esac
