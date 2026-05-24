import uuid
from modules.options.infrastructure.db.option_model import OptionModel


class OptionRepositorySQL:

    def __init__(self, db):
        self.db = db

    # =========================
    # CREATE
    # =========================
    def save(self, option):

        model = OptionModel(
            id=str(uuid.uuid4()),
            name=option.name,
            type=option.type,
            price=option.price,   # ✅ AJOUT
            is_active=True
        )

        self.db.add(model)
        self.db.commit()
        return model

    # =========================
    # GET ALL
    # =========================
    def get_all(self):
        return self.db.query(OptionModel).all()

    # =========================
    # GET BY ID
    # =========================
    def get_by_id(self, option_id: str):
        return self.db.query(OptionModel).filter_by(id=option_id).first()

    # =========================
    # UPDATE
    # =========================
    def update(self, option):

        model = self.get_by_id(option.id)

        if not model:
            return None

        model.name = option.name
        model.type = option.type
        model.price = option.price   # ✅ AJOUT
        model.is_active = option.is_active

        self.db.commit()
        return model
    
    # =========================
    # ACTIVE
    # =========================
    def get_active(self):
        return (
            self.db.query(OptionModel)
            .filter(OptionModel.is_active == True)
            .all()
        )

    # =========================
    # DELETE (SOFT DELETE)
    # =========================
    def delete(self, option_id: str):

        model = self.get_by_id(option_id)

        if model:
            model.is_active = False
            self.db.commit()

 