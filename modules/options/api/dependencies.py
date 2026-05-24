from fastapi import Depends
from infrastructure.db.dependencies import get_db
from modules.options.infrastructure.repositories.option_repository_sql import OptionRepositorySQL
from modules.options.application.use_cases.create_option import CreateOption
from modules.options.application.use_cases.get_options import GetOptions
from modules.options.application.use_cases.update_option import UpdateOption
from modules.options.application.use_cases.delete_option import DeleteOption

def get_option_repository(db=Depends(get_db)):
    return OptionRepositorySQL(db)


def get_create_option_uc(repo=Depends(get_option_repository)):
    return CreateOption(repo)

def get_get_options_uc(repo=Depends(get_option_repository)):
    return GetOptions(repo)

def get_update_option_uc(repo=Depends(get_option_repository)):
    return UpdateOption(repo)

def get_delete_option_uc(repo=Depends(get_option_repository)):
    return DeleteOption(repo)