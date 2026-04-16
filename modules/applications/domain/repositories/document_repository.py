from abc import ABC, abstractmethod
from typing import List, Optional
from modules.applications.domain.entities.document import Document


class DocumentRepository(ABC):

    @abstractmethod
    def save(self, document: Document):
        pass

    @abstractmethod
    def get_by_application_id(self, application_id: str) -> List[Document]:
        pass
