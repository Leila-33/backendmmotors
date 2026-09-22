from sqlalchemy.orm import Session
from modules.options.infrastructure.db.option_model import OptionModel
from modules.options.infrastructure.mapper.option_mapper import OptionMapper
from modules.options.domain.entities.option import Option
from modules.options.domain.repositories.option_repository import OptionRepository
from sqlalchemy import func

class OptionRepositorySQL(OptionRepository):


    def __init__(
        self,
        db: Session,
    ):
        self.db = db


    # =========================
    # SAVE
    # =========================

    def save(
        self,
        option: Option,
    ) -> Option:

        model = (
            OptionMapper.to_model(
                option
            )
        )

        self.db.add(model)

        self.db.flush()

        return OptionMapper.to_domain(
            model
        )


    # =========================
    # UPDATE
    # =========================

    def update(
        self,
        option: Option,
    ) -> Option:

        model = (
            self.db.query(
                OptionModel
            )
            .filter(
                OptionModel.id == option.id
            )
            .first()
        )


        if model is None:
            return None


        OptionMapper.update_model(
            model,
            option,
        )

        self.db.flush()

        return OptionMapper.to_domain(
            model
        )


    # =========================
    # GET BY ID
    # =========================

    def get_by_id(
        self,
        option_id: str,
    ) -> Option | None:

        model = (
            self.db.query(
                OptionModel
            )
            .filter(
                OptionModel.id == option_id
            )
            .first()
        )


        if model is None:
            return None


        return OptionMapper.to_domain(
            model
        )

    # =========================
    # GET BY IDS
    # =========================

    def get_by_ids(
        self,
        option_ids: list[str],
    ) -> list[Option]:

        if not option_ids:
            return []

        models = (
            self.db.query(OptionModel)
            .filter(
                OptionModel.id.in_(option_ids)
            )
            .all()
        )

        return [
            OptionMapper.to_domain(model)
            for model in models
        ]

    # =========================
    # GET ALL
    # =========================

    def get_all(
        self,
    ) -> list[Option]:

        models = (
            self.db.query(
                OptionModel
            )
            .order_by(
                OptionModel.name.asc()
            )
            .all()
        )


        return [

            OptionMapper.to_domain(
                model
            )

            for model in models

        ]


    # =========================
    # GET ACTIVE
    # =========================

    def get_active(
        self,
    ) -> list[Option]:

        models = (

            self.db.query(
                OptionModel
            )

            .filter(
                OptionModel.is_active.is_(True)
            )

            .order_by(
                OptionModel.name.asc()
            )

            .all()

        )


        return [

            OptionMapper.to_domain(
                model
            )

            for model in models

        ]
    
    # =========================
    # EXISTS BY NAME
    # =========================
    def exists_by_name(
        self,
        name: str,
    ) -> bool:

        normalized = name.strip().lower()

        return (
            self.db.query(
                OptionModel
            )
            .filter(
                func.lower(
                    OptionModel.name
                ) == normalized
            )
            .first()
            is not None
        )
    
    def exists_by_name_except_id(
    self,
    name: str,
    option_id: str,
) -> bool:


        normalized = (
            name
            .strip()
            .lower()
        )


        return (

            self.db.query(
                OptionModel
            )

            .filter(
                func.lower(
                    OptionModel.name
                )
                == normalized,

                OptionModel.id != option_id
            )

            .first()

            is not None

        )