from abc import ABC, abstractmethod


from abc import ABC, abstractmethod


class WarrantyPlanRepository(ABC):


    # =========================
    # CREATE
    # =========================

    @abstractmethod
    def save(
        self,
        plan
    ):
        """
        Créer un plan de garantie
        """
        pass



    # =========================
    # READ
    # =========================

    @abstractmethod
    def get_by_id(
        self,
        plan_id: str
    ):
        """
        Récupérer un plan par son identifiant
        """
        pass



    @abstractmethod
    def find_all(
        self
    ):
        """
        Récupérer tous les plans
        """
        pass



    @abstractmethod
    def find_by_name(
        self,
        name: str
    ):
        """
        Rechercher un plan par son nom
        """
        pass



    @abstractmethod
    def find_by_plan_type(
        self,
        plan_type: str
    ):
        """
        Récupérer les plans par type
        """
        pass



    # =========================
    # UPDATE
    # =========================

    @abstractmethod
    def update(
        self,
        plan
    ):
        """
        Modifier un plan existant
        """
        pass



    # =========================
    # DELETE
    # =========================

    @abstractmethod
    def delete(
        self,
        plan_id: str
    ):
        """
        Supprimer un plan
        (ou désactiver si soft delete)
        """
        pass