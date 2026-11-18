from pwdlib import PasswordHash

# Argon2 hashing. Each hash gets its own random salt, so no secret key is needed here.
# (The SECRET_KEY in .env is only for signing login tokens.)
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)
