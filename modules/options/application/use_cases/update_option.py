from modules.core.exceptions import (
    OptionNotFound
)
class UpdateOption:

    def __init__(self, repo):
        self.repo = repo

    def execute(self, option_id: str, request):

        option = self.repo.get_by_id(option_id)

        if not option:
            raise OptionNotFound()

        update_data = request.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(option, field, value)

        self.repo.update(option)

        return option