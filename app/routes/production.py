from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Proje, Projecihaz, Cihaz, Cnc, Plan, Malzstok, Malztransc, Projeopr, Lot, Uretim, Hataraporu, Tezgahstatu, Personel, Users, Uygunsuzluklar
from math import ceil
from datetime import date, datetime
from sqlalchemy import and_, or_, func, desc
from collections import Counter

production_bp = Blueprint("production", __name__)

@production_bp.route("/lot-add", methods=["GET","POST"])
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

@production_bp.route("/work-order/<int:cnc_id>", methods=["GET","POST"])
def is_emri(cnc_id):
    data = db.session.query(Plan).filter(and_(Plan.cnc_id == cnc_id, Plan.plan_stat == 0, Plan.plan_sira_no == 1)).first()
    still_work = db.session.query(Lot).filter(and_(or_(Lot.lot_stat == "Ayar",Lot.lot_stat == "Seri"),Lot.plan.has(Plan.cnc_id == cnc_id))).first()
    if data:
        if still_work:
            flash("İstasyonda Çalışan İş Mevcut")
            return redirect(url_for('production.lot_ekle'))
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

                new_uretim = Uretim(
                    lot_id=lot_to_add.id,
                    ur_ad=0,
                    descr_statu="Lot No Eklendi",
                    tarih=datetime.now()

                )
                db.session.add(new_uretim)

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
                return redirect(url_for('production.lot_ekle'))
    else:
        flash("Plan Sırası Girilmeli!")
        return redirect(url_for('production.lot_ekle'))





    return render_template("is-emri.html", logged_in=current_user.is_authenticated, user=current_user, data=data, siparis=siparis,termin=termin_tarihi, lot=new_lot, mastar=mastar)


#saatlik üretimlerin girildiği sayfa
@production_bp.route("/uretim-girisi", methods=["GET","POST"])
def uretim_add():


    lotlar = db.session.query(Lot).filter(or_(Lot.lot_stat == "Ayar", Lot.lot_stat == "Seri İmalat")).all()
    son_uretim_girisleri = {}
    for lot in lotlar:
        uretim_girisi = db.session.query(Uretim).filter(Uretim.lot_id == lot.id).order_by(Uretim.tarih.desc()).first()
        if uretim_girisi:
            son_uretim_girisleri[lot.id] = (datetime.now() - uretim_girisi.tarih).total_seconds() / 60
        else:
            son_uretim_girisleri[lot.id] = None



    return render_template("uretim-ekle.html", logged_in=current_user.is_authenticated, user=current_user, lot=lotlar, sureler=son_uretim_girisleri)

#üretim bitir sayfası lot bilgileri olacak ve koçan miktarı girilip üretim bitirilecek
@production_bp.route("/uretim-bitir/<int:lot_id>", methods=["GET","POST"])
def uretim_bitir(lot_id):
    lot = db.get_or_404(Lot, lot_id)
    tarihler = []
    ur_adetleri = {}
    siparisler = []
    malz_boy =lot.proje.boy
    gereken_malz = ceil(lot.ad / (2700 / (malz_boy + 3)))
    kullanılan_malz = db.session.query(func.sum(Malztransc.ad)).filter(and_(Malztransc.lot_id == lot_id, Malztransc.transc_type == 'Çıkış')).scalar()
    uygunsuz_ad = db.session.query(Hataraporu).filter(Hataraporu.lot_id == lot_id).all()

    for str in lot.plan.planstr:
        if str.str.sip.sip_no in siparisler:
            pass
        else:
            siparisler.append(str.str.sip.sip_no)

    sonuclar = db.session.query(Uretim).filter(and_(Uretim.lot_id == lot_id),Uretim.sure.isnot(None)).all()
    for t in sonuclar:
        date = t.tarih.date()
        if date in tarihler:
            pass
        else:
            tarihler.append(date)
    for u in sonuclar:
        u_date = u.tarih.date()
        for d in tarihler:
            if u_date == d:
                if d in ur_adetleri:
                    ur_adetleri[d][0] += u.ur_ad
                    ur_adetleri[d][1] += u.sure * 60
                else:
                    ur_adetleri[d] = [u.ur_ad, u.sure * 60, 0]
        for h in uygunsuz_ad:
            if u.id == h.uretim_id:
                ur_adetleri[d][2] += h.ad
            else:
                pass


    print(ur_adetleri)



    return render_template("uretim-bitir.html", logged_in=current_user.is_authenticated, user=current_user, lot=lot, sonuc=ur_adetleri, siparis=siparisler, malz=gereken_malz, kullanilan_malz=kullanılan_malz)


#tüm lotların göründüğü sayfa
@production_bp.route("/lot-takip", methods=["GET","POST"])
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
@production_bp.route("/lot-sil", methods=["GET","POST"])
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
@production_bp.route("/lot-info-add/<int:lot_id>", methods=["GET","POST"])
def lot_info_add(lot_id):
    operators = db.session.query(Personel).filter(Personel.division.has(Users.division == "Üretim")).all()
    uygunsuzluk = db.session.query(Uygunsuzluklar).all()
    son_uretim = db.session.query(Uretim).filter(Uretim.lot_id == lot_id).order_by(Uretim.tarih.desc()).first()
    lot = db.get_or_404(Lot, lot_id)
    if request.method == 'POST':
        if lot.lot_stat =="Ayar":
            flash("İlk Onay verilmedi. Üretim Bilgileri Girilemez")
            return redirect(url_for('production.lot_info_add', lot_id=lot_id))
        else:
            iml_sure = request.form['iml_sure']
            ayar_fire = request.form['ayar_fire']
            operator = request.form['operator']
            personel = request.form['personel']
            ur_adet = request.form['ur_ad']
            s_saat = request.form['bitis_saat']
            s_tarih = request.form['bitis_tarih']
            s_saat_obj = datetime.strptime(s_saat, "%H:%M").time()
            s_tarih_obj = datetime.strptime(s_tarih, '%Y-%m-%d')
            s_tarih_comb = datetime.combine(s_tarih_obj,s_saat_obj)
            if s_tarih_comb < son_uretim.tarih:
                flash("Üretim Tarihi ve Saati Son Üretim Tarihinden Küçük Olamaz!")
                return redirect(url_for('production.lot_info_add', lot_id=lot_id))
            if s_tarih_comb > datetime.now():

                flash("Üretim Tarihi ve Saati İleri Tarih Olamaz!")
                return redirect(url_for('production.lot_info_add', lot_id=lot_id))

            work_time = (s_tarih_comb - son_uretim.tarih).total_seconds() / 60

            lot.sure = iml_sure
            if lot.fire_ad:
                lot.fire_ad += int(ayar_fire)
            else:
                lot.fire_ad = int(ayar_fire)
            lot.operator_id = operator
            lot.ad += int(ur_adet)
            l_ay = str(s_tarih_comb.month).zfill(2)
            l_gün = str(s_tarih_comb.day).zfill(2)
            l_saat = str(s_tarih_comb.hour).zfill(2)
            l_dk = str(s_tarih_comb.minute).zfill(2)
            lot_saat = f"{lot.lot_no}-{l_ay}{l_gün}{l_saat}{l_dk}"


            new_uretim = Uretim(
                lot_id=lot_id,
                lot_saat=lot_saat,
                ur_ad=ur_adet,
                statu_id=15,
                sure=work_time,
                personel_id=personel,
                tarih=s_tarih_comb

            )
            db.session.add(new_uretim)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()  # Hata durumunda değişiklikleri geri al
                print(f"Hata: {str(e)}")  # Hata mesajını yazdır



            return redirect(url_for('production.uretim_add'))



    print(f'{lot_id} ok')
    return render_template("uretim-adet.html", logged_in=current_user.is_authenticated, user=current_user, operator=operators, lot=lot, uyg=uygunsuzluk, son_uretim=son_uretim)

@production_bp.route("/bekleme-add/<int:lot_id>", methods=["GET","POST"])
def bekleme_add(lot_id):
    lot = db.get_or_404(Lot, lot_id)
    son_uretim = db.session.query(Uretim).filter(Uretim.lot_id == lot_id).order_by(Uretim.tarih.desc()).first()
    duruslar = db.session.query(Tezgahstatu).filter(or_(Tezgahstatu.statu_baslık == "Sistem",Tezgahstatu.statu_baslık == "Üretim")).all()
    personel = db.session.query(Personel).filter(Personel.division.has(Users.division == "Üretim")).all()
    if request.method == "POST":
        durus_id = request.form['durus']
        durus_desc = request.form['desc']
        personel_id = request.form['personel']
        s_saat = request.form['bitis_saat']
        s_tarih = request.form['bitis_tarih']
        s_saat_obj = datetime.strptime(s_saat, "%H:%M").time()
        s_tarih_obj = datetime.strptime(s_tarih, '%Y-%m-%d')
        s_tarih_comb = datetime.combine(s_tarih_obj, s_saat_obj)
        if s_tarih_comb < son_uretim.tarih:
            flash("Tarih ve Saat Son Üretim Tarihinden Küçük Olamaz!")
            return redirect(url_for('production.bekleme_add', lot_id=lot_id))
        if s_tarih_comb > datetime.now():
            flash("Tarih ve Saat İleri Tarih Olamaz!")
            return redirect(url_for('production.bekleme_add', lot_id=lot_id))
        work_time = (s_tarih_comb - son_uretim.tarih).total_seconds() / 60

        new_uretim = Uretim(
            lot_id=lot_id,
            ur_ad=0,
            statu_id=durus_id,
            descr_statu=durus_desc,
            sure=work_time,
            personel_id=personel_id,
            tarih=s_tarih_comb

        )
        db.session.add(new_uretim)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Hata durumunda değişiklikleri geri al
            print(f"Hata: {str(e)}")  # Hata mesajını yazdır
        return redirect(url_for('production.uretim_add'))

    return render_template("uretim-durus.html", logged_in=current_user.is_authenticated, user=current_user, lot=lot, son_uretim=son_uretim, duruslar=duruslar, personel=personel)


#lot bilgisi yazdırma ekranı
@production_bp.route("/lot-print/<int:lot_id>", methods=["GET","POST"])
def lot_print(lot_id):
    lot = db.get_or_404(Lot, lot_id)
    uretim_lot = db.session.query(Uretim).filter(and_(Uretim.lot_id == lot_id, Uretim.lot_saat.isnot(None))).order_by(Uretim.tarih.desc()).first()

    return render_template("lot-print.html", logged_in=current_user.is_authenticated, user=current_user, lot=lot, son_uretim=uretim_lot)
