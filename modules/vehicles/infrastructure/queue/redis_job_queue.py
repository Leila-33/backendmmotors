from modules.vehicles.infrastructure.queue.queues import (
    inspection_queue,
    reconditioning_queue
)

from modules.inspections.infrastructure.worker.inspection_worker import run_inspection
from modules.reconditionings.infrastructure.worker.reconditioning_worker import run_reconditioning


class RedisJobQueue:

    def enqueue_inspection(self, vehicle_id: str, admin_id: str):
        inspection_queue.enqueue(
            run_inspection,
            vehicle_id,
            admin_id
        )

    def enqueue_reconditioning(self, reconditioning_id: str, admin_id: str):
        reconditioning_queue.enqueue(
            run_reconditioning,
            reconditioning_id,
            admin_id
        )