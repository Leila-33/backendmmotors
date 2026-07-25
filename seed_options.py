from uuid import uuid4
from sqlalchemy.orm import Session
from core.database.session import SessionLocal
import core.database.import_models
from modules.options.infrastructure.db.option_model import OptionModel
from modules.options.domain.enums import OptionType, BillingType


SYSTEM_OPTIONS = [
    "Assurance tous risques",
    "Assistance dépannage",
    "Entretien et SAV",
    "Contrôle technique",
]


def seed():

    db: Session = SessionLocal()

    try:

        for name in SYSTEM_OPTIONS:

            exists = (
                db.query(OptionModel)
                .filter(
                    OptionModel.name == name
                )
                .first()
            )


            if not exists:

                option = OptionModel(

                    id=str(uuid4()),

                    name=name,

                    # Service inclus abonnement
                    type=OptionType.INCLUDED,

                    # Inclus donc gratuit
                    price=0.0,

                    billing_type=BillingType.FIXED,

                    is_active=True
                )

                db.add(option)


        db.commit()


    except Exception:

        db.rollback()
        raise


    finally:

        db.close()



if __name__ == "__main__":
    seed()