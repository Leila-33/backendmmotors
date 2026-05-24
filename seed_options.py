from uuid import uuid4
from sqlalchemy.orm import Session
from infrastructure.db.session import SessionLocal
from modules.options.infrastructure.db.option_model import OptionModel

SYSTEM_OPTIONS = [
    ("Assurance tous risques", "assurance_tous_risques"),
    ("Assistance dépannage", "assistance_depannage"),
    ("Entretien et SAV", "entretien_sav"),
    ("Contrôle technique", "controle_technique"),
]


def seed():
    db: Session = SessionLocal()

    for label, opt_type in SYSTEM_OPTIONS:
        exists = db.query(OptionModel).filter_by(type=opt_type).first()

        if not exists:
            option = OptionModel(
                id=str(uuid4()),
                name=label,
                type=opt_type,
                price=0.0,          # ✅ AJOUT IMPORTANT
                is_active=True
            )
            db.add(option)

    db.commit()
    db.close()


if __name__ == "__main__":
    seed()