from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Proje, Cnc, Plan, Lot, Uretim, Hataraporu, Personel, Users, SpcPlan, Cihaz, Projeopr, Operasyon, SpcOlcum,\
    Prjolcu
from math import ceil
from datetime import date, datetime
from sqlalchemy import and_, or_, func, desc
from collections import Counter
from app.utils import parse_decimal, olcum_kaydet, olcum_degerlendir

process_control_bp = Blueprint("process_control", __name__)

#proses kontrol ekranı
@process_control_bp.route("/proses-kontrol", methods=["GET","POST"])
def proses_kontrol():
    query = db.session.query(Lot).filter(or_(Lot.lot_stat == 'Ayar', Lot.lot_stat == 'Seri İmalat'))
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


@process_control_bp.route("/proses-kontrol-giris/<int:lot_id>", methods=["GET","POST"])
def proses_kontrol_giris(lot_id):
    lot = db.get_or_404(Lot, lot_id)
    prss_kontrol = db.session.query(Hataraporu).filter(Hataraporu.lot_id == lot_id).order_by(Hataraporu.baslangic_tarih).all()
    ilk_onay_cond = db.session.query(Hataraporu).filter(and_(Hataraporu.lot_id == lot_id, or_(Hataraporu.kontrol_type == 'İlk Onay',Hataraporu.kontrol_type == 'Proses Kontrol'))).order_by(Hataraporu.baslangic_tarih.desc()).first()
    personel = db.session.query(Personel).filter(Personel.division.has(Users.division == "Kalite Kontrol")).all()
    kontrol_suresi = {}

    if ilk_onay_cond:
        if ilk_onay_cond.bitis_tarih:

            is_ilkonay = True
        else:

            is_ilkonay = False

        for kontrol in prss_kontrol:

            if kontrol.bitis_tarih:
                kontrol_suresi[kontrol.id] = [
                    kontrol.baslangic_tarih,
                    kontrol.bitis_tarih,
                    (kontrol.bitis_tarih - kontrol.baslangic_tarih).total_seconds() / 60
                ]
            else:
                kontrol_suresi[kontrol.id] = [
                    kontrol.baslangic_tarih,
                    None,
                    None
                ]
    else:
        is_ilkonay = True

    is_ilkonay = True

    return render_template("proses-kontrol-giris.html", logged_in=current_user.is_authenticated, user=current_user, lot=lot, pk=prss_kontrol, kontrol_suresi=kontrol_suresi, ilk_onay=is_ilkonay, personel=personel, ilk_onay_cond=ilk_onay_cond)


@process_control_bp.route("/ilk-onay/<int:lot_id>", methods=["GET","POST"])
def ilk_onay(lot_id):

    lot = db.get_or_404(Lot, lot_id)
    opr_id = db.session.query(Operasyon).filter(Operasyon.opr_name == "Proses Kontrol").first()
    prjopr_id = db.session.query(Projeopr).filter(and_(Projeopr.prj_id == lot.proje_id, Projeopr.opr_id == opr_id.id)).first()
    personel = db.session.query(Personel).filter(Personel.division.has(Users.division == "Kalite Kontrol")).all()
    olcu = db.session.query(Prjolcu).filter(Prjolcu.prjopr_id == prjopr_id.id).all()
    pk_check = db.session.query(Hataraporu).filter(and_(Hataraporu.lot_id == lot_id, or_(Hataraporu.kontrol_type == 'İlk Onay',Hataraporu.kontrol_type == 'Proses Kontrol'),Hataraporu.bitis_tarih.is_(None))).order_by(Hataraporu.baslangic_tarih.desc()).first()
    ilk_onay_check = db.session.query(Hataraporu).filter(and_(Hataraporu.lot_id == lot_id, Hataraporu.kontrol_type == 'İlk Onay')).order_by(Hataraporu.baslangic_tarih.desc()).first()
    olcum_cihaz = {}
    for olc in olcu:
        cihaz = db.session.query(Cihaz).filter(Cihaz.cihaz_type == olc.olculer.cihaz).all()
        olcum_cihaz[olc.olcu_id] = cihaz
    print(olcum_cihaz)
    if pk_check:
        pass
    elif ilk_onay_check and ilk_onay_check.ad==0:


        pk = Hataraporu(
            lot_id=lot_id,
            operasyon_id=lot.opr_id,
            kontrol_type='Proses Kontrol',
            kafile_ad=1,
            kontrol_ad=1,
            baslangic_tarih=datetime.now(),

        )
        db.session.add(pk)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Hata durumunda değişiklikleri geri al
            print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    else:
        pk = Hataraporu(
            lot_id=lot_id,
            operasyon_id=lot.opr_id,
            kontrol_type='İlk Onay',
            kafile_ad=1,
            kontrol_ad=1,
            baslangic_tarih=datetime.now(),

        )
        db.session.add(pk)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Hata durumunda değişiklikleri geri al
            print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    return render_template("proses-kontrol-olcu.html", logged_in=current_user.is_authenticated, user=current_user, olcum_cihaz=olcum_cihaz, lot=lot, olcu=olcu,personel=personel)


@process_control_bp.route("/ilk-onay-bitir/<int:lot_id>", methods=["GET","POST"])
def ilk_onay_bitir(lot_id):
    lot = db.get_or_404(Lot, lot_id)
    # if request.method == 'POST':
    #     operator_id = request.form['operator']
    #     uygnlk = request.form['uygunluk']
    #     description = request.form['bulgu']
    #
    #     if uygnlk:
    #         ilk_onay = db.session.query(Hataraporu).filter(and_(Hataraporu.lot_id == lot_id, or_(Hataraporu.kontrol_type == 'İlk Onay',Hataraporu.kontrol_type == 'Proses Kontrol'))).order_by(Hataraporu.baslangic_tarih.desc()).first()
    #         uretim = db.session.query(Uretim).filter(Uretim.lot_id == lot_id).order_by(Uretim.tarih).first()
    #         if ilk_onay:
    #             if ilk_onay.bitis_tarih:
    #                 print("ilk onay bitmiş")
    #                 flash("İlk onay zaten tamamlanmış!")
    #                 return redirect(url_for('process_control.proses_kontrol_giris', lot_id=lot_id))
    #             else:
    #                 ilk_onay.bitis_tarih = datetime.now()
    #                 ilk_onay.personel_id = operator_id
    #                 try:
    #                     db.session.commit()
    #                 except Exception as e:
    #                     db.session.rollback()  # Hata durumunda değişiklikleri geri al
    #                     print(f"Hata: {str(e)}")  # Hata mesajını yazdır
    #                 if ilk_onay.kontrol_type == "İlk Onay" and uygnlk == "1":
    #                     ayar_onay_sure = (datetime.now()-uretim.tarih).total_seconds()/ 60
    #                     ilk_onay.ad = 0
    #                     ilk_onay.descr_uyg = description
    #                     lot.lot_stat = "Seri İmalat"
    #                     ilk_onay_sure = (ilk_onay.bitis_tarih - ilk_onay.baslangic_tarih).total_seconds() / 60
    #                     ayar_sure =  ayar_onay_sure - ilk_onay_sure
    #                     new_uretim = Uretim(
    #                         lot_id=lot_id,
    #                         ur_ad=1,
    #                         statu_id=13,
    #                         sure=ayar_sure,
    #                         descr_statu="Ayar",
    #                         tarih=datetime.now()
    #                     )
    #                     db.session.add(new_uretim)
    #                     try:
    #                         db.session.commit()
    #                     except Exception as e:
    #                         db.session.rollback()
    #                 elif ilk_onay.kontrol_type == "İlk Onay" and uygnlk == "0":
    #                     ilk_onay.ad = 1
    #                     ilk_onay.descr_uyg = description
    #                     try:
    #                         db.session.commit()
    #                     except Exception as e:
    #                         db.session.rollback()
    #                 elif ilk_onay.kontrol_type == "Proses Kontrol" and uygnlk == "1":
    #                     ilk_onay.ad = 0
    #                     ilk_onay.descr_uyg = description
    #                     try:
    #                         db.session.commit()
    #                     except Exception as e:
    #                         db.session.rollback()
    #                 elif ilk_onay.kontrol_type == "Proses Kontrol" and uygnlk == "0":
    #                     ilk_onay.ad = 1
    #                     ilk_onay.descr_uyg = description
    #                     try:
    #                         db.session.commit()
    #                     except Exception as e:
    #                         db.session.rollback()
    #     else:
    #         flash("Uygunluk Durumunu Seçiniz!")
    #         return redirect(url_for('process_control.proses_kontrol_giris', lot_id=lot_id))

    return redirect(url_for('process_control.proses_kontrol_giris', lot_id=lot_id))

#saatlik kontrol sayfası
@process_control_bp.route("/saatlik-kontrol/<int:lot_id>", methods=["GET","POST"])
def saatlik_kontrol(lot_id):
    lot = db.get_or_404(Lot, lot_id)
    personel = db.session.query(Personel).filter(Personel.division.has(Users.division == "Kalite Kontrol")).all()
    lot_saat = db.session.query(Uretim).filter(and_(Uretim.lot_id == lot_id, Uretim.lot_saat.isnot(None))).order_by(Uretim.tarih.desc()).all()
    lot_saat_pk = db.session.query(Hataraporu).filter(and_(Hataraporu.lot_id == lot_id,Hataraporu.uretim_id.isnot(None), Hataraporu.bitis_tarih.isnot(None))).all()
    lot_saat_pk_undone = db.session.query(Hataraporu).filter(and_(Hataraporu.uretim_id.isnot(None),Hataraporu.baslangic_tarih.isnot(None), Hataraporu.bitis_tarih.is_(None))).all()
    lot_saat_sure = {}
    lot_saat_done =[]
    lot_saat_undone = []
    for ur in lot_saat_pk:
        lot_saat_done.append(ur.uretim_id)
        sure = (ur.bitis_tarih - ur.baslangic_tarih).total_seconds() / 60
        lot_saat_sure[ur.uretim_id] = sure
    for ur in lot_saat_pk_undone:
        lot_saat_undone.append(ur.uretim_id)



    return render_template("saatlik-kontrol.html", logged_in=current_user.is_authenticated, user=current_user,lot=lot,lot_saat=lot_saat,lot_saat_done=lot_saat_done,lot_saat_undone=lot_saat_undone,personel=personel, lot_saat_sure=lot_saat_sure,lot_saat_pk=lot_saat_pk)

#saatlik kontrol başlatma
@process_control_bp.route("/saatlik-kontrol/<int:lot_id>/<int:ur_id>/<stat>", methods=["GET","POST"])
def saatlik_kontrol_baslat(lot_id, ur_id, stat):
    print(lot_id, ur_id, stat)
    lot = db.get_or_404(Lot, lot_id)
    opr_id = db.session.query(Operasyon).filter(Operasyon.opr_name == "Talaşlı İmalat").first()
    prjopr_id = db.session.query(Projeopr).filter(and_(Projeopr.prj_id == lot.proje_id, Projeopr.opr_id == opr_id.id)).first()
    olcu = db.session.query(Prjolcu).filter(Prjolcu.prjopr_id == prjopr_id.id).all()
    personel = db.session.query(Personel).filter(Personel.division.has(Users.division == "Üretim")).all()
    saatlik = db.session.query(Hataraporu).filter(and_(Hataraporu.lot_id == lot_id,Hataraporu.kontrol_type == 'Saatlik Kontrol',Hataraporu.bitis_tarih.is_(None))).order_by(Hataraporu.baslangic_tarih.desc()).first()
    olcum_cihaz = {}
    for olc in olcu:
        cihaz = db.session.query(Cihaz).filter(Cihaz.cihaz_type == olc.olculer.cihaz).all()
        olcum_cihaz[olc.olcu_id] = cihaz
    lot_saat = db.get_or_404(Uretim, ur_id)

    pk_lot_saat = db.session.query(Hataraporu).filter(and_(Hataraporu.uretim_id == ur_id,Hataraporu.bitis_tarih.is_(None))).first()
    print(pk_lot_saat)
    print(stat)
    print(saatlik)
    if pk_lot_saat:
        pass
    # saatlik ölçümü bitirmek için
    # if request.method == "POST":
    #     uygnlk = request.form[f"uygunluk-{ur_id}"]
    #     description = request.form[f"bulgular-{ur_id}"]
    #     oprt = request.form[f"operator-{ur_id}"]
    #     print(type(uygnlk))
    #     if uygnlk == "1":
    #         print("burada")
    #         pk_lot_saat.descr_uyg = description
    #         pk_lot_saat.personel_id = oprt
    #         pk_lot_saat.ad = 0
    #         pk_lot_saat.bitis_tarih = datetime.now()
    #
    #         try:
    #             db.session.commit()
    #         except Exception as e:
    #             db.session.rollback()
    #     elif uygnlk == "0":
    #         pk_lot_saat.descr_uyg = description
    #         pk_lot_saat.personel_id = oprt
    #         pk_lot_saat.ad = 1
    #         pk_lot_saat.bitis_tarih = datetime.now()
    #         try:
    #             db.session.commit()
    #         except Exception as e:
    #             db.session.rollback()
    #
    #     print(uygnlk, description, oprt)
    #
    #     return redirect(url_for('process_control.saatlik_kontrol', lot_id=lot_id))

    else:
        pk = Hataraporu(
            lot_id=lot_id,
            uretim_id=ur_id,
            operasyon_id=lot.opr_id,
            kontrol_type='Saatlik Kontrol',
            kafile_ad=lot_saat.ur_ad,
            kontrol_ad=1,
            baslangic_tarih=datetime.now(),

        )
        db.session.add(pk)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Hata durumunda değişiklikleri geri al
            print(f"Hata: {str(e)}")  # Hata mesajını yazdır



    return render_template("saatlik-kontrol-olcu.html", logged_in=current_user.is_authenticated, user=current_user, lot=lot, olcu=olcu, olcum_cihaz=olcum_cihaz, personel=personel, lot_saat=lot_saat)
    # return redirect(url_for('process_control.saatlik_kontrol', lot=lot))




@process_control_bp.route("/saatlik-etiket/<int:ur_id>", methods=["GET","POST"])
def saatlik_etiket(ur_id):
    uretim = db.get_or_404(Uretim, ur_id)
    lot = db.get_or_404(Lot, uretim.lot_id)
    hata_rapor = db.session.query(Hataraporu).filter(Hataraporu.uretim_id == ur_id).first()
    return render_template("saatlik-etiket.html", logged_in=current_user.is_authenticated, user=current_user, uretim=uretim, lot=lot, hata_rapor=hata_rapor)

@process_control_bp.route("/spc-olcum-kaydet/<int:lot_id>", methods=["GET","POST"])
def spc_olcum_kaydet(lot_id):
    lot = db.get_or_404(Lot, lot_id)
    opr_id = db.session.query(Operasyon).filter(Operasyon.opr_name == "Proses Kontrol").first()
    prjopr_id = db.session.query(Projeopr).filter(and_(Projeopr.prj_id == lot.proje_id, Projeopr.opr_id == opr_id.id)).first()
    spc_plan_lineer = db.session.query(Prjolcu).filter(Prjolcu.prjopr_id == prjopr_id.id).all()
    spc_plan_lineer_olculer = [spc.olculer for spc in spc_plan_lineer if spc.olculer.olcu_tipi == "lineer" and (spc.olculer.cihaz != "Vida Halka Mastar" and spc.olculer.cihaz != "Vida Tampon Mastar" and spc.olculer.cihaz != "Pim Mastar" and spc.olculer.cihaz != "Halka Mastar")]
    spc_plan_other_olculer = [spc.olculer for spc in spc_plan_lineer if spc.olculer.olcu_tipi != "lineer" or (spc.olculer.olcu_tipi == "lineer" and (spc.olculer.cihaz == "Vida Halka Mastar" or spc.olculer.cihaz == "Vida Tampon Mastar" or spc.olculer.cihaz == "Pim Mastar" or spc.olculer.cihaz == "Halka Mastar"))]
    ilk_onay = db.session.query(Hataraporu).filter(and_(Hataraporu.lot_id == lot_id,or_(Hataraporu.kontrol_type == 'İlk Onay',Hataraporu.kontrol_type == 'Proses Kontrol'),Hataraporu.bitis_tarih.is_(None))).order_by(Hataraporu.baslangic_tarih.desc()).first()
    print(spc_plan_lineer_olculer)
    if request.method == "POST":
        pers_id = request.form['olcumu_yapan']
        for s_lineer in spc_plan_lineer_olculer:
            deger = request.form.get(f'{s_lineer.id}-olcum_sonucu')
            değer_i = parse_decimal(deger)
            cihaz_id_i = request.form.get(f'{s_lineer.id}-cihaz_no')
            note_i = request.form.get(f'{s_lineer.id}-not')
            olcum_yeri = "Proses Kontrol"
            spc_id = s_lineer.id
            print(f'sonuçlar,{s_lineer.id} {değer_i}, {cihaz_id_i}, {note_i}')
            olcum_kaydet(lot_id=lot_id, spc_id=spc_id, hata_raporu_id=ilk_onay.id, olc_yeri=olcum_yeri, pers_id=pers_id,
                         deger=değer_i, cihaz_id=cihaz_id_i, nots=note_i)
        for s in spc_plan_other_olculer:
            sonuc = request.form.get(f'{s.id}-uygunluk')
            cihaz_id_i = request.form.get(f'{s.id}-cihaz_no')
            note_i = request.form.get(f'{s.id}-not')
            olcum_yeri = "Proses Kontrol"
            deger = None
            print(f'sonuçlar {sonuc}')
            if sonuc == "uygun":
                deger = 1

            elif sonuc == "uygunsuz":
                deger = 0

            olcum = SpcOlcum(
                spc_plan_id=s.id,
                lot_id=lot_id,
                hata_raporu_id=ilk_onay.id,
                olcum_yeri=olcum_yeri,
                tarih=datetime.now(),
                olcen_kisi=pers_id,
                deger=parse_decimal(deger),
                cihaz=cihaz_id_i,
                notlar=note_i
            )
            db.session.add(olcum)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()  # Hata durumunda değişiklikleri geri al
                print(f"Hata: {str(e)}")  # Hata mesajını yazdır

        description = request.form.get('desc', '')
        #
        #
        # for i in range(len(spc_plan_lineer_olculer)):
        #     print(i)
        #     değer_i = parse_decimal(deger[i])
        #     cihaz_id_i = cihaz_id[i]
        #     note_i = note[i]
        #     olcum_yeri = "Proses Kontrol"
        #     spc_id = spc_plan_lineer_olculer[i].olculer.id
        #
        #     olcum_kaydet(lot_id=lot_id, spc_id=spc_id,hata_raporu_id=ilk_onay.id, olc_yeri=olcum_yeri, pers_id=pers_id, deger=değer_i, cihaz_id=cihaz_id_i, nots=note_i)


    uretim = db.session.query(Uretim).filter(Uretim.lot_id == lot_id).order_by(Uretim.tarih).first()
    olcum_sonucu, uygnlk = olcum_degerlendir(lot_id=lot_id, hata_rapor_id=ilk_onay.id)
    print(uygnlk)
    if ilk_onay:
        if ilk_onay.bitis_tarih:
            print("ilk onay bitmiş")
            print(ilk_onay.bitis_tarih)
            print("Buradayız")
            flash("İlk onay zaten tamamlanmış!")
            return redirect(url_for('process_control.proses_kontrol_giris', lot_id=lot_id))
        else:
            ilk_onay.bitis_tarih = datetime.now()
            ilk_onay.personel_id = pers_id
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()  # Hata durumunda değişiklikleri geri al
                print(f"Hata: {str(e)}")  # Hata mesajını yazdır
            if ilk_onay.kontrol_type == "İlk Onay" and uygnlk == "1":
                ayar_onay_sure = (datetime.now() - uretim.tarih).total_seconds() / 60
                ilk_onay.ad = 0
                ilk_onay.descr_uyg = description
                lot.lot_stat = "Seri İmalat"
                ilk_onay_sure = (ilk_onay.bitis_tarih - ilk_onay.baslangic_tarih).total_seconds() / 60
                ayar_sure = ayar_onay_sure - ilk_onay_sure
                new_uretim = Uretim(
                    lot_id=lot_id,
                    ur_ad=1,
                    statu_id=13,
                    sure=ayar_sure,
                    descr_statu="Ayar",
                    tarih=datetime.now()
                )
                db.session.add(new_uretim)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
            elif ilk_onay.kontrol_type == "İlk Onay" and uygnlk == "0":
                ilk_onay.ad = 1
                ilk_onay.descr_uyg = description
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
            elif ilk_onay.kontrol_type == "Proses Kontrol" and uygnlk == "1":
                ilk_onay.ad = 0
                ilk_onay.descr_uyg = description
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
            elif ilk_onay.kontrol_type == "Proses Kontrol" and uygnlk == "0":
                ilk_onay.ad = 1
                ilk_onay.descr_uyg = description
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()



    return redirect(url_for('process_control.proses_kontrol_giris', lot_id=lot_id))



@process_control_bp.route("/spc-olcum-kaydet-saatlik/<int:lot_id>", methods=["GET","POST"])
def spc_olcum_kaydet_saatlik(lot_id):
    lot = db.get_or_404(Lot, lot_id)
    opr_id = db.session.query(Operasyon).filter(Operasyon.opr_name == "Talaşlı İmalat").first()
    prjopr_id = db.session.query(Projeopr).filter(and_(Projeopr.prj_id == lot.proje_id, Projeopr.opr_id == opr_id.id)).first()
    spc_plan_lineer = db.session.query(Prjolcu).filter(Prjolcu.prjopr_id == prjopr_id.id).all()
    spc_plan_lineer_olculer = [spc.olculer for spc in spc_plan_lineer if spc.olculer.olcu_tipi == "lineer" and (spc.olculer.cihaz != "Vida Halka Mastar" and spc.olculer.cihaz != "Vida Tampon Mastar" and spc.olculer.cihaz != "Pim Mastar" and spc.olculer.cihaz != "Halka Mastar")]
    spc_plan_other_olculer = [spc.olculer for spc in spc_plan_lineer if spc.olculer.olcu_tipi != "lineer" or (spc.olculer.olcu_tipi == "lineer" and (spc.olculer.cihaz == "Vida Halka Mastar" or spc.olculer.cihaz == "Vida Tampon Mastar" or spc.olculer.cihaz == "Pim Mastar" or spc.olculer.cihaz == "Halka Mastar"))]
    saatlik = db.session.query(Hataraporu).filter(and_(Hataraporu.lot_id == lot_id,Hataraporu.kontrol_type == 'Saatlik Kontrol')).order_by(Hataraporu.baslangic_tarih.desc()).first()
    print(spc_plan_lineer_olculer)
    if request.method == "POST":
        pers_id = request.form['olcumu_yapan']
        for s_lineer in spc_plan_lineer_olculer:
            deger = request.form.get(f'{s_lineer.id}-olcum_sonucu')
            değer_i = parse_decimal(deger)
            cihaz_id_i = request.form.get(f'{s_lineer.id}-cihaz_no')
            note_i = request.form.get(f'{s_lineer.id}-not')
            olcum_yeri = "İmalat"     #**************** BURADAYIZ *******************
            spc_id = s_lineer.id
            print(f'sonuçlar {değer_i}, {cihaz_id_i}, {note_i}')
            olcum_kaydet(lot_id=lot_id, spc_id=spc_id, hata_raporu_id=saatlik.id, olc_yeri=olcum_yeri, pers_id=pers_id,
                         deger=değer_i, cihaz_id=cihaz_id_i, nots=note_i)
        for s in spc_plan_other_olculer:
            sonuc = request.form.get(f'{s.id}-uygunluk')
            cihaz_id_i = request.form.get(f'{s.id}-cihaz_no')
            note_i = request.form.get(f'{s.id}-not')
            olcum_yeri = "Proses Kontrol"
            deger = None
            if sonuc == "uygun":
                deger = 1

            elif sonuc == "uygunsuz":
                deger = 0

            olcum = SpcOlcum(
                spc_plan_id=s.id,
                lot_id=lot_id,
                hata_raporu_id=saatlik.id,
                olcum_yeri=olcum_yeri,
                tarih=datetime.now(),
                olcen_kisi=pers_id,
                deger=parse_decimal(deger),
                cihaz=cihaz_id_i,
                notlar=note_i
            )
            db.session.add(olcum)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()  # Hata durumunda değişiklikleri geri al
                print(f"Hata: {str(e)}")  # Hata mesajını yazdır

        description = request.form.get('desc', '')

    uretim = db.session.query(Uretim).filter(Uretim.lot_id == lot_id).order_by(Uretim.tarih).first()
    olcum_sonucu, uygnlk = olcum_degerlendir(lot_id=lot_id, hata_rapor_id=saatlik.id)
    print(uygnlk)


    if saatlik:
        if saatlik.bitis_tarih:
            print("ilk onay bitmiş")
            flash("İlk onay zaten tamamlanmış!")
            return redirect(url_for('process_control.proses_kontrol_giris', lot_id=lot_id))
        else:
            saatlik.bitis_tarih = datetime.now()
            saatlik.personel_id = pers_id
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()  # Hata durumunda değişiklikleri geri al
                print(f"Hata: {str(e)}")  # Hata mesajını yazdır
            if saatlik.kontrol_type == "Saatlik Kontrol" and uygnlk == "1":

                saatlik.ad = 0
                saatlik.descr_uyg = description

                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
            elif saatlik.kontrol_type == "Saatlik Kontrol" and uygnlk == "0":
                saatlik.ad = 1
                saatlik.descr_uyg = description
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()




    return redirect(url_for('process_control.proses_kontrol_giris', lot_id=lot_id))