from ..manager.database import Database


class UserService:
    def __init__(self, db: Database):
        self.db = db

    def get_users(self) -> list[dict]:
        return self.db.users.list()

    def get_groups(self) -> list[dict]:
        return self.db.groups.list()

    def add_group(self, group_name: str) -> dict:
        return self.db.groups.add_group(group_name)

    def set_user_group(self, username: str, group_id: int) -> list[dict]:
        return self.db.users.set_group(username, group_id)

    def does_any_user_exist(self) -> bool:
        return self.db.users.does_any_user_exist()
