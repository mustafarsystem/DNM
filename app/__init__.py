import os
from flask import Flask
from dotenv import load_dotenv
from app.extensions import db, login_manager, bootstrap
import datetime as dt

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
    from app.routes.admin import admin_bp
    from app.routes.stock import stock_bp
    from app.routes.progress import progress_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(plan_bp)
    app.register_blueprint(stock_raw_bp)
    app.register_blueprint(production_bp)
    app.register_blueprint(process_control_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(progress_bp)

    @app.template_filter("to_ts")
    def to_ts(d):
        if d is None:
            return 0
        if isinstance(d, str):
            d = dt.date.fromisoformat(d)
        if isinstance(d, dt.date) and not isinstance(d, dt.datetime):
            d = dt.datetime.combine(d, dt.time())
        return int(d.replace(tzinfo=dt.timezone.utc).timestamp())



    # Flask-Admin entegrasyonu
    from flask_admin import Admin
    from flask_admin.contrib.sqla import ModelView
    from app.models import Users, Firmalar, Siparis, Satir, Lot, Proje, Projerevtakip,Projeopr, Projecihaz, Plan, Planstr, Cnc, Malzeme, Malztransc, Malzstok, Mastar, Operasyon, Tedarikci, Siparistalep, Cihaz, Lottransc, Uretim, Tezgahstatu, Uygunsuzluklar, Hataraporu, Sevkiyat, Tasks, Usertasks, Dosya, Personel, Prjolcu, Pdk,Pdkbol,Pdklotsaat
    admin = Admin(app, name='MRP Admin', template_mode='bootstrap3')
    admin.add_view(ModelView(Users, db.session, endpoint="users_admin"))
    admin.add_view(ModelView(Firmalar, db.session, endpoint="firmalar_admin"))
    admin.add_view(ModelView(Siparis, db.session, endpoint="siparis_admin"))
    admin.add_view(ModelView(Satir, db.session, endpoint="satir_admin"))
    admin.add_view(ModelView(Lot, db.session, endpoint="lot_admin"))
    admin.add_view(ModelView(Proje, db.session, endpoint="proje_admin"))
    admin.add_view(ModelView(Projerevtakip, db.session, endpoint="projerevtakip_admin"))
    admin.add_view(ModelView(Projeopr, db.session, endpoint="projeopr_admin"))
    admin.add_view(ModelView(Projecihaz, db.session, endpoint="projecihaz_admin"))
    admin.add_view(ModelView(Plan, db.session, endpoint="plan_admin"))
    admin.add_view(ModelView(Planstr, db.session, endpoint="planstr_admin"))
    admin.add_view(ModelView(Cnc, db.session, endpoint="cnc_admin"))
    admin.add_view(ModelView(Malzeme, db.session, endpoint="malzeme_admin"))
    admin.add_view(ModelView(Malztransc, db.session, endpoint="malztransc_admin"))
    admin.add_view(ModelView(Malzstok, db.session, endpoint="malzstok_admin"))
    admin.add_view(ModelView(Mastar, db.session, endpoint="mastar_admin"))
    admin.add_view(ModelView(Operasyon, db.session, endpoint="operasyon_admin"))
    admin.add_view(ModelView(Tedarikci, db.session, endpoint="tedarikci_admin"))
    admin.add_view(ModelView(Siparistalep, db.session, endpoint="siparistalep_admin"))
    admin.add_view(ModelView(Cihaz, db.session, endpoint="cihaz_admin"))
    admin.add_view(ModelView(Lottransc, db.session, endpoint="lottransc_admin"))
    admin.add_view(ModelView(Uretim, db.session, endpoint="uretim_admin"))
    admin.add_view(ModelView(Tezgahstatu, db.session, endpoint="tezgahstatu_admin"))
    admin.add_view(ModelView(Uygunsuzluklar, db.session, endpoint="uygunsuzluklar_admin"))
    admin.add_view(ModelView(Hataraporu, db.session, endpoint="hataraporu_admin"))
    admin.add_view(ModelView(Sevkiyat, db.session, endpoint="sevkiyat_admin"))
    admin.add_view(ModelView(Tasks, db.session, endpoint="tasks_admin"))
    admin.add_view(ModelView(Usertasks, db.session, endpoint="usertasks_admin"))
    admin.add_view(ModelView(Dosya, db.session, endpoint="dosya_admin"))
    admin.add_view(ModelView(Personel, db.session, endpoint="personel_admin"))
    admin.add_view(ModelView(Prjolcu, db.session, endpoint="olcu_admin"))
    admin.add_view(ModelView(Prjolcu, db.session, endpoint="prjolcu_admin"))
    admin.add_view(ModelView(Prjolcu, db.session, endpoint="pdk_admin"))
    admin.add_view(ModelView(Prjolcu, db.session, endpoint="pdkbol_admin"))
    admin.add_view(ModelView(Prjolcu, db.session, endpoint="pdklotsaat_admin"))



    @login_manager.user_loader
    def load_user(user_id):
        return db.get_or_404(Users, user_id)

    with app.app_context():
        db.create_all()

    return app