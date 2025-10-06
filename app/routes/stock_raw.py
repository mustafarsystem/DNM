from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Malzeme, Malztransc, Plan, Malzstok, Tedarikci, Siparistalep, Lot
from math import ceil
from datetime import date, datetime
from sqlalchemy import and_, func, desc
from collections import Counter

stock_raw_bp = Blueprint("stock_raw", __name__)

@stock_raw_bp.route("/malz-rez", methods=["GET","POST"])
def malz_rezerve():
    cnc_id = request.args.get("cnc_id")
    plan_id = request.args.get("plan_id")
    malz_id = request.args.get("malz_id")

    if malz_id == '0' or malz_id == '':
        flash("Malzeme Seçiniz!")
        return redirect(url_for('plan.cnc_plan', cnc_id=cnc_id))
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


    return redirect(url_for('plan.cnc_plan', cnc_id=cnc_id))

@stock_raw_bp.route("/malz-stok", methods=["GET","POST"])
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


@stock_raw_bp.route("/malz-sil/<int:malz_id>", methods=["GET","POST"])
def malz_sil(malz_id):
    malz_to_delete = db.get_or_404(Malzstok, malz_id)
    malz_trans = db.session.query(Malztransc).filter(Malztransc.malz_id == malz_id).first()
    if malz_trans:
        flash("Silmek istediğiniz malzeme no için malzeme hareketi mevcut. Silinemez!")
        return redirect(url_for('stock_raw.malz_stok'))
    else:
        db.session.delete(malz_to_delete)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Hata durumunda değişiklikleri geri al
            print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    return redirect(url_for('stock_raw.malz_stok'))

@stock_raw_bp.route("/malz-ekle", methods=["GET","POST"])
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
            return redirect(url_for('stock_raw.malz_stok'))


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



    return redirect(url_for('stock_raw.malz_stok'))

@stock_raw_bp.route("/malz-transc", methods=["GET","POST"])
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


@stock_raw_bp.route("/malz-transc-del/<int:trans_id>", methods=["GET","POST"])
def malz_hareket_sil(trans_id):
    transc_to_delete = db.get_or_404(Malztransc, trans_id)
    if transc_to_delete.transc_type == "Çıkış":
        flash("Ham malzeme çıkışı silinemez!")
        return redirect(url_for('stock_raw.malz_hareket'))
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

        return redirect(url_for('stock_raw.malz_hareket'))

@stock_raw_bp.route("/malz-transc-add", methods=["GET", "POST"])
def malz_hareket_ekle():
    # lot ekleme yapılıdıktan sonra düzenlenecek
    return render_template("malz-transc-add.html", logged_in=current_user.is_authenticated, user=current_user)