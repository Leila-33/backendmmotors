from abc import ABC, abstractmethod

class ApplicationOptionRepository(ABC):

    @abstractmethod
    def replace_options(
        self,
        application_id: str,
        option_ids: list[str]
    ):
        pass


    @abstractmethod
    def delete_by_application(
        self,
        application_id: str
    ):
        pass