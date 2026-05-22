

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Proje, Projecihaz, Cihaz, Cnc, Plan, Malzstok, Malztransc, Projeopr, Lot, Uretim, Hataraporu, \
    Tezgahstatu, Personel, Users, Uygunsuzluklar, Planstr, Pdklotsaat, Pdk, Lottransc, Pdkbol
from math import ceil
from datetime import date, datetime
from sqlalchemy import and_, or_, func, desc
from collections import Counter

stock_bp = Blueprint("stock", __name__)

@stock_bp.route("/stock", methods=["GET","POST"])
def stok():
    query = db.session.query(Pdk)

    lot_filtre = request.args.get('lotno', '')
    parca_adi_filtre = request.args.get('parcaadi', '')
    urnno_filtre = request.args.get('urunkodu', '')
    rsmno_filtre = request.args.get('teknikresimno', '')
    revno_filtre = request.args.get('revno', '')



    if lot_filtre:
        query = query.filter(Pdk.lot.has(Lot.lot_no.ilike(f"%{lot_filtre}%")))
    if urnno_filtre:
        query = query.filter(Pdk.lot.has(Lot.proje.has(Proje.urn_no.ilike(f"%{urnno_filtre}%"))))
    if rsmno_filtre:
        query = query.filter(Pdk.lot.has(Lot.proje.has(Proje.tkr_no.ilike(f"%{rsmno_filtre}%"))))
    if revno_filtre:
        query = query.filter(Pdk.lot.has(Lot.proje.has(Proje.tkr_rev_no.ilike(f"%{revno_filtre}%"))))

    page = request.args.get("page", 1, type=int)
    per_page = 50
    toplam_kayit = query.count()

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    pdk_records = pagination.items
    guncel_opr = {}
    sonraki_opr = {}
    for p in pdk_records:
        gncl_opr = db.session.query(Lottransc).filter(Lottransc.pdk_id == p.id).order_by(Lottransc.sevk_tarh.desc()).first()

        if gncl_opr:
            guncel_opr[p.id] = gncl_opr.opr.opr_name
            sıradaki_opr_sira_no = db.session.query(Projeopr).filter(
                and_(Projeopr.prj_id == p.lot.proje_id, Projeopr.opr_id == gncl_opr.opr_id)).order_by(
                Projeopr.opr_sira_no).first()
            sıradaki_opr = db.session.query(Projeopr).filter(
                and_(Projeopr.prj_id == p.lot.proje_id, Projeopr.opr_sira_no == sıradaki_opr_sira_no.opr_sira_no + 1)).order_by(
                Projeopr.opr_sira_no).first()
            if sıradaki_opr and sıradaki_opr.opr_id == 5:
                sıradaki_opr = db.session.query(Projeopr).filter(
                    and_(Projeopr.prj_id == p.lot.proje_id, Projeopr.opr_sira_no == sıradaki_opr_sira_no.opr_sira_no + 2)).order_by(
                    Projeopr.opr_sira_no).first()
            else:
                pass
            if sıradaki_opr:
                sonraki_opr[p.id] = sıradaki_opr.oprsyn.opr_name
                print(sıradaki_opr.oprsyn.opr_name)
            else:
                sonraki_opr[p.id] = "N/A"
        else:
            guncel_opr[p.id] = "N/A"
            if p.lot.proje.opr[1].opr_id == 5 and len(p.lot.proje.opr) > 1:
                 sonraki_opr[p.id] = p.lot.proje.opr[2].oprsyn.opr_name if len(p.lot.proje.opr) > 2 else "N/A"
            else:
                sonraki_opr[p.id] = p.lot.proje.opr[1].oprsyn.opr_name if len(p.lot.proje.opr) > 1 else "N/A"
                print(guncel_opr)




    return render_template("stok.html", logged_in=current_user.is_authenticated, user=current_user, pdk=pdk_records, pagination=pagination, toplam_kayit=toplam_kayit, guncel_opr=guncel_opr, sonraki_opr=sonraki_opr)


@stock_bp.route("/pdk", methods=["GET","POST"])
def pdk():
    query = db.session.query(Uretim)
    pdk_query = db.session.query(Pdklotsaat).all()
    pdklar = db.session.query(Pdk).outerjoin(Lottransc, Lottransc.pdk_id == Pdk.id).filter(Lottransc.id == None).all()

    lot_filtre = request.args.get('lotno', '')
    parca_adi_filtre = request.args.get('parcaadi', '')
    urnno_filtre = request.args.get('urunkodu', '')
    rsmno_filtre = request.args.get('teknikresimno', '')
    revno_filtre = request.args.get('revno', '')

    if lot_filtre:
        query = query.filter(Uretim.lot.has(Lot.lot_no.ilike(f"%{lot_filtre}%")))
    if urnno_filtre:
        query = query.filter(Uretim.lot.has(Lot.proje.has(Proje.urn_no.ilike(f"%{urnno_filtre}%"))))
    if rsmno_filtre:
        query = query.filter(Uretim.lot.has(Lot.proje.has(Proje.tkr_no.ilike(f"%{rsmno_filtre}%"))))
    if revno_filtre:
        query = query.filter(Uretim.lot.has(Lot.proje.has(Proje.tkr_rev_no.ilike(f"%{revno_filtre}%"))))

    print(query.all())
    query = query.filter(Uretim.lot_saat.isnot(None)).all()

    pdk_list = []
    final_query = []
    if pdk_query:
        for p in pdk_query:
            pdk_list.append(p.ur_id)


        for q in query:
            print(p.ur_id, q.id)
            if q.id in pdk_list:
                print("Eşleşme var")
                pass

            else:
                print("Eşleşme yok eklendi")
                final_query.append(q)
    else:
        for q in query:
            final_query.append(q)

    print(len(final_query))

    if request.method == "POST":

        print("burdayız")
        selected_ids = request.form.getlist("selected[]")
        pdk_ids = request.form['pdk_ids']
        print(f'pdk_ids, {pdk_ids}')
        if pdk_ids:
            pdk_id = int(pdk_ids)
            pdk_to_add = db.get_or_404(Pdk, pdk_id)
            lot_ids = []
            toplam_adet = 0
            if selected_ids:
                for sid in selected_ids:
                    uretim_record = db.session.query(Uretim).filter_by(id=int(sid)).first()
                    if uretim_record:
                        toplam_adet += uretim_record.ur_ad
                        lot_ids.append(uretim_record.lot.id)
                if all(x == lot_ids[0] for x in lot_ids):
                    print("Tüm elemanlar aynı")
                    if pdk_to_add.lot_id != lot_ids[0]:
                        flash("Seçilen kayıtlar ile PDK kaydı farklı lotlara ait. Lütfen aynı lottan kayıtlar seçiniz.", "danger")
                        return redirect(url_for('stock.pdk'))
                else:
                    print("Farklı eleman var")
                    flash("Farklı lotlara ait kayıtlar seçtiniz. Lütfen aynı lottan kayıtlar seçiniz.", "danger")
                    return redirect(url_for('stock.pdk'))

                pdk_to_add.ad = pdk_to_add.ad + toplam_adet

                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()  # Hata durumunda değişiklikleri geri al
                    print(f"Hata: {str(e)}")  # Hata mesajını yazdır

                for sid in selected_ids:
                    uretim_record = db.session.query(Uretim).filter_by(id=int(sid)).first()

                    if uretim_record:

                        new_pdk_lotsaat = Pdklotsaat(
                            pdk_id=pdk_to_add.id,
                            ur_id=uretim_record.id,
                            ad=uretim_record.ur_ad
                        )
                        db.session.add(new_pdk_lotsaat)
                        try:
                            db.session.commit()
                        except Exception as e:
                            db.session.rollback()  # Hata durumunda değişiklikleri geri al
                            print(f"Hata: {str(e)}")  # Hata mesajını yazdır

                flash(f"Seçilen {len(selected_ids)} kayıt PDK tablosuna eklendi.", "success")
                return redirect(url_for("stock.pdk"))
            else:
                flash("Hiç kayıt seçilmedi. Lütfen en az bir kayıt seçiniz.", "warning")
                return redirect(url_for('stock.pdk'))
        else:
            lot_ids = []
            toplam_adet = 0
            if selected_ids:
                for sid in selected_ids:
                    uretim_record = db.session.query(Uretim).filter_by(id=int(sid)).first()
                    if uretim_record:
                        toplam_adet += uretim_record.ur_ad
                        lot_ids.append(uretim_record.lot.id)
                if all(x == lot_ids[0] for x in lot_ids):
                    print("Tüm elemanlar aynı")
                else:
                    print("Farklı eleman var")
                    flash("Farklı lotlara ait kayıtlar seçtiniz. Lütfen aynı lottan kayıtlar seçiniz.", "danger")
                    return redirect(url_for('stock.pdk'))

                new_pdk = Pdk(
                    lot_id=lot_ids[0],
                    ad=toplam_adet

                )
                db.session.add(new_pdk)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()  # Hata durumunda değişiklikleri geri al
                    print(f"Hata: {str(e)}")  # Hata mesajını yazdır

                for sid in selected_ids:
                    uretim_record = db.session.query(Uretim).filter_by(id=int(sid)).first()

                    if uretim_record:

                        new_pdk_lotsaat = Pdklotsaat(
                            pdk_id=new_pdk.id,
                            ur_id=uretim_record.id,
                            ad=uretim_record.ur_ad
                        )
                        db.session.add(new_pdk_lotsaat)
                        try:
                            db.session.commit()
                        except Exception as e:
                            db.session.rollback()  # Hata durumunda değişiklikleri geri al
                            print(f"Hata: {str(e)}")  # Hata mesajını yazdır

                flash(f"Seçilen {len(selected_ids)} kayıt PDK tablosuna eklendi.", "success")
                return redirect(url_for("stock.pdk"))
            else:
                flash("Hiç kayıt seçilmedi. Lütfen en az bir kayıt seçiniz.", "warning")
                return redirect(url_for('stock.pdk'))

    return render_template("pdk.html", logged_in=current_user.is_authenticated, user=current_user, uretim=final_query, pdk=pdklar)

@stock_bp.route("/pdk-etiket/<int:pdk_id>/", defaults={"altpdk_id": None}, methods=["GET", "POST"])
@stock_bp.route("/pdk-etiket/<int:pdk_id>/<int:altpdk_id>", methods=["GET", "POST"])
# @stock_bp.route("/pdk-etiket/<int:pdk_id>", methods=["GET", "POST"])
def pdk_etiket(pdk_id,altpdk_id):
    if altpdk_id:
        alt_pdk = db.session.query(Pdkbol).filter_by(id=altpdk_id).first()
        pdk_record = alt_pdk.ust_pdk
    else:
        pdk_record = db.session.query(Pdk).filter_by(id=pdk_id).first()
        if not pdk_record:
            flash("PDK kaydı bulunamadı.", "danger")
            return redirect(url_for("stock.stok"))

    yıl = datetime.now().year
    parca_kodu = pdk_record.lot.proje.urn_no if pdk_record.lot and pdk_record.lot.proje else ""
    parca_adi = pdk_record.lot.proje.urn_adi if pdk_record.lot and pdk_record.lot.proje else ""
    return render_template("pdk-etiket.html", pdk=pdk_record,yıl=yıl, logged_in=current_user.is_authenticated, user=current_user, alt_pdk=alt_pdk if altpdk_id else None)

@stock_bp.route("/stok-hareketi", methods=["GET", "POST"])
def stok_hareket():
    guncel_opr = {}
    sonraki_opr = {}

    lot_filtre = request.args.get('lotno', '')
    parca_adi_filtre = request.args.get('parcaadi', '')
    urnno_filtre = request.args.get('urunkodu', '')
    rsmno_filtre = request.args.get('teknikresimno', '')
    revno_filtre = request.args.get('revno', '')
    pdk_filtre = request.args.get('pdkno', '')
    pdk_no = int(pdk_filtre[-4:]) if pdk_filtre and pdk_filtre[-4:].isdigit() else None
    print(pdk_no)
    query = db.session.query(Pdk)
    if lot_filtre:
        query = query.filter(Pdk.lot.has(Lot.lot_no.ilike(f"%{lot_filtre}%")))
    if urnno_filtre:
        query = query.filter(Pdk.lot.has(Lot.proje.has(Proje.urn_no.ilike(f"%{urnno_filtre}%"))))
    if rsmno_filtre:
        query = query.filter(Pdk.lot.has(Lot.proje.has(Proje.tkr_no.ilike(f"%{rsmno_filtre}%"))))
    if revno_filtre:
        query = query.filter(Pdk.lot.has(Lot.proje.has(Proje.tkr_rev_no.ilike(f"%{revno_filtre}%"))))
    if pdk_no:
        query = query.filter(Pdk.id == pdk_no)


    page = request.args.get("page", 1, type=int)
    per_page = 50
    toplam_kayit = query.count()

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    pdk_records = pagination.items
    for p in pdk_records:
        if p.pdkbol:
            print("alt pdk var")


    for p in pdk_records:
        if p.pdkbol:
            gncl_opr = db.session.query(Lottransc).filter(Lottransc.pdk_id == p.id).order_by(
                Lottransc.sevk_tarh.desc()).first()
            if gncl_opr:
                if gncl_opr.alt_pdk_id:

                    for alt_pdk in p.pdkbol:

                        gncl_opr_alt_pdk = db.session.query(Lottransc).filter(Lottransc.alt_pdk_id == alt_pdk.id).order_by(Lottransc.sevk_tarh.desc()).first()
                        if gncl_opr_alt_pdk:
                            guncel_opr[f"{p.id}-{alt_pdk.id}"] = gncl_opr_alt_pdk.opr.opr_name
                            sıradaki_opr_sira_no = db.session.query(Projeopr).filter(
                                and_(Projeopr.prj_id == p.lot.proje_id, Projeopr.opr_id == gncl_opr_alt_pdk.opr_id)).order_by(
                                Projeopr.opr_sira_no).first()
                            sıradaki_opr = db.session.query(Projeopr).filter(
                                and_(Projeopr.prj_id == p.lot.proje_id,
                                     Projeopr.opr_sira_no == sıradaki_opr_sira_no.opr_sira_no + 1)).order_by(
                                Projeopr.opr_sira_no).first()
                            if sıradaki_opr and sıradaki_opr.opr_id == 5:
                                sıradaki_opr = db.session.query(Projeopr).filter(
                                    and_(Projeopr.prj_id == p.lot.proje_id,
                                         Projeopr.opr_sira_no == sıradaki_opr_sira_no.opr_sira_no + 2)).order_by(
                                    Projeopr.opr_sira_no).first()
                            else:
                                pass
                            if sıradaki_opr:
                                sonraki_opr[f"{p.id}-{alt_pdk.id}"] = sıradaki_opr.oprsyn.opr_name

                            else:
                                sonraki_opr[f"{p.id}-{alt_pdk.id}"] = "N/A"
                        else:
                            guncel_opr[f"{p.id}-{alt_pdk.id}"] = "N/A"
                            if p.lot.proje.opr[1].opr_id == 5 and len(p.lot.proje.opr) > 1:
                                sonraki_opr[f"{p.id}-{alt_pdk.id}"] = p.lot.proje.opr[2].oprsyn.opr_name if len(
                                    p.lot.proje.opr) > 2 else "N/A"
                            else:
                                sonraki_opr[f"{p.id}-{alt_pdk.id}"] = p.lot.proje.opr[1].oprsyn.opr_name if len(
                                    p.lot.proje.opr) > 1 else "N/A"

                else:
                    for alt_pdk in p.pdkbol:

                        guncel_opr[f"{p.id}-{alt_pdk.id}"] = gncl_opr.opr.opr_name
                        sıradaki_opr_sira_no = db.session.query(Projeopr).filter(
                            and_(Projeopr.prj_id == p.lot.proje_id, Projeopr.opr_id == gncl_opr.opr_id)).order_by(
                            Projeopr.opr_sira_no).first()
                        sıradaki_opr = db.session.query(Projeopr).filter(
                            and_(Projeopr.prj_id == p.lot.proje_id,
                                 Projeopr.opr_sira_no == sıradaki_opr_sira_no.opr_sira_no + 1)).order_by(
                            Projeopr.opr_sira_no).first()
                        if sıradaki_opr and sıradaki_opr.opr_id == 5:
                            sıradaki_opr = db.session.query(Projeopr).filter(
                                and_(Projeopr.prj_id == p.lot.proje_id,
                                     Projeopr.opr_sira_no == sıradaki_opr_sira_no.opr_sira_no + 2)).order_by(
                                Projeopr.opr_sira_no).first()
                        else:
                            pass
                        if sıradaki_opr:
                            sonraki_opr[f"{p.id}-{alt_pdk.id}"] = sıradaki_opr.oprsyn.opr_name

                        else:
                            sonraki_opr[f"{p.id}-{alt_pdk.id}"] = "N/A"
            else:
                for alt_pdk in p.pdkbol:
                    guncel_opr[f"{p.id}-{alt_pdk.id}"] = "N/A"
                    if p.lot.proje.opr[1].opr_id == 5 and len(p.lot.proje.opr) > 1:
                        sonraki_opr[f"{p.id}-{alt_pdk.id}"] = p.lot.proje.opr[2].oprsyn.opr_name if len(p.lot.proje.opr) > 2 else "N/A"
                    else:
                        sonraki_opr[f"{p.id}-{alt_pdk.id}"] = p.lot.proje.opr[1].oprsyn.opr_name if len(p.lot.proje.opr) > 1 else "N/A"
        else:
            gncl_opr = db.session.query(Lottransc).filter(Lottransc.pdk_id == p.id).order_by(Lottransc.sevk_tarh.desc()).first()

            if gncl_opr:
                guncel_opr[p.id] = gncl_opr.opr.opr_name
                sıradaki_opr_sira_no = db.session.query(Projeopr).filter(
                    and_(Projeopr.prj_id == p.lot.proje_id, Projeopr.opr_id == gncl_opr.opr_id)).order_by(
                    Projeopr.opr_sira_no).first()
                sıradaki_opr = db.session.query(Projeopr).filter(
                    and_(Projeopr.prj_id == p.lot.proje_id, Projeopr.opr_sira_no == sıradaki_opr_sira_no.opr_sira_no + 1)).order_by(
                    Projeopr.opr_sira_no).first()
                if sıradaki_opr and sıradaki_opr.opr_id == 5:
                    sıradaki_opr = db.session.query(Projeopr).filter(
                        and_(Projeopr.prj_id == p.lot.proje_id, Projeopr.opr_sira_no == sıradaki_opr_sira_no.opr_sira_no + 2)).order_by(
                        Projeopr.opr_sira_no).first()
                else:
                    pass
                if sıradaki_opr:
                    sonraki_opr[p.id] = sıradaki_opr.oprsyn.opr_name

                else:
                    sonraki_opr[p.id] = "N/A"
            else:
                guncel_opr[p.id] = "N/A"
                if p.lot.proje.opr[1].opr_id == 5 and len(p.lot.proje.opr) > 1:
                     sonraki_opr[p.id] = p.lot.proje.opr[2].oprsyn.opr_name if len(p.lot.proje.opr) > 2 else "N/A"
                else:
                    sonraki_opr[p.id] = p.lot.proje.opr[1].oprsyn.opr_name if len(p.lot.proje.opr) > 1 else "N/A"
    print(guncel_opr, sonraki_opr)

    return render_template("stok-hareketi.html", logged_in=current_user.is_authenticated, user=current_user,pdk=pdk_records, pagination=pagination, toplam_kayit=toplam_kayit,opr=guncel_opr, sonraki_opr=sonraki_opr)

@stock_bp.route("/stok-sevk/<int:pdk_id>", methods=["GET", "POST"])
def stok_sevk(pdk_id):
    pdk = db.get_or_404(Pdk, pdk_id)

    lot_transc_records = db.session.query(Lottransc).filter(Lottransc.pdk_id == pdk.id).order_by(Lottransc.sevk_tarh.desc()).first()
    print("1. adım")
    if lot_transc_records:
        operasyon = lot_transc_records.pdk.lot.proje.opr
        guncel_opr_id = lot_transc_records.opr_id
        sonraki_opr = None
        for opr in operasyon:
            if opr.opr_id == guncel_opr_id:
                sonraki_opr = db.session.query(Projeopr).filter(
                    and_(Projeopr.prj_id == pdk.lot.proje_id, Projeopr.opr_sira_no == opr.opr_sira_no + 1)).first()
                if sonraki_opr:
                    break

                else:
                    print("burdayızz")
                    flash("Sonraki operasyon bulunamadı.", "warning")
                    return redirect(url_for("stock.stok_hareket"))
        print(sonraki_opr.opr_id)
        print("2. adım")
        if lot_transc_records.bit_tarh is None:
            flash("Güncel Operasyon Tamamlanmadı!.", "warning")
            return redirect(url_for("stock.stok_hareket"))
        else:
            transc_type =sonraki_opr.oprsyn.opr_tip
            yeni_lot_transc = Lottransc(
                pdk_id=pdk.id,
                opr_id=sonraki_opr.opr_id,
                transc_type=transc_type,
                ad=pdk.ad,
                descrp=sonraki_opr.opr_desc,
                sevk_tarh=datetime.now()
            )
            db.session.add(yeni_lot_transc)
            try:
                db.session.commit()
                flash("Stok sevk işlemi başarıyla gerçekleştirildi.", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Stok sevk işlemi sırasında bir hata oluştu: {str(e)}", "danger")
    else:
        opr_to_sevk = pdk.lot.proje.opr[2] if pdk.lot.proje.opr[1].opr_id == 5 else pdk.lot.proje.opr[1]
        if opr_to_sevk:
            yeni_lot_transc = Lottransc(
                pdk_id=pdk.id,
                opr_id=opr_to_sevk.opr_id,
                transc_type=opr_to_sevk.oprsyn.opr_tip,
                ad=pdk.ad,
                descrp=opr_to_sevk.opr_desc,
                sevk_tarh=datetime.now()
            )
            db.session.add(yeni_lot_transc)
            try:
                db.session.commit()
                flash("Stok sevk işlemi başarıyla gerçekleştirildi.", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Stok sevk işlemi sırasında bir hata oluştu: {str(e)}", "danger")
        else:
            pass

    return redirect(url_for("stock.stok_hareket"))


@stock_bp.route("/stok-sevk-alt-pdk/<int:alt_pdk_id>", methods=["GET", "POST"])
def stok_sevk_alt_pdk(alt_pdk_id):
    alt_pdk = db.get_or_404(Pdkbol, alt_pdk_id)
    pdk=alt_pdk.ust_pdk

    lot_transc_records = db.session.query(Lottransc).filter(Lottransc.alt_pdk_id == alt_pdk.id).order_by(Lottransc.sevk_tarh.desc()).first()
    print("1. adım")
    if lot_transc_records:
        operasyon = lot_transc_records.pdk.lot.proje.opr
        guncel_opr_id = lot_transc_records.opr_id
        sonraki_opr = None
        for opr in operasyon:
            if opr.opr_id == guncel_opr_id:
                sonraki_opr = db.session.query(Projeopr).filter(
                    and_(Projeopr.prj_id == pdk.lot.proje_id, Projeopr.opr_sira_no == opr.opr_sira_no + 1)).first()
                if sonraki_opr:
                    break

                else:
                    print("burdayızz")
                    flash("Sonraki operasyon bulunamadı.", "warning")
                    return redirect(url_for("stock.stok_hareket"))
        print(sonraki_opr.opr_id)
        print("2. adım")
        if lot_transc_records.bit_tarh is None:
            flash("Güncel Operasyon Tamamlanmadı!.", "warning")
            return redirect(url_for("stock.stok_hareket"))
        else:
            transc_type =sonraki_opr.oprsyn.opr_tip
            yeni_lot_transc = Lottransc(
                pdk_id=pdk.id,
                alt_pdk_id=alt_pdk_id,
                opr_id=sonraki_opr.opr_id,
                transc_type=transc_type,
                ad=alt_pdk.ad,
                descrp=sonraki_opr.opr_desc,
                sevk_tarh=datetime.now()
            )
            db.session.add(yeni_lot_transc)
            try:
                db.session.commit()
                flash("Stok sevk işlemi başarıyla gerçekleştirildi.", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Stok sevk işlemi sırasında bir hata oluştu: {str(e)}", "danger")
    else:
        opr_to_sevk = pdk.lot.proje.opr[2] if pdk.lot.proje.opr[1].opr_id == 5 else pdk.lot.proje.opr[1]
        if opr_to_sevk:
            yeni_lot_transc = Lottransc(
                pdk_id=pdk.id,
                alt_pdk_id=alt_pdk_id,
                opr_id=opr_to_sevk.opr_id,
                transc_type=opr_to_sevk.oprsyn.opr_tip,
                ad=alt_pdk.ad,
                descrp=opr_to_sevk.opr_desc,
                sevk_tarh=datetime.now()
            )
            db.session.add(yeni_lot_transc)
            try:
                db.session.commit()
                flash("Stok sevk işlemi başarıyla gerçekleştirildi.", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Stok sevk işlemi sırasında bir hata oluştu: {str(e)}", "danger")
        else:
            pass

    return redirect(url_for("stock.stok_hareket"))





@stock_bp.route("/pdk-bol/<int:pdk_id>", methods=["GET", "POST"])
def pdk_bol(pdk_id):
    pdk = db.get_or_404(Pdk, pdk_id)

    pdk_adet_list = request.form.getlist("pdk_adet[]")
    print("buradayız")

    if pdk_adet_list:
        toplam = 0
        for adet in pdk_adet_list:
            toplam = toplam + int(adet)
        if toplam > pdk.ad:
            flash("Bölünecek adet toplamı, PDK adedinden fazla olamaz.", "danger")
            return redirect(url_for("stock.stok_hareket"))
        n = 1
        for p in pdk_adet_list:
            print(f"{p} adet bölünecek")

            new_pdk = Pdkbol(
                pdk_id=pdk.id,
                alt_pdk_no=f"PDK-{pdk.tarh.year}-{pdk.id:04d}-{n}" ,  # Alt PDK numarası olarak ana PDK numarasını kullanabilirsiniz
                ad=int(p),

            )
            db.session.add(new_pdk)
            n += 1

        if toplam < pdk.ad:
            kalan_adet = pdk.ad - toplam

            new_pdk = Pdkbol(
                pdk_id=pdk.id,
                alt_pdk_no=f"PDK-{pdk.tarh.year}-{pdk.id:04d}-{n}",  # Kalan adet için yeni bir alt PDK numarası
                ad=kalan_adet,
            )
            db.session.add(new_pdk)
        try:
            db.session.commit()
            print(f"{p} adet bölme işlemi başarıyla gerçekleştirildi.")

        except Exception as e:
            db.session.rollback()


    else:
        print("Bölünecek adet bilgisi alınamadı.")
    # Bölme işlemi için gerekli mantık burada uygulanacak
    # Örneğin, yeni bir PDK kaydı oluşturulabilir ve ilgili Lottransc kayıtları güncellenebilir
    flash("PDK bölme işlemi başarıyla gerçekleştirildi.", "success")
    return redirect(url_for("stock.stok"))