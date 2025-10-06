from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Malzeme, Projerevtakip, Operasyon, Projeopr, Proje, Projecihaz, Mastar
from math import ceil
from datetime import date, datetime
from sqlalchemy import and_, or_, desc
from collections import Counter

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/proje", methods=["GET","POST"])
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


@projects_bp.route("/proje-edit/<int:prj_id>", methods=["GET","POST"])
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
            return redirect(url_for('projects.proje_edit', prj_id=prj_id))


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


        return redirect(url_for('projects.proje'))


    return render_template("proje-edit.html", logged_in=current_user.is_authenticated, user=current_user, proje=proje_to_edit, malz=malz, malz_stan=malz_stan)

@projects_bp.route("/proje-rev-gunc/<int:prj_id>", methods=["GET","POST"])
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

    return redirect(url_for('projects.proje_edit', prj_id=prj_id))


@projects_bp.route("/opr-ekran/<int:prj_id>", methods=["GET","POST"])
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

@projects_bp.route("/opr-ekle/<int:prj_id>/<int:opr_id>", methods=["GET","POST"])
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

    return redirect(url_for('projects.opr_ekran', prj_id=prj_id))

@projects_bp.route("/opr-çikar/<int:prj_id>", methods=["GET","POST"])
def opr_cikar(prj_id):
    prj_opr=db.session.query(Projeopr).filter(Projeopr.prj_id == prj_id).order_by(desc(Projeopr.opr_sira_no)).first()

    db.session.delete(prj_opr)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    return redirect(url_for('projects.opr_ekran', prj_id=prj_id))

@projects_bp.route("/opr-desc-ekle/<int:prj_id>", methods=["GET","POST"])
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
                return redirect(url_for('projects.opr_ekran', prj_id=prj_id))
        if el['sira_no'] in opr_out_list:
            print('ok')
            if not el['desc'] or el['desc'].strip() == '' :
                print(f"açıkalama: {el['desc']}")
                flash("Dış Operasyon açıklaması Boş Bırakılamaz!")
                return redirect(url_for('projects.opr_ekran', prj_id=prj_id))

        prj_opr = db.session.query(Projeopr).filter(and_(Projeopr.prj_id == prj_id, Projeopr.opr_sira_no == el['sira_no'])).one()
        prj_opr.opr_desc =el['desc']
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Hata durumunda değişiklikleri geri al
            print(f"Hata: {str(e)}")  # Hata mesajını yazdır


    return redirect(url_for('projects.proje'))

@projects_bp.route("/mstr-ekle/<int:prj_id>/<int:mstr_id>", methods=["GET","POST"])
def mstr_ekle(prj_id,mstr_id):
    chz_added = db.session.query(Projecihaz).filter(Projecihaz.prj_id == prj_id)
    mastar_id = []
    for m in chz_added:
        mastar_id.append(m.cihaz_id)
    if mstr_id in mastar_id:
        flash("Aynı cihazdan 2 adet eklenemez!")
        return redirect(url_for('projects.opr_ekran', prj_id=prj_id))

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

    return redirect(url_for('projects.opr_ekran', prj_id=prj_id))

@projects_bp.route("/mstr-çikar/<int:prj_id>/<int:mstr_id>", methods=["GET","POST"])
def mstr_cikar(prj_id,mstr_id):
    prj_chz=db.session.query(Projecihaz).filter(and_(Projecihaz.prj_id == prj_id,Projecihaz.cihaz_id == mstr_id)).one()

    db.session.delete(prj_chz)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    return redirect(url_for('projects.opr_ekran', prj_id=prj_id))


#proje tarafına ölçüler ekleyeceğim zaman bunu kullanacağım
@projects_bp.route("/olculer", methods=["GET","POST"])
def olculer():
    return render_template("olculer.html", logged_in=current_user.is_authenticated, user=current_user)

