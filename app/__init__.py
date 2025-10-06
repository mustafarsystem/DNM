import os
from flask import Flask
from dotenv import load_dotenv
from app.extensions import db, login_manager, bootstrap


def create_app():
    # Ortam değişkenlerini yükle (.env dosyasından)
    load_dotenv()
    secret_key = os.getenv("SECRET_KEY")
    database_url = os.getenv("DATABASE_URL")

    # Flask uygulamasını oluştur
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url

    # Flask extension'larını başlat
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)

    from app import models
    from app.models import Users

    from app.routes.auth import auth_bp
    from app.routes.orders import orders_bp
    from app.routes.projects import projects_bp
    from app.routes.plan import plan_bp
    from app.routes.stock_raw import stock_raw_bp
    from app.routes.production import production_bp
    from app.routes.process_control import process_control_bp
    from app.routes.home import home_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(plan_bp)
    app.register_blueprint(stock_raw_bp)
    app.register_blueprint(production_bp)
    app.register_blueprint(process_control_bp)
    app.register_blueprint(home_bp)



    @login_manager.user_loader
    def load_user(user_id):
        return db.get_or_404(Users, user_id)

    with app.app_context():
        db.create_all()

    return app