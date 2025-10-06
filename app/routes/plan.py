from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Proje, Projecihaz, Cihaz, Cnc, Satir, Siparis, Firmalar, Plan, Planstr, Malzstok, Malztransc
from math import ceil
from sqlalchemy import and_, or_, func


plan_bp = Blueprint("plan", __name__)


@plan_bp.route("/planlama", methods=["GET", "POST"])
def planlama():
    cnc = db.session.query(Cnc).all()
    plan_filtre = request.args.get('plan_stat', '')
    if plan_filtre == '2' or plan_filtre == '' or plan_filtre == None:
        satirlar_tuple = db.session.query(Satir.proje_id).distinct().filter(
            or_(Satir.satr_stat == "İşleme Alındı", Satir.satr_stat == "Üretim Planına Alındı")).all()
        projeler = [p[0] for p in satirlar_tuple]  # proje idleri
    if plan_filtre == '1':
        satirlar_tuple = db.session.query(Satir.proje_id).distinct().filter(
            Satir.satr_stat == "Üretim Planına Alındı").all()
        projeler = [p[0] for p in satirlar_tuple]  # proje idleri
    if plan_filtre == '0':
        satirlar_tuple = db.session.query(Satir.proje_id).distinct().filter(Satir.satr_stat == "İşleme Alındı").all()
        projeler = [p[0] for p in satirlar_tuple]  # proje idleri
    satirlar = []

    siparis_adetleri = db.session.query(Satir.proje_id, func.sum(Satir.ad).label("toplam_adet")).group_by(
        Satir.proje_id).all()
    satir_adetleri = dict(siparis_adetleri)  # projeid: toplam sipariş adedi şeklinde dict
    plan_adet = db.session.query(Plan.proje_id, func.sum(Plan.ad).label("toplam_adet")).group_by(Plan.proje_id).all()
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
        planlar = db.session.query(Plan).filter(and_(Plan.proje_id == s, Plan.plan_stat == 0)).all()
        plan_prjler[s] = planlar

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
        if len(filtreler) > 0:

            if firm_filtre:
                new_str = new_str.filter(and_(Satir.proje_id == s, Satir.sip.has(
                    Siparis.firma.has(Firmalar.name.ilike(f"%{firm_filtre}%")))))

            if urnno_filtre:
                new_str = new_str.filter(
                    and_(Satir.proje_id == s, Satir.urn.has(Proje.urn_no.ilike(f"%{urnno_filtre}%"))))

            if sipno_filtre:
                new_str = new_str.filter(
                    and_(Satir.proje_id == s, Satir.sip.has(Siparis.sip_no.ilike(f"%{sipno_filtre}%"))))

            if rsmno_filtre:
                new_str = new_str.filter(
                    and_(Satir.proje_id == s, Satir.urn.has(Proje.tkr_no.ilike(f"%{rsmno_filtre}%"))))
                s
            new_str = new_str.first()
            if new_str:
                ort_satirlar.append(new_str)

            else:
                pass
        else:

            new_str = new_str.filter(Satir.proje_id == s).first()
            ort_satirlar.append(new_str)

    return render_template("planlama.html", logged_in=current_user.is_authenticated, user=current_user, cnc=cnc,
                           satirlar=ort_satirlar, adetler=satir_adetleri, plan_adet=plan_adetleri,
                           plan_prjler=plan_prjler)


@plan_bp.route("/plan-ekle/<int:prj_id>", methods=["GET", "POST"])
def plan_ekle(prj_id):
    proje_to_add = db.get_or_404(Proje, prj_id)
    if proje_to_add.teklif_sure == 0 or proje_to_add.teklif_sure == None or proje_to_add.boy == 0 or proje_to_add.boy == None:
        flash("Projede eksik bilgiler var! Kontrol ediniz.")
        return redirect(url_for('plan.planlama'))

    cnc = db.session.query(Cnc).all()
    satirlar = db.session.query(Satir).filter(and_(Satir.proje_id == prj_id, or_(Satir.satr_stat == 'İşleme Alındı',
                                                                                 Satir.satr_stat == 'Üretim Planına Alındı'))).order_by(
        Satir.ter_tarh).all()
    top_adet = db.session.query(func.sum(Satir.ad)).filter(and_(Satir.proje_id == prj_id,
                                                                or_(Satir.satr_stat == 'İşleme Alındı',
                                                                    Satir.satr_stat == 'Üretim Planına Alındı'))).scalar()
    top_plan_ad = db.session.query(func.sum(Plan.ad)).filter(
        and_(Plan.proje_id == prj_id, or_(Plan.plan_stat == 0, Plan.plan_stat == 1))).scalar()
    plan_str_ad = {}
    planstr = db.session.query(func.sum(Planstr.plan_ad))
    for str in satirlar:
        p_ad = planstr.filter(Planstr.str_id == str.id).scalar()
        plan_str_ad[str.id] = p_ad

    return render_template("plan-ekle.html", logged_in=current_user.is_authenticated, user=current_user,
                           proje=proje_to_add, satirlar=satirlar, cnc=cnc, top_adet=top_adet, top_plan_ad=top_plan_ad,
                           plan_str_ad=plan_str_ad)


@plan_bp.route("/cnc-ekle/<int:prj_id>", methods=["GET", "POST"])
def cnc_ekle(prj_id):
    satirlar = db.session.query(Satir).filter(
        and_(Satir.proje_id == prj_id, Satir.satr_stat == 'İşleme Alındı')).order_by(Satir.ter_tarh).all()
    prj = db.get_or_404(Proje, prj_id)
    cnc_id = request.args.get('cnc_no', '')
    top_adet = db.session.query(func.sum(Satir.ad)).filter(and_(Satir.proje_id == prj_id,
                                                                or_(Satir.satr_stat == 'İşleme Alındı',
                                                                    Satir.satr_stat == 'Üretim Planına Alındı'))).scalar()
    top_plan_ad = db.session.query(func.sum(Plan.ad)).filter(
        and_(Plan.proje_id == prj_id, or_(Plan.plan_stat == 0, Plan.plan_stat == 1))).scalar()
    plan_str_ad = {}
    planstr = db.session.query(func.sum(Planstr.plan_ad))
    for str in satirlar:
        p_ad = planstr.filter(Planstr.str_id == str.id).scalar()
        plan_str_ad[f'{str.id}'] = p_ad

    try:
        ad = int(request.args.get('plan_ad', ''))
    except ValueError:
        flash("Plana alınacak adet 0 olamaz!")
        return redirect(url_for('plan.plan_ekle', prj_id=prj_id))
    if ad == 0:
        flash("Plana alınacak adet 0 olamaz!")
        return redirect(url_for('plan.plan_ekle', prj_id=prj_id))
    if cnc_id == '0' or cnc_id == '':
        flash("Cnc no boş bırakılamaz!")
        return redirect(url_for('plan.plan_ekle', prj_id=prj_id))
    if (top_plan_ad or 0) + ad > top_adet:
        flash("Sipariş adedinden fazla adet plana alınamaz!")
        return redirect(url_for('plan.plan_ekle', prj_id=prj_id))
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

    return redirect(url_for('plan.planlama'))


@plan_bp.route("/plan-sil/<int:plan_id>", methods=["GET", "POST"])
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

    return redirect(url_for('plan.planlama'))


@plan_bp.route("/plan-edit/<int:plan_id>", methods=["GET", "POST"])
def plan_edit(plan_id):
    plan = db.get_or_404(Plan, plan_id)
    prj_id = plan.proje_id
    proje_to_add = db.get_or_404(Proje, prj_id)
    cnc = db.session.query(Cnc).all()
    satirlar = db.session.query(Satir).filter(and_(Satir.proje_id == prj_id, or_(Satir.satr_stat == 'İşleme Alındı',
                                                                                 Satir.satr_stat == 'Üretim Planına Alındı'))).all()
    top_adet = db.session.query(func.sum(Satir.ad)).filter(and_(Satir.proje_id == prj_id,
                                                                or_(Satir.satr_stat == 'İşleme Alındı',
                                                                    Satir.satr_stat == 'Üretim Planına Alındı'))).scalar()
    top_plan_ad = plan.ad

    return render_template("plan-edit.html", logged_in=current_user.is_authenticated, user=current_user, plan=plan,
                           proje=proje_to_add, satirlar=satirlar, cnc=cnc, top_adet=top_adet, top_plan_ad=top_plan_ad)


@plan_bp.route("/cnc-plan-edit/<int:plan_id>/<int:prj_id>", methods=["GET", "POST"])
def cnc_plan_edit(plan_id, prj_id):
    plan_to_delete = db.get_or_404(Plan, plan_id)
    planstr_to_delete = db.session.query(Planstr).filter(Planstr.plan_id == plan_id).all()
    cnc_id = request.args.get('cnc_edit_no', '')
    try:
        ad = int(request.args.get('plan_edit_ad', ''))
    except ValueError:
        flash("Plana alınacak adet 0 olamaz!")
        return redirect(url_for('plan.plan_edit', plan_id=plan_id))
    if ad == 0:
        flash("Plana alınacak adet 0 olamaz!")
        return redirect(url_for('plan.plan_edit', plan_id=plan_id))
    if cnc_id == '0' or cnc_id == '':
        flash("Cnc no boş bırakılamaz!")
        return redirect(url_for('plan.plan_edit', plan_id=plan_id))

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

    return redirect(url_for('plan.planlama'))


@plan_bp.route("/cnc-plan/<int:cnc_id>", methods=["GET", "POST"])
def cnc_plan(cnc_id):
    planlar = db.session.query(Plan).filter(and_(Plan.cnc_id == cnc_id, Plan.plan_stat == 0)).order_by(
        Plan.plan_sira_no).all()

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
        malz_s = db.session.query(Malzstok).filter(
            and_(Malzstok.malz_name == malzeme_name, Malzstok.ad > 0, Malzstok.cap >= cap)).order_by(
            Malzstok.gir_tarh).all()
        malz = []
        malz_r_adet = []
        for m in malz_s:
            malz_ad = db.session.query(func.sum(Malztransc.ad)).filter(
                and_(Malztransc.transc_type == 'Rezerve', Malztransc.malz_id == m.id)).scalar()
            malz_r_ad = m.ad - (malz_ad or 0)

            if malz_r_ad > 0:
                malz.append((m, malz_r_ad))

        malz_r = db.session.query(Malztransc).filter(
            and_(Malztransc.transc_type == 'Rezerve', Malztransc.plan_id == p.id)).first()

        plan_malzleri[p.id] = (malz, malz_r, malz_r_adet)

        print(plan_malzleri)

    plan_terminleri = {}
    for p in planlar:
        plan_str = db.session.query(Planstr).join(Satir, Planstr.str_id == Satir.id).filter(
            Planstr.plan_id == p.id).order_by(Satir.ter_tarh).first()
        plan_terminleri[p.id] = plan_str.str.ter_tarh
    print(plan_terminleri)
    if request.method == 'POST':
        plan_sira_nolar = []
        for p in planlar:
            sira_no = request.form[f'sira_no_{p.id}']
            if sira_no == '' or sira_no == None:
                flash("Plan Sıra No Boş Bırakılamaz!")
                return redirect(url_for('plan.cnc_plan', cnc_id=cnc_id))
            plan_sira_nolar.append(sira_no)
            if len(plan_sira_nolar) != len(set(plan_sira_nolar)):
                flash("Birden fazla satıra aynı sıra no girilemez!")
                return redirect(url_for('plan.cnc_plan', cnc_id=cnc_id))
            p.plan_sira_no = sira_no
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()  # Hata durumunda değişiklikleri geri al
                print(f"Hata: {str(e)}")  # Hata mesajını yazdır
        planlar = db.session.query(Plan).filter(and_(Plan.cnc_id == cnc_id, Plan.plan_stat == 0)).order_by(
            Plan.plan_sira_no).all()

    return render_template("cnc-plan.html", logged_in=current_user.is_authenticated, user=current_user, plan=planlar,
                           cnc=cnc, termin=plan_terminleri, malz=plan_malzleri, malz_stok=malz_stok, mastar=plan_mastar)
