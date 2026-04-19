def get_user_repository():
    from modules.clients.infrastructure.repositories.user_repository_sql import UserRepositorySQL
    return UserRepositorySQL()