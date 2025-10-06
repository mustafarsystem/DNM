# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5

# Declarative base (main.py'deki Base tanımının buraya taşınmış hali)
class Base(DeclarativeBase):
    pass

# SQLAlchemy extension nesnesi (aynı API ile kullanılacak)
db = SQLAlchemy(model_class=Base)

# Diğer Flask extension nesneleri
login_manager = LoginManager()
bootstrap = Bootstrap5()
