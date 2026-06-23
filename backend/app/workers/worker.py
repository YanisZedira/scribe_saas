"""Worker RQ autonome (palier avancé).

Lancement :
    rq worker scribe --url $REDIS_URL
ou via Docker (voir docker-compose.yml, service ``worker``).
"""

from __future__ import annotations

import sys

from redis import Redis
from rq import Connection, Worker

from app.config import settings


def main() -> None:
    if not settings.redis_url:
        sys.exit("REDIS_URL non défini : worker asynchrone indisponible.")
    conn = Redis.from_url(settings.redis_url)
    with Connection(conn):
        Worker(["scribe"]).work()


if __name__ == "__main__":
    main()
