from abc import ABC, abstractmethod


class JobQueue(ABC):

    @abstractmethod
    def enqueue_inspection(self, vehicle_id: str, admin_id: str):
        pass

    @abstractmethod    
    def enqueue_reconditioning(self, reconditioning_id: str, admin_id: str):
        pass