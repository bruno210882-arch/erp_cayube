import os
from datetime import datetime

APP_VERSION = os.getenv("APP_VERSION", datetime.now().strftime("%Y%m%d%H%M%S"))
PIX_CHAVE = "35548112899"
PIX_NOME = "BRUNA RAFAELA SOARES SILVA"
PIX_CIDADE = "CAIEIRAS"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "cayube_erp_chave_secreta_2026")
    APP_VERSION = APP_VERSION
    PIX_CHAVE = PIX_CHAVE
    PIX_NOME = PIX_NOME
    PIX_CIDADE = PIX_CIDADE

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    uri = os.getenv("DATABASE_URL")
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = uri or "sqlite:///erp_cayube.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
