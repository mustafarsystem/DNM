from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Proje, Projecihaz, Cihaz, Cnc, Satir, Siparis, Firmalar, Plan, Planstr, Malzstok, Malztransc, Lot
from math import ceil
from sqlalchemy import and_, or_, func
from datetime import datetime, timezone

from app.routes.stock_raw import malz_rezerve

plan_bp = Blueprint("plan", __name__)


@plan_bp.route("/planlama", methods=["GET", "POST"])
def planlama():
    cnc = db.session.query(Cnc).all()
    plan_filtre = request.args.get('plan_stat', '')
    if plan_filtre == '2' or plan_filtre == '' or plan_filtre == None:
        satirlar_tuple = db.session.query(Satir.proje_id).distinct().filter(
            or_(Satir.satr_stat == "İşleme Alındı", Satir.satr_stat == "Üretim Planına Alındı",Satir.satr_stat == "Lot Atandı")).all()
        projeler = [p[0] for p in satirlar_tuple]  # proje idleri
    if plan_filtre == '1':
        satirlar_tuple = db.session.query(Satir.proje_id).distinct().filter(or_(Satir.satr_stat == "Üretim Planına Alındı",Satir.satr_stat == "Lot Atandı")).all()
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
        planlar = db.session.query(Plan).filter(and_(Plan.proje_id == s, or_(Plan.plan_stat == 0,Plan.plan_stat == 1))).all()
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

    #Tezgah doluluk kontrolü
    # doluluk_durumu = {}
    # for c in cnc:
    #     plan_sure_cnc = db.session.query(func.sum(Plan.toplam_sure)).filter(and_(Plan.cnc_id == c.id, or_(Plan.plan_stat == 0, Plan.plan_stat == 1))).scalar()
    #     plan_for_cnc = db.session.query(Plan).filter(and_(Plan.cnc_id == c.id, Plan.plan_stat == 1)).all()
    #     lots_in_lot = db.session.query(Lot).all()
    #     all_plans = db.session.query(Plan).filter(and_(Plan.cnc_id == c.id, or_(Plan.plan_stat == 0, Plan.plan_stat == 1))).order_by(Plan.termin_tarihi.asc()).all()
    #     print(plan_sure_cnc)
    #     if plan_sure_cnc:
    #
    #         sure = plan_sure_cnc * 24 #günden saate çevirdik
    #     else:
    #         sure = 0
    #
    #     for p in plan_for_cnc:
    #
    #         for l in lots_in_lot:
    #             if l.plan_id == p.id and l.lot_stat == 'Seri İmalat' and p.ad > l.ad:
    #                 if l.sure:
    #                     sure -= int(round(((l.sure * l.ad) / (3600)))) #saniyeden saate çevirdik
    #
    #                     doluluk_durumu[c.id] = [sure,all_plans]
    #
    # print(type(doluluk_durumu[1][1][0].termin_tarihi))

    doluluk_durumu = {}

    cnc_list = db.session.query(Cnc).all()

    for c in cnc_list:
        # CNC'deki toplam plan süresi (aktif + bekleyen)
        plan_sure_cnc = db.session.query(func.sum(Plan.toplam_sure)).filter(
            and_(Plan.cnc_id == c.id, or_(Plan.plan_stat == 0, Plan.plan_stat == 1))
        ).scalar() or 0

        # aktif planlar
        plan_for_cnc = db.session.query(Plan).filter(
            and_(Plan.cnc_id == c.id, Plan.plan_stat == 1)
        ).all()

        lots_in_lot = db.session.query(Lot).all()

        # termin tarihine göre sıralı tüm planlar
        all_plans = db.session.query(Plan).filter(
            and_(Plan.cnc_id == c.id, or_(Plan.plan_stat == 0, Plan.plan_stat == 1))
        ).order_by(Plan.termin_tarihi.asc()).all()

        sure = plan_sure_cnc * 24  # gün → saat

        for p in plan_for_cnc:
            for l in lots_in_lot:
                if l.plan_id == p.id and l.lot_stat == "Seri İmalat" and p.ad > l.ad and l.sure:
                    sure -= int(round(((l.sure * l.ad) / 3600)))  # saniye → saat

        # total_time ve plan listesi (nesnelerle)
        doluluk_durumu[c.id] = {
            "total_time": sure,
            "plans": all_plans
        }

    return render_template("planlama.html", logged_in=current_user.is_authenticated, user=current_user, cnc=cnc,
                           satirlar=ort_satirlar, adetler=satir_adetleri, plan_adet=plan_adetleri,
                           plan_prjler=plan_prjler, doluluk=doluluk_durumu)


@plan_bp.route("/plan-ekle/<int:prj_id>", methods=["GET", "POST"])
def plan_ekle(prj_id):
    proje_to_add = db.get_or_404(Proje, prj_id)
    if proje_to_add.teklif_sure == 0 or proje_to_add.teklif_sure == None or proje_to_add.boy == 0 or proje_to_add.boy == None:
        flash("Projede eksik bilgiler var! Kontrol ediniz.")
        return redirect(url_for('plan.planlama'))

    cnc = db.session.query(Cnc).all()
    satirlar = db.session.query(Satir).filter(and_(Satir.proje_id == prj_id, or_(Satir.satr_stat == 'İşleme Alındı',Satir.satr_stat == 'Üretim Planına Alındı',Satir.satr_stat == 'Lot Atandı'))).order_by(Satir.ter_tarh).all()
    top_adet = db.session.query(func.sum(Satir.ad)).filter(and_(Satir.proje_id == prj_id,or_(Satir.satr_stat == 'İşleme Alındı',Satir.satr_stat == 'Üretim Planına Alındı',Satir.satr_stat == 'Lot Atandı'))).scalar()
    top_plan_ad = db.session.query(func.sum(Plan.ad)).filter(and_(Plan.proje_id == prj_id, or_(Plan.plan_stat == 0, Plan.plan_stat == 1))).scalar()
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
    satirlar = db.session.query(Satir).filter(and_(Satir.proje_id == prj_id, Satir.satr_stat == 'İşleme Alındı')).order_by(Satir.ter_tarh).all()
    print(satirlar)
    prj = db.get_or_404(Proje, prj_id)
    cnc_id = request.args.get('cnc_no', '')
    top_adet = db.session.query(func.sum(Satir.ad)).filter(and_(Satir.proje_id == prj_id,
                                                                or_(Satir.satr_stat == 'İşleme Alındı',
                                                                    Satir.satr_stat == 'Üretim Planına Alındı',Satir.satr_stat == 'Lot Atandı'))).scalar()
    print(top_adet)
    top_plan_ad = db.session.query(func.sum(Plan.ad)).filter(
        and_(Plan.proje_id == prj_id, or_(Plan.plan_stat == 0, Plan.plan_stat == 1))).scalar()
    print(top_plan_ad)
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
        kala_ad=ad,
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
    malz_rezerve = db.session.query(Malztransc).filter(and_(Malztransc.plan_id == plan_id, Malztransc.transc_type == 'Rezerve')).one()
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
    db.session.delete(malz_rezerve)
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

    plan_str_ad = {}
    planstr = db.session.query(func.sum(Planstr.plan_ad))
    for str in satirlar:
        p_ad = planstr.filter(Planstr.str_id == str.id).scalar()
        plan_str_ad[str.id] = p_ad

    return render_template("plan-edit.html", logged_in=current_user.is_authenticated, user=current_user, plan=plan,
                           proje=proje_to_add, satirlar=satirlar, cnc=cnc, plan_str_ad=plan_str_ad, top_adet=top_adet, top_plan_ad=top_plan_ad)


@plan_bp.route("/cnc-plan-edit/<int:plan_id>/<int:prj_id>", methods=["GET", "POST"])
def cnc_plan_edit(plan_id, prj_id):
    plan_to_delete = db.get_or_404(Plan, plan_id)
    planstr_to_delete = db.session.query(Planstr).filter(Planstr.plan_id == plan_id).all()
    cnc_id = int(request.args.get('cnc_edit_no', ''))
    print(f"CNC İD = {cnc_id}")
    print(plan_to_delete.cnc_id)
    if cnc_id == plan_to_delete.cnc_id:
        print("CNC idler aynı")
    try:
        ad = int(request.args.get('plan_edit_ad', ''))
    except ValueError:
        flash("Plana alınacak adet 0 olamaz!")
        return redirect(url_for('plan.plan_edit', plan_id=plan_id))
    if plan_to_delete.plan_stat == 2:
        flash("Tamamlanan planlarlar değiştirilemez!")
        return redirect(url_for('plan.plan_edit', plan_id=plan_id))
    if (plan_to_delete.plan_stat == 1 or plan_to_delete.plan_stat == 2) and plan_to_delete.cnc_id != cnc_id:
        flash("Plan aktif veya beklemede ise sadece adet değiştirilebilir!")
        return redirect(url_for('plan.plan_edit', plan_id=plan_id))
    if ad == 0:
        flash("Plana alınacak adet 0 olamaz!")
        return redirect(url_for('plan.plan_edit', plan_id=plan_id))
    if cnc_id == '0' or cnc_id == '':
        flash("Cnc no boş bırakılamaz!")
        return redirect(url_for('plan.plan_edit', plan_id=plan_id))

    for satir in planstr_to_delete:
        s = db.get_or_404(Satir, satir.str_id)

        s.satr_stat = "İşleme Alındı"
        db.session.delete(satir)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Hata durumunda değişiklikleri geri al
            print(f"Hata: {str(e)}")  # Hata mesajını yazdır
    # db.session.delete(plan_to_delete)
    # try:
    #     db.session.commit()
    # except Exception as e:
    #     db.session.rollback()  # Hata durumunda değişiklikleri geri al
    #     print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    satirlar = db.session.query(Satir).filter(
        and_(Satir.proje_id == prj_id, Satir.satr_stat == 'İşleme Alındı')).order_by(Satir.ter_tarh).all()
    prj = db.get_or_404(Proje, prj_id)

    malz_ad = int(ceil(ad / (2700 / (prj.boy + 3))))
    toplam_sure = int(ceil(((prj.teklif_sure * ad) + (8 * 3600)) / (3600 * 24)))
    plan_to_delete.ad = ad
    plan_to_delete.kala_ad = ad
    plan_to_delete.malz_ad = malz_ad
    plan_to_delete.toplam_sure = toplam_sure
    plan_to_delete.cnc_id = cnc_id

    if plan_to_delete.plan_stat == 1 :
        pass
    else:
        malz_rezerve = db.session.query(Malztransc).filter(
            and_(Malztransc.plan_id == plan_id, Malztransc.transc_type == 'Rezerve')).one()
        plan_to_delete.malz_id = None
        db.session.delete(malz_rezerve)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    # new_plan = Plan(
    #     proje_id=prj_id,
    #     cnc_id=cnc_id,
    #     ad=ad,
    #     kala_ad=ad,
    #     malz_ad=malz_ad,
    #     toplam_sure=toplam_sure
    # )
    # db.session.add(new_plan)
    # try:
    #     db.session.commit()
    # except Exception as e:
    #     db.session.rollback()  # Hata durumunda değişiklikleri geri al
    #     print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    plan_str_ad = {}
    planstr = db.session.query(func.sum(Planstr.plan_ad))
    for str in satirlar:
        p_ad = planstr.filter(Planstr.str_id == str.id).scalar()
        plan_str_ad[f'{str.id}'] = p_ad

    kalan_ad = ad

    for s in satirlar:
        if kalan_ad >= s.ad:
            if (plan_str_ad[f'{s.id}'] or 0) > 0:
                kalan_ad = kalan_ad - s.ad + (plan_str_ad[f'{s.id}'] or 0)
                s.satr_stat = "Üretim Planına Alındı"

                new_planstr = Planstr(
                    plan_id=plan_to_delete.id,
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
                    plan_id=plan_to_delete.id,
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
                    plan_id=plan_to_delete.id,
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
                        plan_id=plan_to_delete.id,
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
                        plan_id=plan_to_delete.id,
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

    ter = db.session.query(Planstr).filter(Planstr.plan_id == plan_to_delete.id).all()
    ter_tarih = []
    for i in ter:
        ter_tarih.append(i.str.ter_tarh)

    plan_to_delete.ter_tarh = sorted(ter_tarih)[0]
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır
    # for s in satirlar:
    #     if kalan_ad >= s.ad:
    #         if s.plan_ad > 0:
    #             kalan_ad = kalan_ad - s.ad + s.plan_ad
    #             s.satr_stat = "Üretim Planına Alındı"
    #             s.plan_ad = s.ad
    #             new_planstr = Planstr(
    #                 plan_id=plan_to_delete.id,
    #                 str_id=s.id
    #             )
    #             db.session.add(new_planstr)
    #             try:
    #                 db.session.commit()
    #             except Exception as e:
    #                 db.session.rollback()  # Hata durumunda değişiklikleri geri al
    #                 print(f"Hata: {str(e)}")  # Hata mesajını yazdır
    #         else:
    #
    #             kalan_ad = kalan_ad - s.ad
    #             s.satr_stat = "Üretim Planına Alındı"
    #             s.plan_ad = s.ad
    #             new_planstr = Planstr(
    #                 plan_id=plan_to_delete.id,
    #                 str_id=s.id
    #             )
    #             db.session.add(new_planstr)
    #             try:
    #                 db.session.commit()
    #             except Exception as e:
    #                 db.session.rollback()  # Hata durumunda değişiklikleri geri al
    #                 print(f"Hata: {str(e)}")  # Hata mesajını yazdır
    #     else:
    #         if kalan_ad > (s.ad - s.plan_ad):
    #             kalan_ad = kalan_ad - s.ad + s.plan_ad
    #             s.satr_stat = "Üretim Planına Alındı"
    #             s.plan_ad = s.ad
    #             new_planstr = Planstr(
    #                 plan_id=plan_to_delete.id,
    #                 str_id=s.id
    #             )
    #             db.session.add(new_planstr)
    #             try:
    #                 db.session.commit()
    #             except Exception as e:
    #                 db.session.rollback()  # Hata durumunda değişiklikleri geri al
    #                 print(f"Hata: {str(e)}")  # Hata mesajını yazdır
    #         else:
    #             if s.plan_ad > 0:
    #                 s.plan_ad += kalan_ad
    #                 new_planstr = Planstr(
    #                     plan_id=plan_to_delete.id,
    #                     str_id=s.id
    #                 )
    #                 db.session.add(new_planstr)
    #                 try:
    #                     db.session.commit()
    #                 except Exception as e:
    #                     db.session.rollback()  # Hata durumunda değişiklikleri geri al
    #                     print(f"Hata: {str(e)}")  # Hata mesajını yazdır
    #                 break
    #             else:
    #                 s.plan_ad = kalan_ad
    #                 new_planstr = Planstr(
    #                     plan_id=plan_to_delete.id,
    #                     str_id=s.id
    #                 )
    #                 db.session.add(new_planstr)
    #                 try:
    #                     db.session.commit()
    #                 except Exception as e:
    #                     db.session.rollback()  # Hata durumunda değişiklikleri geri al
    #                     print(f"Hata: {str(e)}")  # Hata mesajını yazdır
    #                 break

    return redirect(url_for('plan.planlama'))


@plan_bp.route("/cnc-plan/<int:cnc_id>", methods=["GET", "POST"])
def cnc_plan(cnc_id):
    planlar = db.session.query(Plan).filter(and_(Plan.cnc_id == cnc_id, Plan.plan_stat == 0)).order_by(
        Plan.plan_sira_no).all()
    print(planlar)

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

@plan_bp.route("/cnc-auto-plan/<int:cnc_id>", methods=["GET", "POST"])
def cnc_auto_plan(cnc_id):
    planlar = db.session.query(Plan).filter(and_(Plan.cnc_id == cnc_id, Plan.plan_stat == 0)).all()
    planlar_with_cr = []
    for p in planlar:
        termin =datetime.combine(p.termin_tarihi, datetime.min.time(), tzinfo=timezone.utc)
        delta = termin - datetime.now(timezone.utc)
        delta_saat = delta.total_seconds() / 3600
        delta_saat_rounded = round(delta_saat,1)
        critical_ratio = delta_saat_rounded / (p.toplam_sure * 24)
        planlar_with_cr.append((p, critical_ratio))
        print(critical_ratio)

    planlar_sorted = sorted(planlar_with_cr, key=lambda x: x[1])

    for p in planlar_sorted:
        p[0].plan_sira_no = planlar_sorted.index(p) + 1
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()


    return redirect(url_for('plan.cnc_plan', cnc_id=cnc_id))