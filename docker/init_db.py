"""
Schema initializer for containerized fishwrap runs.

Per docs/adr/001-release-artifact.md, the newsroom SQLite database is
ephemeral inside the container. That means every container run starts
without a database and the pipeline expects the schema to exist before
the fetcher writes the first row.

This script bridges that gap: it loads the active config (via the
FISHWRAP_CONFIG env var the entrypoint already sets) and runs
`Base.metadata.create_all` against the configured database URL.

It is idempotent: running it against an already-initialized database is
a no-op.

Used internally by docker/entrypoint.sh's `fishwrap-build` dispatch.
Not part of the documented consumer CLI surface.
"""

from sqlalchemy import create_engine

from fishwrap.db.models import Base
from fishwrap.db.repository import _get_database_url


def main() -> None:
    url = _get_database_url()
    engine = create_engine(url)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    main()
