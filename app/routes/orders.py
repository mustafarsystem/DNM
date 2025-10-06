from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Firmalar, Siparis, Satir, Lot, Proje
from math import ceil
from forms import FirmForm, SiparisForm
from datetime import date, datetime
orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/siparis-ekle",methods=["GET","POST"])
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


        return redirect(url_for("orders.siparis"))




    return render_template("sipariş_ekle.html",logged_in=current_user.is_authenticated,user=current_user,orders=orders, firmalar=firmalar, page=page, total_pages=total_pages, lines=satirlar, toplam_kayit=toplam_kayit, page_to_render=page_to_render)


@orders_bp.route("/firma-ekle",methods=["GET","POST"])
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
        return redirect(url_for("orders.firma_ekle"))



    return render_template("firma-ekle.html",form=firma_form, logged_in=current_user.is_authenticated, user=current_user, firmalar=firmalar)


@orders_bp.route("/firma-sil/<int:firm_id>",methods=["GET","POST"])
def firma_sil(firm_id):
    firm_to_delete= db.get_or_404(Firmalar,firm_id)
    db.session.delete(firm_to_delete)
    db.session.commit()
    return redirect(url_for('orders.firma_ekle'))


@orders_bp.route("/firma-edit/<int:firm_id>",methods=["GET","POST"])
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
        return redirect(url_for('orders.firma_ekle'))
    return render_template("firma-ekle.html", form=edit_form,is_edit=True,logged_in=current_user.is_authenticated, user=current_user)

@orders_bp.route("/siparis-edit/<int:sip_id>",methods=["GET","POST"])
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

        return redirect(url_for('orders.siparis_edit',sip_id=sip_id))





    return render_template("sip-edit.html",is_str=False, logged_in=current_user.is_authenticated, user=current_user, order=siparis_to_edit,firmalar=firmalar, lines=lines)


@orders_bp.route("/satir-ekle/<int:sip_id>",methods=["GET","POST"])
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

        return redirect(url_for('orders.siparis_edit', sip_id=sip_id))

    return render_template("sip-edit.html",is_str=True, logged_in=current_user.is_authenticated, user=current_user,order=siparis_to_edit, firmalar=firmalar, lines=lines)




@orders_bp.route("/satir-sil/<int:str_id>/<int:sip_id>",methods=["GET","POST"])
def satir_sil(str_id,sip_id):
    satir_to_delete = db.get_or_404(Satir, str_id)
    db.session.delete(satir_to_delete)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    return redirect(url_for('orders.siparis_edit',sip_id=sip_id ))

@orders_bp.route("/siparis-sil/<int:sip_id>",methods=["GET","POST"])
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

    return redirect(url_for('orders.siparis'))

@orders_bp.route("/sip-filtre", methods=["GET","POST"])
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


@orders_bp.route("/sip-info", methods=["GET","POST"])
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