from abc import ABC, abstractmethod


from abc import ABC, abstractmethod


class DocumentRepository(ABC):

    @abstractmethod
    def get_by_application_and_type(
        self,
        application_id: str,
        doc_type: str
    ):
        pass

    @abstractmethod
    def update_status(
        self,
        document_id: str,
        status: str,
        comment: str | None = None
    ):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def get_by_application(self, application_id: str):
        pass

    @abstractmethod
    def delete_by_application(self, application_id: str):
        pass