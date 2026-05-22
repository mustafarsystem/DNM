from traceback import print_tb

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Proje, Projecihaz, Cihaz, Cnc, Plan, Malzstok, Malztransc, Projeopr, Lot, Uretim, Hataraporu, \
    Tezgahstatu, Personel, Users, Uygunsuzluklar, Planstr, Pdklotsaat, Pdk, Progress, Pdkbol, Lottransc, Operasyon
from math import ceil
from datetime import date, datetime
from sqlalchemy import and_, or_, func, desc
from collections import Counter

progress_bp = Blueprint("progress", __name__)

@progress_bp.route("/progress/<int:pdk_id>", methods=["GET","POST"])
def progress(pdk_id):
    pdk = db.get_or_404(Pdk, pdk_id)
    oprerasyonlar = db.session.query(Projeopr).filter_by(prj_id=pdk.lot.proje_id).all()
    progress = db.session.query(Progress).filter_by(pdk_id=pdk_id).all()
    operation_condition = {}
    alt_pdk = pdk.pdkbol

    operasyon= []
    for o in oprerasyonlar:
        if o.oprsyn.id == 1 or o.oprsyn.id == 5:
            pass
        else:
            operasyon.append(o)
    siparis = []
    for s in pdk.lot.plan.planstr:
        siparis.append(s.str.sip.sip_no)
    print(siparis)
    if alt_pdk:
        return render_template("progress2.html",logged_in=current_user.is_authenticated, user=current_user, pdk=pdk, sip=siparis, opr=operasyon, alt_pdk=alt_pdk)
    else:

        return render_template("progress.html",logged_in=current_user.is_authenticated, user=current_user, pdk=pdk, sip=siparis, opr=operasyon)


@progress_bp.route("/progress-alt-pdk/<int:alt_pdk_id>", methods=["GET","POST"])
def progress_altpdk(alt_pdk_id):
    pdk = db.get_or_404(Pdkbol, alt_pdk_id)
    oprerasyonlar = db.session.query(Projeopr).filter_by(prj_id=pdk.ust_pdk.lot.proje_id).all()
    progress = db.session.query(Progress).filter_by(alt_pdk_id=alt_pdk_id).all()
    lottransc = db.session.query(Lottransc).filter_by(alt_pdk_id=alt_pdk_id).all()
    operation_condition = {}


    operasyon= []
    for o in oprerasyonlar:
        if o.oprsyn.id == 1 or o.oprsyn.id == 5:
            pass
        else:
            operasyon.append(o)
    siparis = []
    for s in pdk.ust_pdk.lot.plan.planstr:
        siparis.append(s.str.sip.sip_no)
    print(siparis)


    return render_template("progress-altpdk.html",logged_in=current_user.is_authenticated, user=current_user, pdk=pdk, sip=siparis, opr=operasyon)


@progress_bp.route("/ic-operasyon/<int:opr_id>", methods=["GET","POST"])
def ic_operasyon(opr_id):
    opr = db.get_or_404(Operasyon, opr_id)

    lot_filtre = request.args.get('lot_no', '')
    urnno_filtre = request.args.get('parca_no', '')
    rsmno_filtre = request.args.get('resim_no', '')
    pdk_no_filtre = request.args.get('pdk_no', '')
    pdk_no = int(pdk_no_filtre[-4:]) if pdk_no_filtre and pdk_no_filtre[-4:].isdigit() else None
    print(pdk_no)
    query = db.session.query(Lottransc).filter(and_(Lottransc.opr_id==opr_id,Lottransc.bit_tarh.is_(None)))
    if lot_filtre:
        query = query.filter(Lottransc.pdk.has(Pdk.lot.has(Lot.lot_no.ilike(f"%{lot_filtre}%"))))
    if urnno_filtre:
        query = query.filter(Lottransc.pdk.has(Pdk.lot.has(Lot.proje.has(Proje.urn_no.ilike(f"%{lot_filtre}%")))))
    if rsmno_filtre:
        query = query.filter(Lottransc.pdk.has(Pdk.lot.has(Lot.proje.has(Proje.tkr_no.ilike(f"%{lot_filtre}%")))))

    if pdk_no:
        query = query.filter(Lottransc.pdk.has(Pdk.id == pdk_no))


    page = request.args.get("page", 1, type=int)
    per_page = 50
    toplam_kayit = query.count()

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    pdk_records = pagination.items

    # opr_satirlari = db.session.query(Lottransc).filter(and_(Lottransc.opr_id==opr_id,Lottransc.bit_tarh.is_(None))).all()

    return render_template("ic-operasyon.html", logged_in=current_user.is_authenticated, user=current_user,opr_list=pdk_records, opr=opr, toplam_kayit=toplam_kayit, pagination=pagination)

@progress_bp.route("/pdk-operasyon/<int:lot_trans_id>/", methods=["GET","POST"])
def pdk_progress(lot_trans_id):
    lot_transc = db.get_or_404(Lottransc, lot_trans_id)

    # pdk_no = f"PDK-{pdk.tarh.year}-{pdk.id:04d}"

    proje_id = lot_transc.pdk.lot.proje_id
    proje_opr = db.session.query(Projeopr).filter_by(prj_id=proje_id, opr_id=lot_transc.opr_id).first()

    opration_history = db.session.query(Progress).filter_by(lot_transc_id=lot_trans_id).order_by(Progress.bas_tarh.desc()).all()
    last_operation = opration_history[-1] if opration_history else None
    work_time = {}
    for o in opration_history:
        if o.bit_tarh:
            time_diff = o.bit_tarh - o.bas_tarh
            work_time[o.id] = round(time_diff.total_seconds() / 3600, 2)  # Çalışma süresini saat cinsinden ve iki ondalık basamağa yuvarla
        else:
            work_time[o.id] = None

    result = db.session.query(
        func.sum(func.coalesce(Progress.saglam_ad, 0)).label("toplam_saglam"),
        func.sum(func.coalesce(Progress.uygnsuz_ad, 0)).label("toplam_uygunsuz")
    ).filter(Progress.lot_transc_id == lot_trans_id).first()
    toplam = (result.toplam_saglam or 0) + (result.toplam_uygunsuz or 0)
    print(toplam)

    if last_operation and last_operation.bit_tarh and toplam >= lot_transc.ad:
        proses_condition = 1   # İşlem tamamlanmış
    elif last_operation and last_operation.bit_tarh is None:
        proses_condition = 2  # İşlem devam ediyor
    elif last_operation and last_operation.bit_tarh and toplam < lot_transc.ad:
        proses_condition = 3    # İşlem duraklatılmış
    elif last_operation is None:
        proses_condition = 4  # İşlem başlamamış

    personel = db.session.query(Personel).all()
    uygunsuzluklar = db.session.query(Uygunsuzluklar).all()
    return render_template("pdk-operasyon.html", logged_in=current_user.is_authenticated, user=current_user, lot_transc=lot_transc, operatorler=personel, proje_opr=proje_opr, opr_hist=opration_history , proses_condition=proses_condition, toplam=toplam, uygunsuzluklar=uygunsuzluklar, work_time=work_time)

@progress_bp.route("/proses-baslat/<int:lot_trans_id>/", methods=["GET","POST"])
def progress_start(lot_trans_id):

    oprtr_id = request.form.get("operator")

    if oprtr_id == "" or oprtr_id is None:
        flash("Lütfen bir operatör seçiniz.", "error")
        return redirect(url_for('progress.pdk_progress', lot_trans_id=lot_trans_id))

    lot_transction = db.get_or_404(Lottransc, lot_trans_id)

    new_progress = Progress(
        pdk_id = lot_transction.pdk_id,
        lot_transc_id = lot_trans_id,
        alt_pdk_id = lot_transction.alt_pdk_id,
        opr_id = lot_transction.opr_id,
        pers_id= oprtr_id,
        proses_stat= 1,  # Proses başladı
        pdk_ad = lot_transction.ad,
        bas_tarh = datetime.now()
    )
    db.session.add(new_progress)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    if lot_transction.bas_tarh is None:
        lot_transction.bas_tarh = datetime.now()
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()

    return redirect(url_for('progress.pdk_progress', lot_trans_id=lot_trans_id))

@progress_bp.route("/proses-duraklat/<int:lot_trans_id>/", methods=["GET","POST"])
def progress_pause(lot_trans_id):
    saglam_ad = request.form.get("saglam_adet_duraklat", 0)
    uygnsuz_ad = request.form.get("uygunsuz_adet_duraklat", 0)
    uygunsuzluk_id = request.form.get("uygunsuzluk_tanim_duraklat", None)
    uygnsuzluk_aciklama = request.form.get("uygunsuz_aciklama_duraklat", "")

    if int(saglam_ad) == 0 or uygnsuz_ad == "":
        flash("Lütfen sağlam ve uygunsuz adetlerini giriniz.", "error")
        return redirect(url_for('progress.pdk_progress',lot_trans_id=lot_trans_id))
    if int(uygnsuz_ad) > 0 and (uygunsuzluk_id is None or uygunsuzluk_id == ""):
        flash("Lütfen uygunsuzluk tanımını seçiniz.", "error")
        return redirect(url_for('progress.pdk_progress',lot_trans_id=lot_trans_id))

    # Proses duraklatma işlemi için gerekli verileri alınacak flash eklenecek hata raporuna pdk ve alt pdk id eklenecek
    last_operation = db.session.query(Progress).filter(and_(Progress.lot_transc_id==lot_trans_id, Progress.proses_stat == 1)).order_by(Progress.bas_tarh.desc()).first()

    last_operation.saglam_ad = int(saglam_ad)
    last_operation.uygnsuz_ad = int(uygnsuz_ad)
    last_operation.proses_stat = 2  # Proses duraklatıldı
    last_operation.bit_tarh = datetime.now()

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    if last_operation.alt_pdk_id is not None:
        if int(uygnsuz_ad) > 0:
            new_hata_raporu = Hataraporu(
                lot_id=last_operation.ust_pdk.lot_id,
                pdk_id=last_operation.pdk_id,
                alt_pdk_id=last_operation.alt_pdk_id,
                operasyon_id=last_operation.opr_id,
                kontrol_type=last_operation.opr.opr_name,
                kafile_ad=int(saglam_ad)+int(uygnsuz_ad),
                kontrol_ad=int(saglam_ad)+int(uygnsuz_ad),
                uygnslk_id=uygunsuzluk_id,
                ad=int(uygnsuz_ad),
                descr_uyg=uygnsuzluk_aciklama,
                personel_id=last_operation.pers_id,
                baslangic_tarih=datetime.now(),
                bitis_tarih=datetime.now()
            )
            db.session.add(new_hata_raporu)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
    else:
        if int(uygnsuz_ad) > 0:
            new_hata_raporu = Hataraporu(
                lot_id=last_operation.ust_pdk.lot_id,
                pdk_id=last_operation.pdk_id,
                operasyon_id=last_operation.opr_id,
                kontrol_type=last_operation.opr.opr_name,
                kafile_ad=int(saglam_ad) + int(uygnsuz_ad),
                kontrol_ad=int(saglam_ad) + int(uygnsuz_ad),
                uygnslk_id=uygunsuzluk_id,
                ad=int(uygnsuz_ad),
                descr_uyg=uygnsuzluk_aciklama,
                personel_id=last_operation.pers_id,
                baslangic_tarih=datetime.now(),
                bitis_tarih=datetime.now()
            )
            db.session.add(new_hata_raporu)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()


    return redirect(url_for('progress.pdk_progress', lot_trans_id=lot_trans_id))

@progress_bp.route("/proses-bitir/<int:lot_trans_id>/", methods=["GET","POST"])
def progress_finish(lot_trans_id):
    saglam_ad = request.form.get("saglam_adet_bitir", 0)
    uygunsuz_ad = request.form.get("uygunsuz_adet_bitir", 0)
    uygunsuzluk_id = request.form.get("uygunsuzluk_tanim_bitir", None)
    uygunsuzluk_aciklama = request.form.get("uygunsuz_aciklama_bitir", "")

    lot_transction = db.get_or_404(Lottransc, lot_trans_id)

    if int(saglam_ad) == 0 or uygunsuz_ad == "":
        flash("Lütfen sağlam ve uygunsuz adetlerini giriniz.")
        return redirect(url_for('progress.pdk_progress',lot_trans_id=lot_trans_id))
    if int(uygunsuz_ad) > 0 and (uygunsuzluk_id is None or uygunsuzluk_id == ""):
        flash("Lütfen uygunsuzluk tanımını seçiniz.")
        return redirect(url_for('progress.pdk_progress',lot_trans_id=lot_trans_id))

    last_operation = db.session.query(Progress).filter(Progress.lot_transc_id == lot_trans_id).order_by(Progress.bas_tarh.desc()).first()

    result = db.session.query(
        func.sum(func.coalesce(Progress.saglam_ad, 0)).label("toplam_saglam"),
        func.sum(func.coalesce(Progress.uygnsuz_ad, 0)).label("toplam_uygunsuz")
    ).filter(Progress.lot_transc_id == lot_trans_id).first()
    toplam = (result.toplam_saglam or 0) + (result.toplam_uygunsuz or 0)

    if toplam + int(saglam_ad) + int(uygunsuz_ad) < last_operation.pdk_ad:
        flash("Toplam adet, pdk adedinden az olamaz.")
        return redirect(url_for('progress.pdk_progress',lot_trans_id=lot_trans_id))



    last_operation.saglam_ad = int(saglam_ad)
    last_operation.uygnsuz_ad = int(uygunsuz_ad)
    last_operation.proses_stat = 0  # Proses bitirildi
    last_operation.bit_tarh = datetime.now()

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    if lot_transction.bit_tarh is None:
        lot_transction.bit_tarh = datetime.now()
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()

    return redirect(url_for('progress.pdk_progress', lot_trans_id=lot_trans_id))