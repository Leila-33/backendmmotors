from rq import Queue

from .redis_connection import redis_conn


inspection_queue = Queue(
    "inspection",
    connection=redis_conn,
)

reconditioning_queue = Queue(
    "reconditioning",
    connection=redis_conn,
)