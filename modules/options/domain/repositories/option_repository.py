from abc import ABC, abstractmethod
from typing import List, Optional

from modules.options.domain.entities.option import Option


class OptionRepository(ABC):

    @abstractmethod
    def save(self, option: Option) -> Option:
        """Créer une nouvelle option"""
        pass

    @abstractmethod
    def update(self, option: Option) -> Option:
        """Mettre à jour une option existante"""
        pass

    @abstractmethod
    def get_by_id(self, option_id: str) -> Optional[Option]:
        """Récupérer une option par son ID"""
        pass

    @abstractmethod
    def get_by_ids(
        self,
        option_ids: list[str],
    ) -> list[Option]:
        pass

    @abstractmethod
    def get_all(self) -> List[Option]:
        """Récupérer toutes les options"""
        pass

    @abstractmethod
    def get_active(self) -> List[Option]:
        """Récupérer uniquement les options actives"""
        pass

    @abstractmethod
    def exists_by_name(
        self,
        name: str,
    ) -> bool:
        pass

    @abstractmethod
    def exists_by_name_except_id(
        self,
        name: str,
        option_id: str,
    ) -> bool:
        pass
