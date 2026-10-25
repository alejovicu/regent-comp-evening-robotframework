"""Application settings, read from environment variables."""
import os


class Settings:
    mongo_url: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    mongo_db: str = os.getenv("MONGO_DB", "shopcart")

    jwt_secret: str = os.getenv("JWT_SECRET", "change-me-demo-secret")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))

    sftp_host: str = os.getenv("SFTP_HOST", "localhost")
    sftp_port: int = int(os.getenv("SFTP_PORT", "22"))
    sftp_user: str = os.getenv("SFTP_USER", "catalog")
    sftp_password: str = os.getenv("SFTP_PASSWORD", "catalog123")
    sftp_dir: str = os.getenv("SFTP_DIR", "upload")

    # Seeded demo accounts: "username:password:role" separated by commas.
    seed_users: str = os.getenv(
        "SEED_USERS", "admin:admin123:admin,user:user123:user,user2:user123:user"
    )
    seed_products: bool = os.getenv("SEED_PRODUCTS", "true").lower() == "true"

    cors_origins: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")


settings = Settings()
