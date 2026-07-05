from abc import ABC, abstractmethod


class WarrantyPlanRepository(ABC):

    @abstractmethod
    def save_plan(self, plan):
        pass

    @abstractmethod
    def find_by_name(self, name: str):
        pass



    @abstractmethod
    def find_all(self):
        pass


    @abstractmethod
    def find_by_plan_type(self, plan_type: str):
        pass
    
    @abstractmethod
    def delete(self, plan_id: str):
        pass
    @abstractmethod
    def get_by_id(self, plan_id: str):
        pass

    @abstractmethod
    def update(self, plan):
        pass
    
    @abstractmethod
    def commit(self):
        pass