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
    def get_all(self) -> List[Option]:
        """Récupérer toutes les options"""
        pass

    @abstractmethod
    def get_active(self) -> List[Option]:
        """Récupérer uniquement les options actives"""
        pass

    @abstractmethod
    def delete(self, option_id: str) -> None:
        """
        Supprimer une option
        👉 en pratique : soft delete (is_active = False)
        """
        pass