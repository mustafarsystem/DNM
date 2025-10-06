from datetime import date, datetime
from flask_login import UserMixin
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Date, Boolean, ForeignKey, Float, DateTime
from app.extensions import db
import pytz


utc = pytz.utc
turkey_tz = pytz.timezone('Europe/Istanbul')


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
    kocan_ad: Mapped[int] = mapped_column(Integer, unique=False, nullable=True)
    malz_id: Mapped[int] = mapped_column(Integer, unique=False,nullable=True)
    lot_stat: Mapped[str] = mapped_column(String(100), unique=False, nullable=True)
    tarih: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    desc: Mapped[str] = mapped_column(String(100), unique=False, nullable=True)
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



class Tezgahstatu(db.Model):
    __tablename__ = "statu"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    statu_name: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    statu_baslık: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)

class Uygunsuzluklar(db.Model):
    __tablename__ = "uygunsuzluklar"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uygnslk_name: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)

class Hataraporu(db.Model):
    __tablename__ = "hataraporu"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lot_id: Mapped[int] = mapped_column(Integer, ForeignKey('lot.id'), nullable=False)
    uretim_id: Mapped[int] = mapped_column(Integer, ForeignKey('uretim.id'), nullable=True)
    lot_saat = relationship("Uretim")
    lot = relationship("Lot")
    operasyon_id: Mapped[int] = mapped_column(Integer, ForeignKey('operasyon.id'), nullable=False)
    operasyon = relationship("Operasyon")
    kontrol_type: Mapped[str] = mapped_column(String(1000), unique=False, nullable=False)
    olcu_type: Mapped[str] = mapped_column(String(1000), unique=False, nullable=True)
    olcu_desc: Mapped[str] = mapped_column(String(1000), unique=False, nullable=True)
    olcu_aleti: Mapped[str] = mapped_column(String(500), unique=False, nullable=True)
    kontrol_sıklıgı: Mapped[str] = mapped_column(String(500), unique=False, nullable=True)
    kafile_ad: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)
    kontrol_ad: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)
    uygnslk_id: Mapped[int] = mapped_column(Integer, ForeignKey('uygunsuzluklar.id'), nullable=True)
    uygunsuzluk = relationship("Uygunsuzluklar")
    ad: Mapped[int] = mapped_column(Integer, unique=False, nullable=True)
    descr_uyg: Mapped[str] = mapped_column(String(1000), unique=False, nullable=True)
    personel_id: Mapped[int] = mapped_column(Integer, ForeignKey('personel.id'), nullable=True)
    personel = relationship("Personel")
    baslangic_tarih: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    bitis_tarih: Mapped[datetime] = mapped_column(DateTime, nullable=True)

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
    lot_saat: Mapped[str] = mapped_column(String(10), unique=False, nullable=True)
    ur_ad: Mapped[int] = mapped_column(Integer, unique=False, nullable=True)
    statu_id: Mapped[int] = mapped_column(Integer, ForeignKey('statu.id'), nullable=True)
    statu = relationship("Tezgahstatu")
    sure: Mapped[int] = mapped_column(Integer, unique=False, nullable=True)
    descr_statu: Mapped[str] = mapped_column(String(1000), unique=False, nullable=True)
    personel_id: Mapped[int] = mapped_column(Integer, ForeignKey('personel.id'), nullable=True)
    personel = relationship("Personel")
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
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ad = db.Column(db.String(255))
    yol = db.Column(db.String(255))  # dosya yolu
    tur = db.Column(db.String(50))   # 'pdf', 'xlsx' vs

class Olcu(db.Model):
    __tablename__ = "olculer"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prj_id: Mapped[int] = mapped_column(Integer, ForeignKey('proje.id'), nullable=False)


class Personel(db.Model):
    __tablename__ = "personel"
    id = db.Column(db.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    name: Mapped[str] = mapped_column(String(1000), unique=False, nullable=False)
    division = relationship("Users")
    oprtr = relationship("Lot", back_populates="operator")