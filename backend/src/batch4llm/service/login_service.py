from ..manager.database import Database
from argon2 import PasswordHasher
from datetime import datetime, timedelta
from jose import jwt

ph = PasswordHasher()


class LoginService:
    def __init__(
        self, db: Database, secret_key: str, algorithm: str, token_expire_minutes: int
    ):
        self.db = db
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expire_minutes = token_expire_minutes

    def __get_hashed_password(self, username: str) -> str:
        return self.db.users.get_for_verification(username=username)["password_hash"]

    def verify_password(self, username: str, password: str) -> bool:
        user = self.db.users.get_by_username(username=username)
        if not user:
            return False

        hashed_password = self.__get_hashed_password(username)
        try:
            ph.verify(hashed_password, password)
            return True
        except Exception:
            return False

    def register_user(self, username: str, password: str) -> bool:
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(username) > 10:
            raise ValueError("Username must be a max of 10 characters")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters")

        user = self.db.users.get_by_username(username=username)
        if user:
            raise ValueError("Username already exists")

        hashed_password = ph.hash(password)
        self.db.users.add(username=username, password_hash=hashed_password)
        return True

    def create_access_token(self, username: str):
        expire = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
        payload = {"sub": str(username), "exp": expire}
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
