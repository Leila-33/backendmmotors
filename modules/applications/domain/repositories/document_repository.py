from abc import ABC, abstractmethod
from modules.applications.domain.entities.document import (
    Document
)

class DocumentRepository(ABC):


    # =========================
    # GET BY APPLICATION + TYPE
    # =========================
    @abstractmethod
    def get_by_application_and_type(
        self,
        application_id: str,
        doc_type: str
    ):
        pass



    # =========================
    # GET ALL BY APPLICATION
    # =========================
    @abstractmethod
    def get_by_application(
        self,
        application_id: str
    ):
        pass
    # =========================
    # GET BY ID
    # =========================
    @abstractmethod
    def get_by_id(
            self,
            document_id: str,
        ) -> Document | None:
            pass
    

    # =========================
    # UPDATE STATUS
    # =========================
    @abstractmethod
    def update_status(
        self,
        document_id: str,
        status: str,
        comment: str | None = None
    ):
        pass



    # =========================
    # DELETE BY APPLICATION
    # =========================
    @abstractmethod
    def delete_by_application(
        self,
        application_id: str
    ):
        pass