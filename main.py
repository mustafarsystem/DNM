
from datetime import date, datetime
from email.policy import default
from enum import unique
from collections import Counter
from flask import Flask, abort, render_template, redirect, url_for, flash, request, jsonify
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Date, Boolean, ForeignKey, and_, Float, desc, func, or_, DateTime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap5
from forms import LoginForm, FirmForm, SiparisForm
from math import ceil
import os
from dotenv import load_dotenv



'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''


load_dotenv()
secret_key = os.getenv("SECRET_KEY")
database_url = os.getenv("DATABASE_URL")

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key

Bootstrap5(app)

#Flask Login

login_manager=LoginManager()
login_manager.init_app(app)

count=None

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(Users,user_id)

#Users için db oluştur

class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Users(UserMixin,db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
    division: Mapped[str] = mapped_column(String(1000))

class Firmalar(db.Model):
    __tablename__ = "firmalar"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(1000),unique=True, nullable=False)
    vergi_no: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    vergi_d: Mapped[str] = mapped_column(String(1000), nullable=True)
    adres: Mapped[str] = mapped_column(String(1000), nullable=True)
    ilgili: Mapped[str] = mapped_column(String(1000), nullable=True)
    firma=relationship("Siparis", back_populates="firma")



class Siparis(db.Model):
    __tablename__ = "siparis"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    firma= relationship("Firmalar", back_populates="firma")
    firma_id: Mapped[int] = mapped_column(Integer, ForeignKey('firmalar.id'))
    sip_no: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    sip_rev_no: Mapped[str] = mapped_column(String(10), unique=False, nullable=True)
    stn_alma: Mapped[str] = mapped_column(String(100), unique=False, nullable=True)
    teklif_no: Mapped[str] = mapped_column(String(20), unique=False, nullable=False)
    sip_tarh: Mapped[date] = mapped_column(Date, default=date.today())
    sip_stat: Mapped[int] = mapped_column(Integer, default=1, unique=False, nullable=False)
    satir= relationship("Satir", back_populates="sip")


class Satir(db.Model):
    __tablename__ = "satirlar"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sip_id: Mapped[int] = mapped_column(Integer, ForeignKey('siparis.id'))
    str_no: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)
    proje_id: Mapped[int]=mapped_column(Integer,ForeignKey('proje.id'))
    urn = relationship("Proje", back_populates="project")
    ad: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)
    kalf: Mapped[int] = mapped_column(Integer, default=0, unique=False, nullable=True)
    satr_stat: Mapped[str] = mapped_column(String(250), unique=False, default="İşleme Alındı", nullable=True)
    ter_tarh: Mapped[date] = mapped_column(Date, default=date.today())
    sip = relationship("Siparis", back_populates="satir")
    sevk = relationship("Sevkiyat", back_populates="satir")



class Lot(db.Model):
    __tablename__ = "lot"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lot_no: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    proje_id: Mapped[int] = mapped_column(Integer, ForeignKey('proje.id'))
    proje = relationship("Proje", back_populates="lot")
    opr_id: Mapped[int] = mapped_column(Integer, ForeignKey('operasyon.id'))
    opr_name = relationship('Operasyon')
    ad: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey('plan.id'))
    plan = relationship('Plan')
    sure: Mapped[int] = mapped_column(Integer, unique=False, nullable=True)
    fire_ad: Mapped[int] = mapped_column(Integer, unique=False, nullable=True)
    malz_id: Mapped[int] = mapped_column(Integer, unique=False,nullable=True)
    lot_stat: Mapped[str] = mapped_column(String(100), unique=False, nullable=True)
    tarih: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    malz = relationship("Malztransc", back_populates="lot")
    sevk = relationship("Sevkiyat", back_populates="lot")
    operator_id: Mapped[int] = mapped_column(Integer, ForeignKey('personel.id'), nullable=True)
    operator = relationship("Personel", back_populates="oprtr")




class Proje(db.Model):
    __tablename__ = "proje"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    urn_no: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    tkr_no: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    tkr_rev_no: Mapped[str] = mapped_column(String(10), unique=False, nullable=False)
    urn_adi: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    prj_no: Mapped[str] = mapped_column(String(250), unique=True, nullable=True)
    prj_rev = relationship('Projerevtakip', back_populates="prj")
    kal_class: Mapped[str] = mapped_column(String(50), unique=False, nullable=True)
    cap: Mapped[float]=mapped_column(Float,unique=False,nullable=True)
    boy: Mapped[float] = mapped_column(Float, unique=False, nullable=True)
    project=relationship("Satir", back_populates="urn")
    malz_id: Mapped[int] = mapped_column(Integer, ForeignKey('malzeme.id'), nullable=True)
    malz = relationship('Malzeme')
    lot = relationship('Lot', back_populates="proje")
    cihaz = relationship('Projecihaz', back_populates="proje")
    prog: Mapped[str] = mapped_column(String(250), unique=False, nullable=True)
    stat: Mapped[str] = mapped_column(String(250), default="Açık",unique=False, nullable=True)
    opr = relationship('Projeopr', back_populates="proje")
    malz_sah: Mapped[str] = mapped_column(String(250), unique=False, nullable=True)
    proj_rev_no: Mapped[int] = mapped_column(Integer, default=0,  nullable=True)
    teklif_sure: Mapped[int] = mapped_column(Integer, nullable=True)
    yay_tarh: Mapped[date] = mapped_column(Date, default=date.today(), nullable=True)
    rev_tarh: Mapped[date] = mapped_column(Date, default=date.today(), nullable=True)

class Projerevtakip(db.Model):
    __tablename__ = "projerevtakip"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prj_id: Mapped[int] = mapped_column(Integer, ForeignKey('proje.id'), nullable=False)
    prj_rev_no: Mapped[int] = mapped_column(Integer, unique=False, nullable=True)
    rev_tarh: Mapped[date] = mapped_column(Date, default=date.today())
    prj = relationship('Proje', back_populates="prj_rev")


class Projecihaz(db.Model):
    __tablename__ = "projecihaz"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prj_id: Mapped[int] = mapped_column(Integer, ForeignKey('proje.id'), nullable=False)
    cihaz_id: Mapped[int] = mapped_column(Integer, ForeignKey('mastar.id'), nullable=False)
    cihaz = relationship('Mastar')
    proje = relationship('Proje', back_populates="cihaz")


class Projeopr(db.Model):
    __tablename__ = "projeopr"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prj_id: Mapped[int] = mapped_column(Integer, ForeignKey('proje.id'), nullable=False)
    opr_id: Mapped[int] = mapped_column(Integer, ForeignKey('operasyon.id'), nullable=False)
    opr_sira_no: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)
    opr_desc: Mapped[int] = mapped_column(Integer, unique=False, nullable=True)
    proje = relationship('Proje', back_populates="opr")
    oprsyn = relationship('Operasyon')

class Plan(db.Model):
    __tablename__ = "plan"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    proje_id: Mapped[int] = mapped_column(Integer, ForeignKey('proje.id'))
    proje = relationship('Proje')
    cnc_id: Mapped[int] = mapped_column(Integer, ForeignKey('cnc.id'))
    cnc = relationship('Cnc')
    ad: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)
    malz_id: Mapped[int] = mapped_column(Integer, ForeignKey('malztransc.id'), nullable=True)
    malz = relationship('Malztransc', foreign_keys=[malz_id], cascade="all, delete")
    plan_stat: Mapped[int] = mapped_column(Integer, unique=False, default=0, nullable=False)
    malz_ad: Mapped[int] = mapped_column(Integer, unique=False, nullable=True)
    toplam_sure: Mapped[int] = mapped_column(Integer, unique=False, nullable=True)
    plan_sira_no: Mapped[int] = mapped_column(Integer, unique=False, nullable=True)
    malz_name: Mapped[str] = mapped_column(String(100), unique=False, nullable=True)
    ter_tarh: Mapped[date] = mapped_column(Date, default=date.today())
    planstr = relationship('Planstr', back_populates="plan", cascade="all, delete")

class Planstr(db.Model):
    __tablename__ = "planstr"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey('plan.id'))
    str_id: Mapped[int] = mapped_column(Integer, ForeignKey('satirlar.id'))
    plan_ad: Mapped[int] = mapped_column(Integer, unique=False, default=0, nullable=True)
    plan = relationship('Plan', back_populates="planstr")
    str = relationship('Satir')

class Cnc(db.Model):
    __tablename__ = "cnc"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    marka: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    model: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    cnc_no: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    maks_cap: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)


class Malzeme(db.Model):
    __tablename__ = "malzeme"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    malz_name: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    malz_standrt: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)

class Mastar(db.Model):
    __tablename__ = "mastar"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mastar_type: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    mastar_name: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)


class Operasyon(db.Model):
    __tablename__ = "operasyon"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    opr_tip: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    opr_name: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)


class Malzstok(db.Model):
    __tablename__ = "malzstok"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    malz_no: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    malz_name: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    malz_stndrt: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    raf_no: Mapped[str] = mapped_column(String(10), unique=False, nullable=False)
    irs_no: Mapped[str] = mapped_column(String(10), unique=False, nullable=False)
    ted_id: Mapped[int] = mapped_column(Integer, ForeignKey('tedarikci.id'), )
    ted = relationship('Tedarikci')
    gir_tarh: Mapped[date] = mapped_column(Date, default=date.today())
    malz_cins: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    agirlik: Mapped[float] = mapped_column(Float, unique=False, nullable=True)
    cap: Mapped[float] = mapped_column(Float, unique=False, nullable=False)
    boy: Mapped[float] = mapped_column(Float, unique=False, nullable=False)
    ad: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)
    malz_transc = relationship("Malztransc", back_populates="malz", cascade="all, delete")
    siparistalep_id: Mapped[int] = mapped_column(Integer, ForeignKey('siptalep.id'))
    siparistalep = relationship("Siparistalep")
    malz_sahp: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)


class Tedarikci(db.Model):
    __tablename__ = "tedarikci"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tedarik_type: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    tedarik_name: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)


class Malztransc(db.Model):
    __tablename__ = "malztransc"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transc_type: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    ad: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)
    malz_id: Mapped[int] = mapped_column(Integer, ForeignKey('malzstok.id'))
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey('plan.id', ondelete='CASCADE'))
    malz = relationship("Malzstok", back_populates="malz_transc")
    lot_id: Mapped[int] = mapped_column(Integer, ForeignKey('lot.id'), nullable=True)
    lot = relationship("Lot", back_populates="malz")
    tarh: Mapped[date] = mapped_column(Date, default=date.today())
    descrp: Mapped[str] = mapped_column(String(500), unique=False, nullable=True)


class Siparistalep(db.Model):
    __tablename__ = "siptalep"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    talep_no: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    talep_type: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    malz_id: Mapped[int] = mapped_column(Integer, ForeignKey('malzeme.id'), nullable=True)
    malz = relationship("Malzeme")
    cihaz_id: Mapped[int] = mapped_column(Integer, ForeignKey('cihaz.id'), nullable=True)
    cihaz = relationship("Cihaz")
    lot_id: Mapped[int] = mapped_column(Integer, ForeignKey('lot.id'), nullable=True)
    lot = relationship("Lot")
    tedarikci_id: Mapped[int] = mapped_column(Integer, ForeignKey('tedarikci.id'), nullable=True)
    tedarikci = relationship("Tedarikci")
    talep_tarh: Mapped[date] = mapped_column(Date, default=date.today())
    ad: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)

class Cihaz(db.Model):
    __tablename__ = "cihaz"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cihaz_no: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    cihaz_type: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    cihaz_name: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    uygunluk_stat: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    gir_tarh: Mapped[date] = mapped_column(Date, default=date.today())
    bolum: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    marka: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    kalib_periot: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)
    kalib_tarh: Mapped[date] = mapped_column(Date, default=date.today())


class Lottransc(db.Model):
    __tablename__ = "lottransc"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lot_id: Mapped[int] = mapped_column(Integer, ForeignKey('lot.id'), nullable=False)
    lot = relationship("Lot")
    transc_type: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    opr_id: Mapped[int] = mapped_column(Integer, ForeignKey('operasyon.id'), nullable=False)
    opr = relationship("Operasyon")
    ad: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)
    siparistalep_id: Mapped[int] = mapped_column(Integer, ForeignKey('siptalep.id'))
    siptalep = relationship("Siparistalep")
    sevk = relationship("Sevkiyat", back_populates="lot_transc")
    tarh: Mapped[date] = mapped_column(Date, default=date.today())



class Duruslar(db.Model):
    __tablename__ = "duruslar"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    durus_name: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    durus_baslık: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)

class Uygunsuzluklar(db.Model):
    __tablename__ = "uygunsuzluklar"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uygnslk_name: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)

class Hataraporu(db.Model):
    __tablename__ = "hataraporu"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lot_id: Mapped[int] = mapped_column(Integer, ForeignKey('lot.id'), nullable=False)
    lot = relationship("Lot")
    operasyon_id: Mapped[int] = mapped_column(Integer, ForeignKey('operasyon.id'), nullable=False)
    operasyon = relationship("Operasyon")
    uygnslk_id: Mapped[int] = mapped_column(Integer, ForeignKey('uygunsuzluklar.id'), nullable=False)
    uygunsuzluk = relationship("Uygunsuzluklar")
    ad: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)
    descr_uyg: Mapped[str] = mapped_column(String(1000), unique=False, nullable=True)

class Sevkiyat(db.Model):
    __tablename__ = "sevkiyat"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sevk_no: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    satir_id: Mapped[int] = mapped_column(Integer, ForeignKey('satirlar.id'), nullable=False)
    satir = relationship("Satir", back_populates="sevk")
    lot_id: Mapped[int] = mapped_column(Integer, ForeignKey('lot.id'), nullable=False)
    lot = relationship("Lot", back_populates="sevk")
    lottransc_id: Mapped[int] = mapped_column(Integer, ForeignKey('lottransc.id'), nullable=False)
    lot_transc = relationship("Lottransc", back_populates="sevk" )

class Uretim(db.Model):
    __tablename__ = "uretim"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lot_id: Mapped[int] = mapped_column(Integer, ForeignKey('lot.id'), nullable=False)
    lot = relationship("Lot")
    ur_ad: Mapped[int] = mapped_column(Integer, unique=False, nullable=True)
    durus_id: Mapped[int] = mapped_column(Integer, ForeignKey('duruslar.id'), nullable=True)
    durus = relationship("Duruslar")
    durus_suresi: Mapped[int] = mapped_column(Integer, unique=False, nullable=True)
    descr_durus: Mapped[str] = mapped_column(String(1000), unique=False, nullable=True)
    tarih: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Tasks(db.Model):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_name: Mapped[str] = mapped_column(String(1000), unique=False, nullable=False)

class Usertasks(db.Model):
    __tablename__ = "usertasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey('tasks.id'), nullable=False)
    task = relationship("Tasks")
    user = relationship("Users")
    task_stat: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)

class Dosya(db.Model):
    __tablename__ = "dosya"
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(255))
    yol = db.Column(db.String(255))  # dosya yolu
    tur = db.Column(db.String(50))   # 'pdf', 'xlsx' vs

class Personel(db.Model):
    __tablename__ = "personel"
    id = db.Column(db.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    name: Mapped[str] = mapped_column(String(1000), unique=False, nullable=False)
    division = relationship("Users")
    oprtr = relationship("Lot", back_populates="operator")


with app.app_context():
    db.create_all()



#manuel kullanıcı ekle
# ps = generate_password_hash("M6609167g", method='pbkdf2:sha256', salt_length=8)
# with app.app_context():
#
#     new_user = Users(email="mustafa.gulseven@cerenotomat.com", password=ps, name="Mustafa Gülseven",division="Admin")
#     db.session.add(new_user)
#     db.session.commit()

# with app.app_context():
#     new_firma=Firmalar(name="Roketsan")
#     new_firma2=Firmalar(name="Kale Kalıp")
#     new_firma3 = Firmalar(name="Bimed")
#
#     db.session.add(new_firma2)
#     db.session.add(new_firma3)
#     db.session.add(new_firma)
#     db.session.commit()


@app.route("/")
def home():
    return render_template("index.html",user=current_user)



@app.route('/login',methods=["GET","POST"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        email=form.email.data
        password=form.password.data

        #find the user
        result=db.session.execute(db.select(Users).where(Users.email==email))
        user=result.scalar()
        #password check
        if check_password_hash(user.password,password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash("Email ya da şifre hatalı")
            return redirect(url_for('login'))
    return render_template("login.html", form=form,logged_in=current_user.is_authenticated, user=current_user)




@app.route("/siparis-ekle",methods=["GET","POST"])
def siparis():


    firmalar = db.session.execute(db.select(Firmalar).order_by(Firmalar.id)).scalars().all()
    satirlar = db.session.execute(db.select(Satir).order_by(Satir.id)).scalars().all()

    page = request.args.get("page", 1, type=int)
    per_page = 50
    toplam_kayit = Siparis.query.count()
    orders = Siparis.query.order_by(Siparis.sip_tarh).offset((page - 1) * per_page).limit(per_page).all()
    total_pages = ceil(toplam_kayit / per_page)

    page_to_render = []
    if page > 1:
        if page == total_pages:
            for p in range(1, page-1):
                if p == 1:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    page_to_render.append(page-1)
                    page_to_render.append(page)
                    break
        else:
            for p in range(1, page - 1):

                if p == 1:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    break

            for p in range(page - 1, page + 2):
                page_to_render.append(p)


            for p in range(page + 2, total_pages + 1):
                if p == total_pages:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    page_to_render.append(total_pages)
                    break
    else:
        for p in range(1, total_pages + 1):
            if p == 1 or p <= 3:
                page_to_render.append(p)
            else:
                page_to_render.append('p')
                page_to_render.append(total_pages)
                break

    if request.method=='POST':
      #Sipariş  ekleme
        print('bu çalıştı')
        order_firm=request.form['firma']
        order_no=request.form['sip-no-modal']
        order_rev=request.form['sip-rev-modal']
        ilgili=request.form['ilgili']
        teklif_no = request.form['teklif-no']
        order_date = request.form['sip-tarih']
        new_order_date = datetime.strptime(order_date, '%Y-%m-%d')

        firm_to_add = db.session.execute(db.select(Firmalar).where(Firmalar.name == order_firm)).scalar()
        new_order=Siparis(
            firma_id=firm_to_add.id,
            sip_no=order_no,
            sip_rev_no=order_rev,
            stn_alma=ilgili,
            teklif_no=teklif_no,
            sip_tarh=new_order_date,
        )
        db.session.add(new_order)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Hata durumunda değişiklikleri geri al
            print(f"Hata: {str(e)}")  # Hata mesajını yazdır

        #Sipariş Satırı ekleme
        order_items_data = []
        row_no= request.form.getlist('order_items[][satır-no]')
        product_no = request.form.getlist('order_items[][urun-kodu]')
        drw_no = request.form.getlist('order_items[][teknik-resim-no]')
        rev_no = request.form.getlist('order_items[][rev-no]')
        product_name=request.form.getlist('order_items[][urun-tanımı]')
        order_quant = request.form.getlist('order_items[][adet]')
        deadline=request.form.getlist('order_items[][ter-tarih]')
        qualification=request.form.getlist('order_items[][kalifikasyon]')
        quality_class = request.form.getlist('order_items[][kal-sınıfı]')

        for i in range(len(row_no)):
            order_items_data.append({
                'row_no': row_no[i],
                'product_no': product_no[i],
                'drw_no': drw_no[i],
                'rev_no': rev_no[i],
                'product_name': product_name[i],
                'order_quant': order_quant[i],
                'deadline': datetime.strptime(deadline[i], '%Y-%m-%d'),
                'qualification': qualification[i],
                'quality_class': quality_class[i]
            })
        print(order_items_data)
        for item in order_items_data:

            result = db.session.execute(db.select(Proje).where(Proje.urn_no == item['product_no'],Proje.tkr_rev_no == item['rev_no']))
            product = result.scalar()
            if product is None:
                new_proje=Proje(
                    urn_no=item['product_no'],
                    tkr_no=item['drw_no'],
                    tkr_rev_no=item['rev_no'],
                    urn_adi=item['product_name'],
                    kal_class=item["quality_class"]

                )
                db.session.add(new_proje)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()  # Hata durumunda değişiklikleri geri al
                    print(f"Hata: {str(e)}")  # Hata mesajını yazdır
                result = db.session.execute(db.select(Proje).where(Proje.urn_no == item['product_no'],Proje.tkr_rev_no == item['rev_no']))
                product = result.scalar()


            new_line=Satir(
                sip_id=new_order.id,
                str_no=item["row_no"],
                proje_id=product.id,
                ad=item['order_quant'],
                kalf=item['qualification'],
                ter_tarh=item['deadline']
            )
            db.session.add(new_line)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()  # Hata durumunda değişiklikleri geri al
                print(f"Hata: {str(e)}")  # Hata mesajını yazdır


        return redirect(url_for("siparis"))




    return render_template("sipariş_ekle.html",logged_in=current_user.is_authenticated,user=current_user,orders=orders, firmalar=firmalar, page=page, total_pages=total_pages, lines=satirlar, toplam_kayit=toplam_kayit, page_to_render=page_to_render)


@app.route("/firma-ekle",methods=["GET","POST"])
def firma_ekle():
    firma_form=FirmForm()
    firmalar = db.session.execute(db.select(Firmalar).order_by(Firmalar.id)).scalars().all()
    if firmalar == None:
        firmalar = []

    if request.method == 'POST':
        firm_name=firma_form.name.data
        firm_verg_no=firma_form.vergi_no.data
        firm_vergi_d=firma_form.vergi_d.data
        firm_ilgili=firma_form.ilgili.data
        firm_adres=firma_form.adres.data



        new_firm=Firmalar(name=firm_name,vergi_no=firm_verg_no,vergi_d=firm_vergi_d,ilgili=firm_ilgili,adres=firm_adres)
        db.session.add(new_firm)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Hata durumunda değişiklikleri geri al
            print(f"Hata: {str(e)}")  # Hata mesajını yazdır
        return redirect(url_for("firma_ekle"))



    return render_template("firma-ekle.html",form=firma_form, logged_in=current_user.is_authenticated, user=current_user, firmalar=firmalar)


@app.route("/firma-sil/<int:firm_id>",methods=["GET","POST"])
def firma_sil(firm_id):
    firm_to_delete= db.get_or_404(Firmalar,firm_id)
    db.session.delete(firm_to_delete)
    db.session.commit()
    return redirect(url_for('firma_ekle'))


@app.route("/firma-edit/<int:firm_id>",methods=["GET","POST"])
def firma_edit(firm_id):
    firm_to_edit= db.get_or_404(Firmalar, firm_id)
    edit_form=FirmForm(
        name=firm_to_edit.name,
        vergi_no=firm_to_edit.vergi_no,
        vergi_d=firm_to_edit.vergi_d,
        adres=firm_to_edit.adres,
        ilgili=firm_to_edit.ilgili

    )
    if request.method == 'POST':
        firm_to_edit.name=edit_form.name.data
        firm_to_edit.vergi_no=edit_form.vergi_no.data
        firm_to_edit.vergi_d=edit_form.vergi_d.data
        firm_to_edit.adres=edit_form.adres.data
        firm_to_edit.ilgili=edit_form.ilgili.data

        db.session.commit()
        return redirect(url_for('firma_ekle'))
    return render_template("firma-ekle.html", form=edit_form,is_edit=True,logged_in=current_user.is_authenticated, user=current_user)

@app.route("/siparis-edit/<int:sip_id>",methods=["GET","POST"])
def siparis_edit(sip_id):
    siparis_to_edit= db.get_or_404(Siparis,sip_id)
    firmalar = db.session.execute(db.select(Firmalar).order_by(Firmalar.id)).scalars().all()
    satirlar = db.session.execute(db.select(Satir).where(Satir.sip_id == sip_id))
    lines = satirlar.scalars().all()
    print(lines)
    if request.method=='POST':



        order_firm=request.form['firma']
        order_no=request.form['sip-no-modal']
        order_rev=request.form['sip-rev-modal']
        ilgili=request.form['ilgili']
        teklif_no = request.form['teklif-no']
        order_date = request.form['sip-tarih']
        new_order_date = datetime.strptime(order_date, '%Y-%m-%d')

        firm_to_edit = db.session.execute(db.select(Firmalar).where(Firmalar.name == order_firm)).scalar()

        # sipariş başlık bilgilerini güncelle

        siparis_to_edit.firma_id = firm_to_edit.id
        siparis_to_edit.sip_no = order_no
        siparis_to_edit.sip_rev_no = order_rev
        siparis_to_edit.stn_alma = ilgili
        siparis_to_edit.teklif_no = teklif_no
        siparis_to_edit.sip_tarh = new_order_date
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Hata durumunda değişiklikleri geri al
            print(f"Hata: {str(e)}")  # Hata mesajını yazdır







        order_items_data = []
        row_no= request.form.getlist('order_items[][satır-no]')
        product_no = request.form.getlist('order_items[][urun-kodu]')
        drw_no = request.form.getlist('order_items[][teknik-resim-no]')
        rev_no = request.form.getlist('order_items[][rev-no]')
        product_name=request.form.getlist('order_items[][urun-tanımı]')
        order_quant = request.form.getlist('order_items[][adet]')
        deadline=request.form.getlist('order_items[][ter-tarih]')
        qualification=request.form.getlist('order_items[][kalifikasyon]')
        quality_class = request.form.getlist('order_items[][kal-sınıfı]')
        row_id = request.form.getlist('order_items[][id]')

        for i in range(len(row_no)):
            order_items_data.append({
                'row_no': row_no[i],
                'product_no': product_no[i],
                'drw_no': drw_no[i],
                'rev_no': rev_no[i],
                'product_name': product_name[i],
                'order_quant': order_quant[i],
                'deadline': datetime.strptime(deadline[i], '%Y-%m-%d'),
                'qualification': qualification[i],
                'quality_class': quality_class[i],
                'row_id': row_id[i]
            })
        print(order_items_data)
        for item in order_items_data:
            satir_result=db.get_or_404(Satir, item['row_id'])
            proje_id=satir_result.proje_id

            project_to_edit = db.get_or_404(Proje, proje_id)
            project_to_edit.urn_no=item['product_no']
            project_to_edit.tkr_no=item['drw_no']
            project_to_edit.tkr_rev_no=item['rev_no']
            project_to_edit.urn_adi=item['product_name']
            project_to_edit.kal_class = item["quality_class"]
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()  # Hata durumunda değişiklikleri geri al
                print(f"Hata: {str(e)}")  # Hata mesajını yazdır



            satir_result.str_no=item["row_no"]
            satir_result.proje_id=proje_id
            satir_result.ad=item['order_quant']
            satir_result.kalf=item['qualification']
            satir_result.ter_tarh=item['deadline']

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()  # Hata durumunda değişiklikleri geri al
                print(f"Hata: {str(e)}")  # Hata mesajını yazdır

        return redirect(url_for('siparis_edit',sip_id=sip_id))





    return render_template("sip-edit.html",is_str=False, logged_in=current_user.is_authenticated, user=current_user, order=siparis_to_edit,firmalar=firmalar, lines=lines)


@app.route("/satir-ekle/<int:sip_id>",methods=["GET","POST"])
def satir_ekle(sip_id):
    siparis_to_edit = db.get_or_404(Siparis, sip_id)
    firmalar = db.session.execute(db.select(Firmalar).order_by(Firmalar.id)).scalars().all()
    satirlar = db.session.execute(db.select(Satir).where(Satir.sip_id == sip_id))
    lines = satirlar.scalars().all()

    if request.method == 'POST':
        order_items_data = []
        row_no = request.form.getlist('order_items1[][satır-no]')
        product_no = request.form.getlist('order_items1[][urun-kodu]')
        drw_no = request.form.getlist('order_items1[][teknik-resim-no]')
        rev_no = request.form.getlist('order_items1[][rev-no]')
        product_name = request.form.getlist('order_items1[][urun-tanımı]')
        order_quant = request.form.getlist('order_items1[][adet]')
        deadline = request.form.getlist('order_items1[][ter-tarih]')
        qualification = request.form.getlist('order_items1[][kalifikasyon]')
        quality_class = request.form.getlist('order_items1[][kal-sınıfı]')

        for i in range(len(row_no)):
            order_items_data.append({
                'row_no': row_no[i],
                'product_no': product_no[i],
                'drw_no': drw_no[i],
                'rev_no': rev_no[i],
                'product_name': product_name[i],
                'order_quant': order_quant[i],
                'deadline': datetime.strptime(deadline[i], '%Y-%m-%d'),
                'qualification': qualification[i],
                'quality_class': quality_class[i]
            })
        print(order_items_data)
        for item in order_items_data:

            result = db.session.execute(db.select(Proje).where(Proje.urn_no == item['product_no'], Proje.tkr_rev_no == item['rev_no']))
            product = result.scalar()
            if product is None:
                new_proje = Proje(
                    urn_no=item['product_no'],
                    tkr_no=item['drw_no'],
                    tkr_rev_no=item['rev_no'],
                    urn_adi=item['product_name'],
                    kal_class=item["quality_class"]

                )
                db.session.add(new_proje)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()  # Hata durumunda değişiklikleri geri al
                    print(f"Hata: {str(e)}")  # Hata mesajını yazdır
                result = db.session.execute(db.select(Proje).where(Proje.urn_no == item['product_no'], Proje.tkr_rev_no == item['rev_no']))
                product = result.scalar()

            new_line = Satir(
                sip_id=sip_id,
                str_no=item["row_no"],
                proje_id=product.id,
                ad=item['order_quant'],
                kalf=item['qualification'],
                ter_tarh=item['deadline']
            )
            db.session.add(new_line)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()  # Hata durumunda değişiklikleri geri al
                print(f"Hata: {str(e)}")  # Hata mesajını yazdır

        return redirect(url_for('siparis_edit', sip_id=sip_id))

    return render_template("sip-edit.html",is_str=True, logged_in=current_user.is_authenticated, user=current_user,order=siparis_to_edit, firmalar=firmalar, lines=lines)




@app.route("/satir-sil/<int:str_id>/<int:sip_id>",methods=["GET","POST"])
def satir_sil(str_id,sip_id):
    satir_to_delete = db.get_or_404(Satir, str_id)
    db.session.delete(satir_to_delete)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    return redirect(url_for('siparis_edit',sip_id=sip_id ))

@app.route("/siparis-sil/<int:sip_id>",methods=["GET","POST"])
def siparis_sil(sip_id):
    lines_to_delete = db.session.execute(db.select(Satir).where(Satir.sip_id == sip_id)).scalars().all()
    for line in lines_to_delete:
        db.session.delete(line)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Hata durumunda değişiklikleri geri al
            print(f"Hata: {str(e)}")  # Hata mesajını yazdır


    siparis_to_delete = db.get_or_404(Siparis,sip_id)
    db.session.delete(siparis_to_delete)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    return redirect(url_for('siparis'))

@app.route("/sip-filtre", methods=["GET","POST"])
def sip_filtre():
    firmalar = db.session.execute(db.select(Firmalar).order_by(Firmalar.id)).scalars().all()
    satirlar = db.session.execute(db.select(Satir).order_by(Satir.id)).scalars().all()



    firm_filtre = request.args.get('firma','')
    sipno_filtre = request.args.get('sipariş_no','')
    urnno_filtre = request.args.get('parca_no','')
    rsmno_filtre = request.args.get('resim_no','')
    revno_filtre = request.args.get('parca_rev','')
    btrh = request.args.get('b_tarih','')
    btrh_filtre=datetime.strptime(btrh, '%Y-%m-%d')
    strh = request.args.get('s_tarih','')
    strh_filtre=datetime.strptime(strh, '%Y-%m-%d')
    statu_filtre = int(request.args.get('statu',''))
    print(f"sipno={sipno_filtre} ")

    query=db.session.query(Siparis)

    if firm_filtre:
        query=query.filter(Siparis.firma.has(Firmalar.name.ilike(f"%{firm_filtre}%")))
        print("firma çalıştı")
    if sipno_filtre:
        query=query.filter(Siparis.sip_no.ilike(f"%{sipno_filtre}%"))
        print("sipno çalıştı")
    if urnno_filtre:
        query=query.filter(Siparis.satir.any(Satir.urn.has(Proje.urn_no.ilike(f"%{urnno_filtre}%"))))
        print("urnno çalıştı")
    if rsmno_filtre:
        query=query.filter(Siparis.satir.any(Satir.urn.has(Proje.tkr_no.ilike(f"%{rsmno_filtre}%"))))
        print("resimno çalıştı")
    if revno_filtre:
        query=query.filter(Siparis.satir.any(Satir.urn.has(Proje.tkr_rev_no.ilike(f"%{revno_filtre}%"))))
        print("revno çalıştı")
    if statu_filtre != 2:
        query=query.filter(Siparis.sip_stat == statu_filtre)
        print("statu çalıştı")
    if btrh and strh:
        query = query.filter(Siparis.sip_tarh.between(btrh_filtre, strh_filtre))
        toplam_kayit = query.count()
        print(toplam_kayit)

    page = request.args.get("page", 1, type=int)
    per_page = 50
    toplam_kayit = query.count()
    total_pages = ceil(toplam_kayit / per_page)

    results = query.offset((page - 1) * per_page).limit(per_page).all()

    page_to_render = []
    if page > 1:
        if page == total_pages:
            for p in range(1, page - 1):
                if p == 1:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    page_to_render.append(page - 1)
                    page_to_render.append(page)
                    break
        else:
            for p in range(1, page - 1):

                if p == 1:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    break

            for p in range(page - 1, page + 2):
                page_to_render.append(p)

            for p in range(page + 2, total_pages + 1):
                if p == total_pages:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    page_to_render.append(total_pages)
                    break
    else:
        for p in range(1, total_pages + 1):
            if p == 1 or p <= 3:
                page_to_render.append(p)
            else:
                page_to_render.append('p')
                page_to_render.append(total_pages)
                break


    for order in results:
        print(f"order no={order.sip_no}")
    return render_template("sip-filtre.html", logged_in=current_user.is_authenticated, user=current_user,orders=results, firmalar=firmalar, page=page, total_pages=total_pages, lines=satirlar, toplam_kayit=toplam_kayit, page_to_render=page_to_render)


@app.route("/sip-info", methods=["GET","POST"])
def sip_info():


    firm_filtre = request.args.get('firma', '')
    sipno_filtre = request.args.get('sipariş_no', '')
    urnno_filtre = request.args.get('parca_no', '')
    rsmno_filtre = request.args.get('resim_no', '')
    revno_filtre = request.args.get('parca_rev', '')
    btrh = request.args.get('b_tarih', '')
    if btrh:
        try:
            btrh_filtre = datetime.strptime(btrh, '%Y-%m-%d')
        except ValueError:
            btrh_filtre = None
    else:
        btrh_filtre=None
    strh = request.args.get('s_tarih', '')
    if strh:
        try:
            strh_filtre = datetime.strptime(strh, '%Y-%m-%d')
        except ValueError:
            strh_filtre = None
    else:
        strh_filtre=None

    statu_filtre = request.args.get('statu', '')
    # if statu_filtre:
    #     try:
    #         statu_filtre = int(request.args.get('statu', ''))
    #     except ValueError:
    #         statu_filtre = 2
    # else:
    #     statu_filtre = 2


    query=db.session.query(Satir)

    if firm_filtre:
        query=query.filter(Satir.sip.has(Siparis.firma.has(Firmalar.name.ilike(f"%{firm_filtre}%"))))
        print(f"firma:{firm_filtre}")
    if sipno_filtre:
        query=query.filter(Satir.sip.has(Siparis.sip_no.ilike(f"%{sipno_filtre}%")))
        print(f"sip:{sipno_filtre}")
    if urnno_filtre:
        query=query.filter(Satir.urn.has(Proje.urn_no.ilike(f"%{urnno_filtre}%")))
        print(f"urnno:{urnno_filtre}")
    if rsmno_filtre:
        query=query.filter(Satir.urn.has(Proje.tkr_no.ilike(f"%{rsmno_filtre}%")))
    if revno_filtre:
        query=query.filter(Satir.urn.has(Proje.tkr_rev_no.ilike(f"%{revno_filtre}%")))
    if statu_filtre != '2':
        query=query.filter(Satir.satr_stat == statu_filtre)
    if btrh_filtre and strh_filtre:
        query = query.filter(Satir.ter_tarh.between(btrh_filtre, strh_filtre))
        toplam_kayit = query.count()

    page = request.args.get("page", 1, type=int)
    per_page = 50
    toplam_kayit = query.count()
    total_pages = ceil(toplam_kayit / per_page)
    lines = query.offset((page - 1) * per_page).limit(per_page).all()

    page_to_render = []
    if page > 1:
        if page == total_pages:
            for p in range(1, page - 1):
                if p == 1:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    page_to_render.append(page - 1)
                    page_to_render.append(page)
                    break
        else:
            for p in range(1, page - 1):

                if p == 1:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    break

            for p in range(page - 1, page + 2):
                page_to_render.append(p)

            for p in range(page + 2, total_pages + 1):
                if p == total_pages:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    page_to_render.append(total_pages)
                    break
    else:
        for p in range(1, total_pages + 1):
            if p == 1 or p <= 3:
                page_to_render.append(p)
            else:
                page_to_render.append('p')
                page_to_render.append(total_pages)
                break
    print(page_to_render)


        #lot bilgileri buraya çekilecek daha sonra

    return render_template("sip-info.html", logged_in=current_user.is_authenticated, user=current_user,orders_lines=lines, page=page, total_pages=total_pages, toplam_kayit=toplam_kayit, page_to_render=page_to_render)

@app.route("/proje", methods=["GET","POST"])
def proje():

    proje_filtre = request.args.get('proje_no', '')
    urnno_filtre = request.args.get('parca_no', '')
    rsmno_filtre = request.args.get('resim_no', '')
    revno_filtre = request.args.get('parca_rev', '')
    btrh = request.args.get('b_tarih', '')
    if btrh:
        try:
            btrh_filtre = datetime.strptime(btrh, '%Y-%m-%d')
        except ValueError:
            btrh_filtre = None
    else:
        btrh_filtre = None
    strh = request.args.get('s_tarih', '')
    if strh:
        try:
            strh_filtre = datetime.strptime(strh, '%Y-%m-%d')
        except ValueError:
            strh_filtre = None
    else:
        strh_filtre = None

    statu_filtre = request.args.get('statu', '')


    query = db.session.query(Proje)

    if proje_filtre:
        query = query.filter(Proje.prj_no.ilike(f"%{proje_filtre}%"))
    if urnno_filtre:
        query = query.filter(Proje.urn_no.ilike(f"%{urnno_filtre}%"))
    if rsmno_filtre:
        query = query.filter(Proje.tkr_no.ilike(f"%{rsmno_filtre}%"))
    if revno_filtre:
        query = query.filter(Proje.tkr_rev_no.ilike(f"%{revno_filtre}%"))
    if statu_filtre != '':
        query = query.filter(Proje.stat == statu_filtre)
    if btrh_filtre and strh_filtre:
        query = query.filter(Proje.yay_tarh.between(btrh_filtre, strh_filtre))
        toplam_kayit = query.count()



    page = request.args.get("page", 1, type=int)
    per_page = 50
    toplam_kayit = query.count()
    parcalar = query.offset((page - 1) * per_page).limit(per_page).all()
    total_pages = ceil(toplam_kayit / per_page)

    page_to_render = []
    if page > 1:
        if page == total_pages:
            for p in range(1, page - 1):
                if p == 1:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    page_to_render.append(page - 1)
                    page_to_render.append(page)
                    break
        else:
            for p in range(1, page - 1):

                if p == 1:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    break

            for p in range(page - 1, page + 2):
                page_to_render.append(p)

            for p in range(page + 2, total_pages + 1):
                if p == total_pages:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    page_to_render.append(total_pages)
                    break
    else:
        for p in range(1, total_pages + 1):
            if p == 1 or p <= 3:
                page_to_render.append(p)
            else:
                page_to_render.append('p')
                page_to_render.append(total_pages)
                break

    return render_template("proje.html", logged_in=current_user.is_authenticated, user=current_user, parcalar=parcalar,page=page,total_pages=total_pages, toplam_kayit=toplam_kayit, page_to_render=page_to_render)


@app.route("/proje-edit/<int:prj_id>", methods=["GET","POST"])
def proje_edit(prj_id):
    proje_to_edit=db.get_or_404(Proje,prj_id)
    malz=[m[0] for m in db.session.query(Malzeme.malz_name).distinct().all()]
    malz_stan = [s[0] for s in db.session.query(Malzeme.malz_standrt).distinct().all()]





    if request.method == "POST":
        urn_adi = request.form['urn_adi']
        sure = request.form['teklif_sure']
        yay_tarih = request.form['yay_tarih']
        if yay_tarih:
            try:
                yay_tarih_filtre = datetime.strptime(yay_tarih, '%Y-%m-%d')
            except ValueError:
                yay_tarih_filtre = None
        else:
            yay_tarih_filtre = None
        prj_no = request.form['prj_no']
        malzeme_name = request.form['malzeme_name']
        malzemestan = request.form['malzemestan']
        malzemesa = request.form['malzemesa']
        isl_cap = float(request.form['isl_cap'])
        parc_boy = float(request.form['parc_boy'])
        kal_sınıf = request.form['kal_sınıf']
        prj_prog = request.form['prj_prog']


        malz_prj = db.session.query(Malzeme).filter(and_(Malzeme.malz_name ==malzeme_name, Malzeme.malz_standrt == malzemestan)).first()

        if malz_prj == None:
            flash("Malzeme ve Standardı Kontrol ediniz!")
            return redirect(url_for('proje_edit', prj_id=prj_id))


        proje_to_edit.prj_no=prj_no
        proje_to_edit.urn_adi = urn_adi
        proje_to_edit.teklif_sure = sure
        proje_to_edit.yay_tarh = yay_tarih_filtre
        proje_to_edit.malz_id=malz_prj.id
        proje_to_edit.cap=isl_cap
        proje_to_edit.boy=parc_boy
        proje_to_edit.kal_class=kal_sınıf
        proje_to_edit.malz_sah=malzemesa
        proje_to_edit.prog = prj_prog

        if proje_to_edit.prj_no:
            proje_to_edit.stat = "Kapalı"
        else:
            proje_to_edit.stat = "Açık"

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Hata durumunda değişiklikleri geri al
            print(f"Hata: {str(e)}")  # Hata mesajını yazdır


        return redirect(url_for('proje'))


    return render_template("proje-edit.html", logged_in=current_user.is_authenticated, user=current_user, proje=proje_to_edit, malz=malz, malz_stan=malz_stan)

@app.route("/proje-rev-gunc/<int:prj_id>", methods=["GET","POST"])
def proje_rev_atlat(prj_id):
    proje_rev = Projerevtakip.query.filter(Projerevtakip.prj_id == prj_id).order_by(Projerevtakip.prj_rev_no.desc()).first()
    prj_rev=proje_rev.prj_rev_no + 1
    new_line=Projerevtakip(
        prj_id=prj_id,
        prj_rev_no=str(int(proje_rev.prj_rev_no) + 1),
        rev_tarh=date.today()
    )
    db.session.add(new_line)
    proje_to_edit = db.get_or_404(Proje, prj_id)
    proje_to_edit.proj_rev_no=prj_rev
    proje_to_edit.rev_tarh = date.today()
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    return redirect(url_for('proje_edit', prj_id=prj_id))


@app.route("/opr-ekran/<int:prj_id>", methods=["GET","POST"])
def opr_ekran(prj_id):
    proje_to_edit = db.get_or_404(Proje, prj_id)
    query=db.session.query(Operasyon)
    query2 = db.session.query(Mastar)
    chz_type = [c[0] for c in db.session.query(Mastar.mastar_type).distinct().all()]
    opr_added=db.session.query(Projeopr).filter(Projeopr.prj_id==prj_id)
    chz_added=db.session.query(Projecihaz).filter(Projecihaz.prj_id==prj_id)

    opr_filtre = request.args.get('opr_name', '')
    opr_type_filtre = request.args.get('opr_type', '')
    mstr_filtre = request.args.get('mstr_name', '')
    mstr_type_filtre = request.args.get('mstr_type', '')

    if mstr_filtre:
        query2 = query2.filter(Mastar.mastar_name.ilike(f"%{mstr_filtre}%"))

    if mstr_type_filtre != '':
        query2 = query2.filter(Mastar.mastar_type == mstr_type_filtre)
    if opr_filtre:
        query = query.filter(Operasyon.opr_name.ilike(f"%{opr_filtre}%"))

    if opr_type_filtre != '':
        query = query.filter(Operasyon.opr_tip == opr_type_filtre)



    return render_template("is-akısı.html", logged_in=current_user.is_authenticated, user=current_user,proje=proje_to_edit, opr=query, opr_added=opr_added, prj_id=prj_id, cihaz=chz_type, mastar=query2, mastar_added=chz_added)

@app.route("/opr-ekle/<int:prj_id>/<int:opr_id>", methods=["GET","POST"])
def opr_ekle(prj_id,opr_id):
    prj_opr=db.session.query(Projeopr).filter(Projeopr.prj_id == prj_id).order_by(Projeopr.opr_sira_no.desc()).first()

    if prj_opr:
        new_opr=Projeopr(
            prj_id=prj_id,
            opr_id=opr_id,
            opr_sira_no=prj_opr.opr_sira_no + 1
        )
    else:
        new_opr = Projeopr(
            prj_id=prj_id,
            opr_id=opr_id,
            opr_sira_no = 1
        )
    db.session.add(new_opr)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    return redirect(url_for('opr_ekran', prj_id=prj_id))

@app.route("/opr-çikar/<int:prj_id>", methods=["GET","POST"])
def opr_cikar(prj_id):
    prj_opr=db.session.query(Projeopr).filter(Projeopr.prj_id == prj_id).order_by(desc(Projeopr.opr_sira_no)).first()

    db.session.delete(prj_opr)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    return redirect(url_for('opr_ekran', prj_id=prj_id))

@app.route("/opr-desc-ekle/<int:prj_id>", methods=["GET","POST"])
def opr_desc_ekle(prj_id):
    opr_desc = db.session.query(Projeopr).filter(Projeopr.prj_id == prj_id).order_by(Projeopr.opr_sira_no)
    prjler = db.session.query(Projeopr).filter(Projeopr.prj_id == prj_id).all()
    opr_idler=[]

    opr_out_list=[]
    for prj in opr_desc:
        if prj.oprsyn.opr_tip == 'Dış Operasyon':
            opr_out_list.append(prj.opr_sira_no)

    opr_desc_data = []
    descritions = request.form.getlist('oprations[][desc]')
    for i in range(len(descritions)):
        prj_opr = db.session.query(Projeopr).filter(and_(Projeopr.prj_id == prj_id, Projeopr.opr_sira_no == i+1)).one()
        opr_desc_data.append({
            'sira_no':i + 1,
            'desc':descritions[i],
            'opr_id':prj_opr.opr_id

        })
        opr_idler.append(prj_opr.opr_id)
    sayaç = Counter(opr_idler)
    tekrar_edenler = [el for el, adet in sayaç.items() if adet > 1]

    for el in opr_desc_data:
        if el['opr_id'] in tekrar_edenler:
            if not el['desc'] or el['desc'].strip() == '' :
                flash("Aynı operasyondan 2 adet eklendi. Açıklama giriniz!")
                return redirect(url_for('opr_ekran', prj_id=prj_id))
        if el['sira_no'] in opr_out_list:
            print('ok')
            if not el['desc'] or el['desc'].strip() == '' :
                print(f"açıkalama: {el['desc']}")
                flash("Dış Operasyon açıklaması Boş Bırakılamaz!")
                return redirect(url_for('opr_ekran', prj_id=prj_id))

        prj_opr = db.session.query(Projeopr).filter(and_(Projeopr.prj_id == prj_id, Projeopr.opr_sira_no == el['sira_no'])).one()
        prj_opr.opr_desc =el['desc']
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Hata durumunda değişiklikleri geri al
            print(f"Hata: {str(e)}")  # Hata mesajını yazdır


    return redirect(url_for('proje'))

@app.route("/mstr-ekle/<int:prj_id>/<int:mstr_id>", methods=["GET","POST"])
def mstr_ekle(prj_id,mstr_id):
    chz_added = db.session.query(Projecihaz).filter(Projecihaz.prj_id == prj_id)
    mastar_id = []
    for m in chz_added:
        mastar_id.append(m.cihaz_id)
    if mstr_id in mastar_id:
        flash("Aynı cihazdan 2 adet eklenemez!")
        return redirect(url_for('opr_ekran', prj_id=prj_id))

    new_prj_chz=Projecihaz(
        prj_id=prj_id,
        cihaz_id=mstr_id
    )

    db.session.add(new_prj_chz)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    return redirect(url_for('opr_ekran', prj_id=prj_id))

@app.route("/mstr-çikar/<int:prj_id>/<int:mstr_id>", methods=["GET","POST"])
def mstr_cikar(prj_id,mstr_id):
    prj_chz=db.session.query(Projecihaz).filter(and_(Projecihaz.prj_id == prj_id,Projecihaz.cihaz_id == mstr_id)).one()

    db.session.delete(prj_chz)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    return redirect(url_for('opr_ekran', prj_id=prj_id))

@app.route("/planlama", methods=["GET","POST"])
def planlama():
    cnc = db.session.query(Cnc).all()
    plan_filtre = request.args.get('plan_stat','')
    if plan_filtre == '2' or plan_filtre == '' or plan_filtre == None :
        satirlar_tuple = db.session.query(Satir.proje_id).distinct().filter(or_(Satir.satr_stat == "İşleme Alındı", Satir.satr_stat == "Üretim Planına Alındı")).all()
        projeler = [p[0] for p in satirlar_tuple] #proje idleri
    if plan_filtre == '1':
        satirlar_tuple = db.session.query(Satir.proje_id).distinct().filter(Satir.satr_stat == "Üretim Planına Alındı").all()
        projeler = [p[0] for p in satirlar_tuple]  # proje idleri
    if plan_filtre == '0':
        satirlar_tuple = db.session.query(Satir.proje_id).distinct().filter(Satir.satr_stat == "İşleme Alındı").all()
        projeler = [p[0] for p in satirlar_tuple] #proje idleri
    satirlar = []

    siparis_adetleri =   db.session.query(Satir.proje_id,func.sum(Satir.ad).label("toplam_adet")).group_by(Satir.proje_id).all()
    satir_adetleri = dict(siparis_adetleri)  # projeid: toplam sipariş adedi şeklinde dict
    plan_adet = db.session.query(Plan.proje_id,func.sum(Plan.ad).label("toplam_adet")).group_by(Plan.proje_id).all()
    plan_adetleri = dict(plan_adet)
    satir_firma = []
    satir_sip = []
    satir_urnno = []
    satir_tkrno = []
    ort_satirlar = []
    filtreler = []

    firm_filtre = request.args.get('firma', '')
    sipno_filtre = request.args.get('sipariş_no', '')
    urnno_filtre = request.args.get('parca_no', '')
    rsmno_filtre = request.args.get('resim_no', '')
    if firm_filtre:
        filtreler.append(firm_filtre)
    if sipno_filtre:
        filtreler.append(sipno_filtre)
    if urnno_filtre:
        filtreler.append(urnno_filtre)
    if rsmno_filtre:
        filtreler.append(rsmno_filtre)



    plan_prjler = {}
    for s in projeler:
        planlar =db.session.query(Plan).filter(and_(Plan.proje_id == s, Plan.plan_stat == 0)).all()
        plan_prjler[s]=planlar

    result = db.session.query(Plan).filter(Plan.plan_stat == 0).all()

    for item in result:
        if item.proje_id in projeler:
            pass
        else:
            db.session.delete(item)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()  # Hata durumunda değişiklikleri geri al
                print(f"Hata: {str(e)}")  # Hata mesajını yazdır





    for s in projeler:
        new_str = db.session.query(Satir)
        if len(filtreler)>0:

            if firm_filtre:
                new_str = new_str.filter(and_(Satir.proje_id == s,Satir.sip.has(Siparis.firma.has(Firmalar.name.ilike(f"%{firm_filtre}%")))))

            if urnno_filtre:
                new_str = new_str.filter(and_(Satir.proje_id == s,Satir.urn.has(Proje.urn_no.ilike(f"%{urnno_filtre}%"))))

            if sipno_filtre:
                new_str = new_str.filter(and_(Satir.proje_id == s,Satir.sip.has(Siparis.sip_no.ilike(f"%{sipno_filtre}%"))))

            if rsmno_filtre:
                new_str = new_str.filter(and_(Satir.proje_id == s,Satir.urn.has(Proje.tkr_no.ilike(f"%{rsmno_filtre}%"))))
                s
            new_str = new_str.first()
            if new_str:
                ort_satirlar.append(new_str)

            else:
                pass
        else:

            new_str = new_str.filter(Satir.proje_id == s).first()
            ort_satirlar.append(new_str)
            




    return render_template("planlama.html", logged_in=current_user.is_authenticated, user=current_user, cnc=cnc, satirlar=ort_satirlar, adetler=satir_adetleri, plan_adet=plan_adetleri, plan_prjler=plan_prjler)



@app.route("/plan-ekle/<int:prj_id>", methods=["GET","POST"])
def plan_ekle(prj_id):
    proje_to_add = db.get_or_404(Proje, prj_id)
    if proje_to_add.teklif_sure == 0 or proje_to_add.teklif_sure == None or proje_to_add.boy == 0 or proje_to_add.boy == None :
        flash("Projede eksik bilgiler var! Kontrol ediniz.")
        return redirect(url_for('planlama'))

    cnc = db.session.query(Cnc).all()
    satirlar = db.session.query(Satir).filter(and_(Satir.proje_id == prj_id, or_(Satir.satr_stat == 'İşleme Alındı', Satir.satr_stat == 'Üretim Planına Alındı'))).order_by(Satir.ter_tarh).all()
    top_adet = db.session.query(func.sum(Satir.ad)).filter(and_(Satir.proje_id == prj_id,or_(Satir.satr_stat == 'İşleme Alındı', Satir.satr_stat == 'Üretim Planına Alındı'))).scalar()
    top_plan_ad = db.session.query(func.sum(Plan.ad)).filter(and_(Plan.proje_id == prj_id, or_(Plan.plan_stat == 0,Plan.plan_stat == 1))).scalar()
    plan_str_ad = {}
    planstr = db.session.query(func.sum(Planstr.plan_ad))
    for str in satirlar:
        p_ad = planstr.filter(Planstr.str_id == str.id).scalar()
        plan_str_ad[str.id] = p_ad

    return render_template("plan-ekle.html", logged_in=current_user.is_authenticated, user=current_user, proje=proje_to_add, satirlar=satirlar, cnc=cnc, top_adet=top_adet, top_plan_ad=top_plan_ad, plan_str_ad=plan_str_ad)


@app.route("/cnc-ekle/<int:prj_id>", methods=["GET","POST"])
def cnc_ekle(prj_id):
    satirlar = db.session.query(Satir).filter(and_(Satir.proje_id == prj_id,Satir.satr_stat == 'İşleme Alındı')).order_by(Satir.ter_tarh).all()
    prj = db.get_or_404(Proje, prj_id)
    cnc_id = request.args.get('cnc_no','')
    top_adet = db.session.query(func.sum(Satir.ad)).filter(and_(Satir.proje_id == prj_id,or_(Satir.satr_stat == 'İşleme Alındı',Satir.satr_stat == 'Üretim Planına Alındı'))).scalar()
    top_plan_ad = db.session.query(func.sum(Plan.ad)).filter(and_(Plan.proje_id == prj_id, or_(Plan.plan_stat == 0,Plan.plan_stat == 1))).scalar()
    plan_str_ad = {}
    planstr = db.session.query(func.sum(Planstr.plan_ad))
    for str in satirlar:
        p_ad = planstr.filter(Planstr.str_id == str.id).scalar()
        plan_str_ad[f'{str.id}'] = p_ad

    try:
        ad = int(request.args.get('plan_ad',''))
    except ValueError:
        flash("Plana alınacak adet 0 olamaz!")
        return redirect(url_for('plan_ekle', prj_id=prj_id))
    if ad == 0 :
        flash("Plana alınacak adet 0 olamaz!")
        return redirect(url_for('plan_ekle', prj_id=prj_id))
    if cnc_id == '0' or cnc_id == '':
        flash("Cnc no boş bırakılamaz!")
        return redirect(url_for('plan_ekle', prj_id=prj_id))
    if (top_plan_ad or 0) + ad > top_adet:
        flash("Sipariş adedinden fazla adet plana alınamaz!")
        return redirect(url_for('plan_ekle', prj_id=prj_id))
    malz_ad = int(ceil(ad/(2700/(prj.boy+3))))
    toplam_sure = int(ceil(((prj.teklif_sure * ad) + (8 * 3600)) / (3600 * 24)))
    new_plan = Plan(
        proje_id=prj_id,
        cnc_id=cnc_id,
        ad=ad,
        malz_ad=malz_ad,
        toplam_sure=toplam_sure
    )
    db.session.add(new_plan)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    kalan_ad = ad
    for s in satirlar:
        if kalan_ad >= s.ad:
            if (plan_str_ad[f'{s.id}'] or 0) > 0:
                kalan_ad = kalan_ad - s.ad + (plan_str_ad[f'{s.id}'] or 0)
                s.satr_stat = "Üretim Planına Alındı"

                new_planstr = Planstr(
                    plan_id=new_plan.id,
                    str_id=s.id,
                    plan_ad=s.ad - (plan_str_ad[f'{s.id}'] or 0)
                )
                db.session.add(new_planstr)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()  # Hata durumunda değişiklikleri geri al
                    print(f"Hata: {str(e)}")  # Hata mesajını yazdır
            else:

                kalan_ad = kalan_ad - s.ad
                s.satr_stat = "Üretim Planına Alındı"

                new_planstr = Planstr(
                    plan_id=new_plan.id,
                    str_id=s.id,
                    plan_ad=s.ad
                )
                db.session.add(new_planstr)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()  # Hata durumunda değişiklikleri geri al
                    print(f"Hata: {str(e)}")  # Hata mesajını yazdır
        else:
            if kalan_ad >= (s.ad - (plan_str_ad[f'{s.id}'] or 0)):
                kalan_ad = kalan_ad - s.ad + (plan_str_ad[f'{s.id}'] or 0)
                s.satr_stat = "Üretim Planına Alındı"

                new_planstr = Planstr(
                    plan_id=new_plan.id,
                    str_id=s.id,
                    plan_ad=s.ad - (plan_str_ad[f'{s.id}'] or 0)
                )
                db.session.add(new_planstr)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()  # Hata durumunda değişiklikleri geri al
                    print(f"Hata: {str(e)}")  # Hata mesajını yazdır
            else:
                if kalan_ad == 0:
                    break
                elif (plan_str_ad[f'{s.id}'] or 0) > 0:

                    new_planstr = Planstr(
                        plan_id=new_plan.id,
                        str_id=s.id,
                        plan_ad=kalan_ad
                    )
                    db.session.add(new_planstr)
                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()  # Hata durumunda değişiklikleri geri al
                        print(f"Hata: {str(e)}")  # Hata mesajını yazdır
                    break
                else:

                    new_planstr = Planstr(
                        plan_id=new_plan.id,
                        str_id=s.id,
                        plan_ad=kalan_ad
                    )
                    db.session.add(new_planstr)
                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()  # Hata durumunda değişiklikleri geri al
                        print(f"Hata: {str(e)}")  # Hata mesajını yazdır
                    break
    ter = db.session.query(Planstr).filter(Planstr.plan_id == new_plan.id).all()
    ter_tarih = []
    for i in ter:
        ter_tarih.append(i.str.ter_tarh)
    print(sorted(ter_tarih))
    new_plan.ter_tarh = sorted(ter_tarih)[0]
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    return redirect(url_for('planlama'))


@app.route("/plan-sil/<int:plan_id>", methods=["GET","POST"])
def plan_sil(plan_id):
    plan_to_delete = db.get_or_404(Plan, plan_id)
    planstr_to_delete = db.session.query(Planstr).filter(Planstr.plan_id == plan_id).all()
    for satir in planstr_to_delete:
        s = db.get_or_404(Satir, satir.str_id)
        s.satr_stat = "İşleme Alındı"
        db.session.delete(satir)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Hata durumunda değişiklikleri geri al
            print(f"Hata: {str(e)}")  # Hata mesajını yazdır
    db.session.delete(plan_to_delete)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır



    return redirect(url_for('planlama'))


@app.route("/plan-edit/<int:plan_id>", methods=["GET","POST"])
def plan_edit(plan_id):
    plan = db.get_or_404(Plan, plan_id)
    prj_id = plan.proje_id
    proje_to_add = db.get_or_404(Proje, prj_id)
    cnc = db.session.query(Cnc).all()
    satirlar = db.session.query(Satir).filter(and_(Satir.proje_id == prj_id, or_(Satir.satr_stat == 'İşleme Alındı',Satir.satr_stat == 'Üretim Planına Alındı'))).all()
    top_adet = db.session.query(func.sum(Satir.ad)).filter(and_(Satir.proje_id == prj_id, or_(Satir.satr_stat == 'İşleme Alındı',Satir.satr_stat == 'Üretim Planına Alındı'))).scalar()
    top_plan_ad = plan.ad

    return render_template("plan-edit.html", logged_in=current_user.is_authenticated, user=current_user, plan=plan, proje=proje_to_add, satirlar=satirlar, cnc=cnc, top_adet=top_adet, top_plan_ad=top_plan_ad)

@app.route("/cnc-plan-edit/<int:plan_id>/<int:prj_id>", methods=["GET","POST"])
def cnc_plan_edit(plan_id,prj_id):
    plan_to_delete = db.get_or_404(Plan, plan_id)
    planstr_to_delete = db.session.query(Planstr).filter(Planstr.plan_id == plan_id).all()
    cnc_id = request.args.get('cnc_edit_no', '')
    try:
        ad = int(request.args.get('plan_edit_ad', ''))
    except ValueError:
        flash("Plana alınacak adet 0 olamaz!")
        return redirect(url_for('plan_edit', plan_id=plan_id))
    if ad == 0:
        flash("Plana alınacak adet 0 olamaz!")
        return redirect(url_for('plan_edit', plan_id=plan_id))
    if cnc_id == '0' or cnc_id == '':
        flash("Cnc no boş bırakılamaz!")
        return redirect(url_for('plan_edit', plan_id=plan_id))

    for satir in planstr_to_delete:
        s = db.get_or_404(Satir, satir.str_id)
        s.plan_ad = 0
        s.satr_stat = "İşleme Alındı"
        db.session.delete(satir)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Hata durumunda değişiklikleri geri al
            print(f"Hata: {str(e)}")  # Hata mesajını yazdır
    db.session.delete(plan_to_delete)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    satirlar = db.session.query(Satir).filter(
        and_(Satir.proje_id == prj_id, Satir.satr_stat == 'İşleme Alındı')).order_by(Satir.ter_tarh).all()
    prj = db.get_or_404(Proje, prj_id)

    malz_ad = int(ceil(ad / (2700 / (prj.boy + 3))))
    toplam_sure = int(ceil(((prj.teklif_sure * ad) + (8 * 3600)) / (3600 * 24)))
    new_plan = Plan(
        proje_id=prj_id,
        cnc_id=cnc_id,
        ad=ad,
        malz_ad=malz_ad,
        toplam_sure=toplam_sure
    )
    db.session.add(new_plan)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    kalan_ad = ad
    for s in satirlar:
        if kalan_ad >= s.ad:
            if s.plan_ad > 0:
                kalan_ad = kalan_ad - s.ad + s.plan_ad
                s.satr_stat = "Üretim Planına Alındı"
                s.plan_ad = s.ad
                new_planstr = Planstr(
                    plan_id=new_plan.id,
                    str_id=s.id
                )
                db.session.add(new_planstr)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()  # Hata durumunda değişiklikleri geri al
                    print(f"Hata: {str(e)}")  # Hata mesajını yazdır
            else:

                kalan_ad = kalan_ad - s.ad
                s.satr_stat = "Üretim Planına Alındı"
                s.plan_ad = s.ad
                new_planstr = Planstr(
                    plan_id=new_plan.id,
                    str_id=s.id
                )
                db.session.add(new_planstr)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()  # Hata durumunda değişiklikleri geri al
                    print(f"Hata: {str(e)}")  # Hata mesajını yazdır
        else:
            if kalan_ad > (s.ad - s.plan_ad):
                kalan_ad = kalan_ad - s.ad + s.plan_ad
                s.satr_stat = "Üretim Planına Alındı"
                s.plan_ad = s.ad
                new_planstr = Planstr(
                    plan_id=new_plan.id,
                    str_id=s.id
                )
                db.session.add(new_planstr)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()  # Hata durumunda değişiklikleri geri al
                    print(f"Hata: {str(e)}")  # Hata mesajını yazdır
            else:
                if s.plan_ad > 0:
                    s.plan_ad += kalan_ad
                    new_planstr = Planstr(
                        plan_id=new_plan.id,
                        str_id=s.id
                    )
                    db.session.add(new_planstr)
                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()  # Hata durumunda değişiklikleri geri al
                        print(f"Hata: {str(e)}")  # Hata mesajını yazdır
                    break
                else:
                    s.plan_ad = kalan_ad
                    new_planstr = Planstr(
                        plan_id=new_plan.id,
                        str_id=s.id
                    )
                    db.session.add(new_planstr)
                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()  # Hata durumunda değişiklikleri geri al
                        print(f"Hata: {str(e)}")  # Hata mesajını yazdır
                    break

    return redirect(url_for('planlama'))






@app.route("/cnc-plan/<int:cnc_id>", methods=["GET","POST"])
def cnc_plan(cnc_id):
    planlar = db.session.query(Plan).filter(and_(Plan.cnc_id == cnc_id, Plan.plan_stat == 0)).order_by(Plan.plan_sira_no).all()

    cnc = db.get_or_404(Cnc, cnc_id)
    malz_stok = db.session.query(Malzstok).all()
    plan_mastar = {}
    plan_malzleri = {}

    for p in planlar:
        mastar = db.session.query(Projecihaz).filter(Projecihaz.prj_id == p.proje_id).all()
        mstr = []
        for m in mastar:
            stat = db.session.query(Cihaz.uygunluk_stat).filter(Cihaz.cihaz_name == m.cihaz.mastar_name).scalar()
            if stat:
                mstr.append(stat)
            else:
                mstr.append('0')
        plan_mastar[p.id] = mstr
    print(plan_mastar)

    for p in planlar:
        malzeme_name = p.proje.malz.malz_name
        cap = p.proje.cap
        malz_s = db.session.query(Malzstok).filter(and_(Malzstok.malz_name == malzeme_name,Malzstok.ad > 0,Malzstok.cap >= cap)).order_by(Malzstok.gir_tarh).all()
        malz = []
        malz_r_adet = []
        for m in malz_s:
            malz_ad = db.session.query(func.sum(Malztransc.ad)).filter(and_(Malztransc.transc_type == 'Rezerve',Malztransc.malz_id == m.id)).scalar()
            malz_r_ad = m.ad-(malz_ad or 0)

            if malz_r_ad > 0:
                malz.append((m,malz_r_ad))

        malz_r = db.session.query(Malztransc).filter(and_(Malztransc.transc_type == 'Rezerve', Malztransc.plan_id == p.id)).first()

        plan_malzleri[p.id] = (malz,malz_r,malz_r_adet)

        print(plan_malzleri)



    plan_terminleri = {}
    for p in planlar:
        plan_str = db.session.query(Planstr).join(Satir, Planstr.str_id == Satir.id).filter(Planstr.plan_id == p.id).order_by(Satir.ter_tarh).first()
        plan_terminleri[p.id] = plan_str.str.ter_tarh
    print(plan_terminleri)
    if request.method == 'POST':
        plan_sira_nolar = []
        for p in planlar:
            sira_no = request.form[f'sira_no_{p.id}']
            if sira_no == '' or sira_no == None:
                flash("Plan Sıra No Boş Bırakılamaz!")
                return redirect(url_for('cnc_plan', cnc_id=cnc_id))
            plan_sira_nolar.append(sira_no)
            if len(plan_sira_nolar) != len(set(plan_sira_nolar)):
                flash("Birden fazla satıra aynı sıra no girilemez!")
                return redirect(url_for('cnc_plan', cnc_id=cnc_id))
            p.plan_sira_no = sira_no
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()  # Hata durumunda değişiklikleri geri al
                print(f"Hata: {str(e)}")  # Hata mesajını yazdır
        planlar = db.session.query(Plan).filter(and_(Plan.cnc_id == cnc_id, Plan.plan_stat == 0)).order_by(Plan.plan_sira_no).all()



    return render_template("cnc-plan.html", logged_in=current_user.is_authenticated, user=current_user, plan=planlar, cnc=cnc, termin=plan_terminleri, malz=plan_malzleri, malz_stok=malz_stok, mastar=plan_mastar)

@app.route("/malz-rez", methods=["GET","POST"])
def malz_rezerve():
    cnc_id = request.args.get("cnc_id")
    plan_id = request.args.get("plan_id")
    malz_id = request.args.get("malz_id")

    if malz_id == '0' or malz_id == '':
        flash("Malzeme Seçiniz!")
        return redirect(url_for('cnc_plan', cnc_id=cnc_id))
    malz_ad = db.session.query(func.sum(Malztransc.ad)).filter(and_(Malztransc.transc_type == 'Rezerve', Malztransc.malz_id == malz_id)).scalar()
    plan = db.get_or_404(Plan, plan_id)
    malzeme = db.get_or_404(Malzstok, malz_id)

    print(malz_ad)
    rez_ad = malzeme.ad - (malz_ad or 0)
    print(rez_ad)
    if plan.malz_ad >= rez_ad:
        ad = rez_ad
    else:
        ad = plan.malz_ad
    malz_tr = Malztransc(
        transc_type='Rezerve',
        ad=ad,
        malz_id=int(malz_id),
        tarh=date.today(),
        plan_id=plan_id,
        lot_id='250012'
    )

    db.session.add(malz_tr)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır
    malz_name = db.get_or_404(Malzstok, malz_id)
    plan.malz_id = malz_tr.id
    plan.malz_name = malz_name.malz_name
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır


    return redirect(url_for('cnc_plan', cnc_id=cnc_id))

@app.route("/malz-stok", methods=["GET","POST"])
def malz_stok():
    malz_talep = db.session.query(Malzeme).all()
    tedarik = db.session.query(Tedarikci).all()
    mal_no_line = db.session.query(Malzstok).order_by(Malzstok.gir_tarh.desc()).first()
    mal_no = mal_no_line.malz_no
    mal_yil = mal_no.split('/')[1]
    yil = datetime.now().year
    if int(mal_yil) == yil:

        mal_sira_no = int(mal_no.split('/')[0]) + 1
    else:
        mal_sira_no = 1

    malz_adi_filtre = request.args.get('malz_adi', '')
    malz_no_filtre = request.args.get('malz_no', '')
    irs_no_filtre = request.args.get('irs_no', '')
    ted_adi_filtre = request.args.get('ted_adi', '')
    cap_filtre = request.args.get('cap', '')
    malz_cins_filtre = request.args.get('malz_cins', '')


    query = db.session.query(Malzstok)

    if malz_adi_filtre:
        query = query.filter(Malzstok.malz_name.ilike(f"%{malz_adi_filtre}%"))
    if malz_no_filtre:
        query = query.filter(Malzstok.malz_no.ilike(f"%{malz_no_filtre}%"))
    if irs_no_filtre:
        query = query.filter(Malzstok.irs_no.ilike(f"%{irs_no_filtre}%"))
    if ted_adi_filtre:
        query = query.filter(Malzstok.ted.has(Tedarikci.tedarik_name.ilike(f"%{ted_adi_filtre}%")))
    if malz_cins_filtre != '':
        query = query.filter(Malzstok.malz_cins == malz_cins_filtre)
    if cap_filtre != '':
        query = query.filter(Malzstok.cap == cap_filtre)



    page = request.args.get("page", 1, type=int)
    per_page = 50
    toplam_kayit = query.count()
    malzler = query.offset((page - 1) * per_page).limit(per_page).all()
    total_pages = ceil(toplam_kayit / per_page)

    page_to_render = []
    if page > 1:
        if page == total_pages:
            for p in range(1, page - 1):
                if p == 1:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    page_to_render.append(page - 1)
                    page_to_render.append(page)
                    break
        else:
            for p in range(1, page - 1):

                if p == 1:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    break

            for p in range(page - 1, page + 2):
                page_to_render.append(p)

            for p in range(page + 2, total_pages + 1):
                if p == total_pages:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    page_to_render.append(total_pages)
                    break
    else:
        for p in range(1, total_pages + 1):
            if p == 1 or p <= 3:
                page_to_render.append(p)
            else:
                page_to_render.append('p')
                page_to_render.append(total_pages)
                break

    return render_template("malz-stok.html", logged_in=current_user.is_authenticated, user=current_user, malz=malzler,malz_talep=malz_talep, yil=yil, mal_sira_no=mal_sira_no, tedarik=tedarik, page=page, total_pages=total_pages, toplam_kayit=toplam_kayit, page_to_render=page_to_render)


@app.route("/malz-sil/<int:malz_id>", methods=["GET","POST"])
def malz_sil(malz_id):
    malz_to_delete = db.get_or_404(Malzstok, malz_id)
    malz_trans = db.session.query(Malztransc).filter(Malztransc.malz_id == malz_id).first()
    if malz_trans:
        flash("Silmek istediğiniz malzeme no için malzeme hareketi mevcut. Silinemez!")
        return redirect(url_for('malz_stok'))
    else:
        db.session.delete(malz_to_delete)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Hata durumunda değişiklikleri geri al
            print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    return redirect(url_for('malz_stok'))

@app.route("/malz-ekle", methods=["GET","POST"])
def malz_ekle():

    if request.method == 'POST':
        malz_no = request.form['malz_ekle_no']
        malz_adi = request.form['malz_ekle_name']
        malz_stan = request.form['malz_ekle_stan']
        malz_cinsi = request.form['malz_ekle_cins']
        irs_no = request.form['malz_ekle_irs']
        raf = request.form['malz_ekle_raf']
        tedarik = request.form['malz_ekle_ted']
        gir_tarh = request.form['gir_tarih']
        if gir_tarh:
            try:
                gir_tarh = datetime.strptime(gir_tarh, '%Y-%m-%d')
            except ValueError:
                gir_tarh = None
        else:
            gir_tarh = None

        agirlik = request.form['malz_ekle_agrlk']
        cap = request.form['malz_ekle_cap']
        boy = request.form['malz_ekle_boy']
        ad = request.form['malz_ekle_ad']
        talep_no = request.form['malz_ekle_talep']
        talep_id_satir =db.session.query(Siparistalep).filter(Siparistalep.talep_no == talep_no).first()
        if talep_id_satir:
            talep_id=talep_id_satir.id
        else:
            flash("Geçerli Talep No Giriniz!")
            return redirect(url_for('malz_stok'))


        malz_shp = request.form['malz_ekle_sahp']

        new_malz = Malzstok(
            malz_no=malz_no,
            malz_name=malz_adi,
            malz_stndrt=malz_stan,
            raf_no=raf,
            irs_no=irs_no,
            ted_id=tedarik,
            gir_tarh=gir_tarh,
            malz_cins=malz_cinsi,
            agirlik=agirlik,
            cap=cap,
            boy=boy,
            ad=ad,
            siparistalep_id=talep_id,
            malz_sahp=malz_shp

        )
        db.session.add(new_malz)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Hata durumunda değişiklikleri geri al
            print(f"Hata: {str(e)}")  # Hata mesajını yazdır



    return redirect(url_for('malz_stok'))

@app.route("/malz-transc", methods=["GET","POST"])
def malz_hareket():
    malz_adi_filtre = request.args.get('malz_adi_tr', '')
    malz_no_filtre = request.args.get('malz_no_tr', '')
    lot_no_filtre = request.args.get('lot_no', '')
    malz_har_filtre = request.args.get('malz_trans_type', '')

    query = db.session.query(Malztransc)

    if malz_adi_filtre:
        query = query.filter(Malztransc.malz.has(Malzstok.malz_name.ilike(f"%{malz_adi_filtre}%")))
    if malz_no_filtre:
        query = query.filter(Malztransc.malz.has(Malzstok.malz_no.ilike(f"%{malz_no_filtre}%")))
    if lot_no_filtre:
        query = query.filter(Malztransc.lot.has(Lot.lot_no.ilike(f"%{lot_no_filtre}%")))
    if malz_har_filtre != '':
        query = query.filter(Malztransc.transc_type == malz_har_filtre)




    page = request.args.get("page", 1, type=int)
    per_page = 50
    toplam_kayit = query.count()
    malzler = query.offset((page - 1) * per_page).limit(per_page).all()
    total_pages = ceil(toplam_kayit / per_page)

    page_to_render = []
    if page > 1:
        if page == total_pages:
            for p in range(1, page - 1):
                if p == 1:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    page_to_render.append(page - 1)
                    page_to_render.append(page)
                    break
        else:
            for p in range(1, page - 1):

                if p == 1:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    break

            for p in range(page - 1, page + 2):
                page_to_render.append(p)

            for p in range(page + 2, total_pages + 1):
                if p == total_pages:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    page_to_render.append(total_pages)
                    break
    else:
        for p in range(1, total_pages + 1):
            if p == 1 or p <= 3:
                page_to_render.append(p)
            else:
                page_to_render.append('p')
                page_to_render.append(total_pages)
                break


    return render_template("malz-transc.html", logged_in=current_user.is_authenticated, user=current_user, malz=malzler, page=page, total_pages=total_pages, toplam_kayit=toplam_kayit, page_to_render=page_to_render)


@app.route("/malz-transc-del/<int:trans_id>", methods=["GET","POST"])
def malz_hareket_sil(trans_id):
    transc_to_delete = db.get_or_404(Malztransc, trans_id)
    if transc_to_delete.transc_type == "Çıkış":
        flash("Ham malzeme çıkışı silinemez!")
        return redirect(url_for('malz_hareket'))
    else:
        plan_id = transc_to_delete.plan_id
        plan = db.get_or_404(Plan, plan_id)
        plan.malz_id = None
        plan.malz_name = None

        db.session.delete(transc_to_delete)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Hata durumunda değişiklikleri geri al
            print(f"Hata: {str(e)}")  # Hata mesajını yazdır

        return redirect(url_for('malz_hareket'))


@app.route("/lot-add", methods=["GET","POST"])
def lot_ekle():
    istasyonlar = db.session.query(Cnc).all()

    lot_istasyonu = request.args.get('cncler','')
    query = {}
    plan_mastar = {}
    if lot_istasyonu:
        query = db.session.query(Plan).filter(and_(Plan.cnc_id == lot_istasyonu, Plan.plan_stat == 0, Plan.plan_sira_no > 0)).order_by(Plan.plan_sira_no.asc()).all()

        for p in query:
            mastar = db.session.query(Projecihaz).filter(Projecihaz.prj_id == p.proje_id).all()
            mstr = []
            for m in mastar:
                stat = db.session.query(Cihaz.uygunluk_stat).filter(Cihaz.cihaz_name == m.cihaz.mastar_name).scalar()
                if stat:
                    mstr.append(stat)
                else:
                    mstr.append('0')
            plan_mastar[p.id] = mstr

    return render_template("lot-ekle.html", logged_in=current_user.is_authenticated, user=current_user, ist=istasyonlar, plan=query, mastar=plan_mastar)

@app.route("/work-order/<int:cnc_id>", methods=["GET","POST"])
def is_emri(cnc_id):
    data = db.session.query(Plan).filter(and_(Plan.cnc_id == cnc_id, Plan.plan_stat == 0, Plan.plan_sira_no == 1)).first()
    still_work = db.session.query(Lot).filter(and_(or_(Lot.lot_stat == "Ayar",Lot.lot_stat == "Seri"),Lot.plan.has(Plan.cnc_id == cnc_id))).first()
    if data:
        if still_work:
            flash("İstasyonda Çalışan İş Mevcut")
            return redirect(url_for('lot_ekle'))
        else:
            prj_opr = db.session.query(Projeopr).filter(Projeopr.prj_id == data.proje_id).order_by(Projeopr.opr_sira_no).first()
            if prj_opr:
                siparis = []
                terminler = []
                for sip in data.planstr:
                    sip_no = sip.str.sip.sip_no
                    if sip_no in siparis:
                        pass
                    else:
                        siparis.append(sip_no)
                for satir in data.planstr:
                    tarih = satir.str.ter_tarh
                    terminler.append(tarih)

                termin_tarihi = min(terminler)
                lot_no = db.session.query(Lot).order_by(Lot.id.desc()).first()
                if lot_no:
                    yil = lot_no.lot_no[:2]
                    sira = str(int(lot_no.lot_no[2:6]) + 1)
                    s =""
                    for i in range(0,4-len(sira)):
                        s += "0"


                    guncel_yıl = str(datetime.today().year)[2:4]
                    if yil == guncel_yıl:
                        new_lot = yil + s + sira



                else:
                    guncel_yıl = str(datetime.today().year)[2:4]
                    new_lot = guncel_yıl + "0001"

                lot_to_add = Lot(
                    lot_no=new_lot,
                    proje_id=data.proje_id,
                    opr_id=prj_opr.opr_id,
                    ad=0,
                    plan_id=data.id,
                    malz_id=data.malz.malz.id,
                    lot_stat='Ayar'
                )

                db.session.add(lot_to_add)

                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()  # Hata durumunda değişiklikleri geri al
                    print(f"Hata: {str(e)}")  # Hata mesajını yazdır
                data.plan_stat = 1
                data.malz.transc_type = 'Çıkış'
                data.malz.lot_id = lot_to_add.id
                malz_id = data.malz.malz.id
                malzeme = db.get_or_404(Malzstok, malz_id)
                malzeme.ad = malzeme.ad - data.malz.ad

                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()  # Hata durumunda değişiklikleri geri al
                    print(f"Hata: {str(e)}")  # Hata mesajını yazdır

                mastar = []
                for m in data.proje.cihaz:
                    mstr = db.session.query(Cihaz).filter(
                        and_(Cihaz.uygunluk_stat == 1, Cihaz.cihaz_name == m.cihaz.mastar_name)).order_by(
                        Cihaz.kalib_tarh.desc()).first()
                    mastar.append(mstr)
                planlar = db.session.query(Plan).filter(and_(Plan.cnc_id == cnc_id, Plan.plan_stat == 0)).all()
                for plan in planlar:
                    if plan.plan_sira_no > 0:
                        print(f"eski {plan.plan_sira_no}")
                        plan.plan_sira_no -=1
                        print(f"yeni {plan.plan_sira_no}")
                        try:
                            db.session.commit()
                        except Exception as e:
                            db.session.rollback()  # Hata durumunda değişiklikleri geri al
                            print(f"Hata: {str(e)}")  # Hata mesajını yazdır







            else:
                flash("Proje Operasyon Bilgileri Eksik")
                return redirect(url_for('lot_ekle'))
    else:
        flash("Plan Sırası Girilmeli!")
        return redirect(url_for('lot_ekle'))





    return render_template("is-emri.html", logged_in=current_user.is_authenticated, user=current_user, data=data, siparis=siparis,termin=termin_tarihi, lot=new_lot, mastar=mastar)

@app.route("/malz-transc-add", methods=["GET","POST"])
def malz_hareket_ekle():
    #lot ekleme yapılıdıktan sonra düzenlenecek
    return render_template("malz-transc-add.html", logged_in=current_user.is_authenticated, user=current_user)

#saatlik üretimlerin girildiği sayfa
@app.route("/uretim-girisi", methods=["GET","POST"])
def uretim_add():

    lotlar = db.session.query(Lot).filter(or_(Lot.lot_stat == "Ayar", Lot.lot_stat == "Seri")).all()
    print(lotlar)


    return render_template("uretim-ekle.html", logged_in=current_user.is_authenticated, user=current_user, lot=lotlar)


#tüm lotların göründüğü sayfa
@app.route("/lot-takip", methods=["GET","POST"])
def lot_ekrani():
    cncler = db.session.query(Cnc).all()
    query = db.session.query(Lot)

    lot_filtre = request.args.get('lot_no', '')
    urnno_filtre = request.args.get('parca_no', '')
    rsmno_filtre = request.args.get('resim_no', '')
    revno_filtre = request.args.get('parca_rev', '')
    btrh = request.args.get('b_tarih', '')
    if btrh:
        try:
            btrh_filtre = datetime.strptime(btrh, '%Y-%m-%d')
        except ValueError:
            btrh_filtre = None
    else:
        btrh_filtre = None
    strh = request.args.get('s_tarih', '')
    if strh:
        try:
            strh_filtre = datetime.strptime(strh, '%Y-%m-%d')
        except ValueError:
            strh_filtre = None
    else:
        strh_filtre = None

    cnc_filtre = request.args.get('cnc_no', '')

    if lot_filtre:
        query = query.filter(Lot.lot_no.ilike(f"%{lot_filtre}%"))
    if urnno_filtre:
        query = query.filter(Lot.proje.has(Proje.urn_no.ilike(f"%{urnno_filtre}%")))
    if rsmno_filtre:
        query = query.filter(Lot.proje.has(Proje.tkr_no.ilike(f"%{rsmno_filtre}%")))
    if revno_filtre:
        query = query.filter(Lot.proje.has(Proje.tkr_rev_no.ilike(f"%{revno_filtre}%")))
    if cnc_filtre != '':
        query = query.filter(Lot.plan.has(Plan.cnc_id == cnc_filtre))
    if btrh_filtre and strh_filtre:
        query = query.filter(Lot.tarih.between(btrh_filtre, strh_filtre))



    page = request.args.get("page", 1, type=int)
    per_page = 50
    toplam_kayit = query.count()
    lotlar = query.offset((page - 1) * per_page).limit(per_page).all()
    total_pages = ceil(toplam_kayit / per_page)

    page_to_render = []
    if page > 1:
        if page == total_pages:
            for p in range(1, page - 1):
                if p == 1:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    page_to_render.append(page - 1)
                    page_to_render.append(page)
                    break
        else:
            for p in range(1, page - 1):

                if p == 1:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    break

            for p in range(page - 1, page + 2):
                page_to_render.append(p)

            for p in range(page + 2, total_pages + 1):
                if p == total_pages:
                    page_to_render.append(p)
                else:
                    page_to_render.append('p')
                    page_to_render.append(total_pages)
                    break
    else:
        for p in range(1, total_pages + 1):
            if p == 1 or p <= 3:
                page_to_render.append(p)
            else:
                page_to_render.append('p')
                page_to_render.append(total_pages)
                break

    return render_template("lot-ekrani.html", logged_in=current_user.is_authenticated, user=current_user, cnc=cncler, lot=lotlar, page=page, total_pages=total_pages, toplam_kayit=toplam_kayit, page_to_render=page_to_render)


#bu güncellenecek
@app.route("/lot-sil", methods=["GET","POST"])
def lot_sil():

    lot = db.session.query(Lot).order_by(Lot.tarih.desc()).first()
    print(lot.lot_no)
    db.session.delete(lot)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    return render_template("uretim-ekle.html", logged_in=current_user.is_authenticated, user=current_user)


#lot bilgisi ekleme. imalat süresi ayar yapan kişi ekleme yapılıyor
@app.route("/lot-info-add/<int:lot_id>", methods=["GET","POST"])
def lot_info_add(lot_id):
    operators = db.session.query(Personel).filter(Personel.division.has(Users.division == "Üretim")).all()
    uygunsuzluk = db.session.query(Uygunsuzluklar).all()
    lot = db.get_or_404(Lot, lot_id)
    if request.method == 'POST':
        iml_sure = request.form['iml_sure']
        ayar_fire = request.form['ayar_fire']
        operator = request.form['operator']
        ur_adet = request.form['ur_ad']
        fire_adet = request.form['fire_ad']
        uygunsuzluk = request.form['uygunsuzluk']
        b_saat = request.form['baslangic_saat']
        b_saat_obj = datetime.strptime(b_saat, "%H:%M").time()
        b_tarih = datetime.combine(datetime.today(), b_saat_obj)
        s_saat = request.form['bitis_saat']
        s_saat_obj = datetime.strptime(s_saat, "%H:%M").time()
        s_tarih = datetime.combine(datetime.today(),s_saat_obj)
        # if lot.lot_stat =="Ayar":
        #     flash("İlk Onay verilmedi. Üretim Bilgileri Girilemez")
        #     return redirect(url_for('lot_info_add', lot_id=lot_id))
        # else:
        lot.sure = iml_sure
        lot.fire_ad = ayar_fire
        lot.operator_id = operator
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Hata durumunda değişiklikleri geri al
            print(f"Hata: {str(e)}")  # Hata mesajını yazdır

        print(b_tarih)







    print(f'{lot_id} ok')
    return render_template("uretim-adet.html", logged_in=current_user.is_authenticated, user=current_user, operator=operators, lot=lot, uyg=uygunsuzluk)

#lot bilgisi yazdırma ekranı
@app.route("/lot-print/<int:lot_id>", methods=["GET","POST"])
def lot_print(lot_id):
    lot = db.get_or_404(Lot, lot_id)

    return render_template("lot-print.html", logged_in=current_user.is_authenticated, user=current_user, lot=lot)


@app.route("/proses-kontrol", methods=["GET","POST"])
def proses_kontrol():
    query = db.session.query(Lot).filter(or_(Lot.lot_stat == 'Ayar', Lot.lot_stat == 'Seri'))
    cncler = db.session.query(Cnc).all()


    lot_filtre = request.args.get('lot_no', '')
    urnno_filtre = request.args.get('parca_no', '')
    rsmno_filtre = request.args.get('resim_no', '')
    revno_filtre = request.args.get('parca_rev', '')
    cnc_filtre = request.args.get('cnc_no', '')

    if lot_filtre:
        query = query.filter(Lot.lot_no.ilike(f"%{lot_filtre}%"))
    if urnno_filtre:
        query = query.filter(Lot.proje.has(Proje.urn_no.ilike(f"%{urnno_filtre}%")))
    if rsmno_filtre:
        query = query.filter(Lot.proje.has(Proje.tkr_no.ilike(f"%{rsmno_filtre}%")))
    if revno_filtre:
        query = query.filter(Lot.proje.has(Proje.tkr_rev_no.ilike(f"%{revno_filtre}%")))
    if cnc_filtre != '':
        query = query.filter(Lot.plan.has(Plan.cnc_id == cnc_filtre))

    toplam_kayit = query.count()
    lot = query.all()


    return render_template("proses-kontrol.html", logged_in=current_user.is_authenticated, user=current_user, lot=lot, cnc=cncler)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
