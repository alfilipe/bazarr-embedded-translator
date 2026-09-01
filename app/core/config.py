import os


class Settings:
    """
    Application configuration.
    """

    APP_NAME: str = os.getenv(
        "APP_NAME",
        "Bazarr Embedded Translator",
    )

    APP_VERSION: str = os.getenv(
        "APP_VERSION",
        "1.0.0",
    )

    TV_ROOT: str = os.getenv(
        "TV_ROOT",
        "/tv",
    )

    MOVIES_ROOT: str = os.getenv(
        "MOVIES_ROOT",
        "/movies",
    )

    HOST: str = os.getenv(
        "HOST",
        "0.0.0.0",
    )

    PORT: int = int(
        os.getenv(
            "PORT",
            "9870",
        )
    )


settings = Settings()
