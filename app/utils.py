from datetime import datetime
from decimal import Decimal, InvalidOperation
from app.extensions import db
from app.models import SpcOlcum, SpcPlan, Lot

def parse_decimal(value):
    """
    Formdan gelen sayısal veriyi güvenli şekilde Decimal'e çevirir.
    Örnek:
      '10,25' -> Decimal('10.25')
      '0.005' -> Decimal('0.005')
    """
    if value is None or value == "":
        return None

    if isinstance(value, Decimal):
        return value

    value = str(value)
    try:
        cleaned = value.replace(",", ".").strip()
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def olcum_kaydet(lot_id, spc_id,hata_raporu_id, olc_yeri,pers_id,deger,cihaz_id,nots):
    """
    Formdan gelen ölçüm verilerini alır ve veritabanına kaydeder.
    """
    olcum = SpcOlcum(
        spc_plan_id=spc_id,
        lot_id=lot_id,
        hata_raporu_id=hata_raporu_id,
        olcum_yeri=olc_yeri,
        tarih=datetime.now(),
        olcen_kisi=pers_id,
        deger=parse_decimal(deger),
        cihaz=cihaz_id,
        notlar=nots
    )
    db.session.add(olcum)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Hata durumunda değişiklikleri geri al
        print(f"Hata: {str(e)}")  # Hata mesajını yazdır

    return olcum

def olcum_degerlendir(lot_id, hata_rapor_id):
    lot = db.get_or_404(Lot, lot_id)
    # spc_plan = db.session.query(SpcPlan).filter(SpcPlan.proje_id==lot.proje_id).all()
    olcum = db.session.query(SpcOlcum).filter(SpcOlcum.hata_raporu_id==hata_rapor_id).all()
    """
    Ölçüm değerini alt ve üst limitlere göre değerlendirir.
    """
    olcum_sonucu = {}
    for olc in olcum:
        if olc.spc_plan.olcu_tipi == "lineer" and (olc.spc_plan.cihaz != "Vida Halka Mastar" and olc.spc_plan.cihaz != "Vida Tampon Mastar" and olc.spc_plan.cihaz != "Pim Mastar" and olc.spc_plan.cihaz != "Halka Mastar"):
            spc = db.get_or_404(SpcPlan, olc.spc_plan_id)
            ust_limit = spc.nominal + spc.tol_plus
            alt_limit = spc.nominal + spc.tol_minus
            deger = olc.deger
            if deger is None:
                return "Geçersiz Değer"

            if alt_limit is not None and deger < alt_limit:
                print(deger, alt_limit)
                olcum_sonucu[olc.id] = 0  # Alt Limitin Altında
            elif ust_limit is not None and deger > ust_limit:
                print(deger, ust_limit)
                olcum_sonucu[olc.id] = 2  # Üst Limitin Üstünde
            else:
                olcum_sonucu[olc.id] = 1  # Limitler İçinde
        else:
            deger = olc.deger
            if deger is None:
                return "Geçersiz Değer"

            if deger == 0:
                olcum_sonucu[olc.id] = 0
            elif deger == 1:
                olcum_sonucu[olc.id] = 1

    uygunluk_list = list(olcum_sonucu.values())
    uygunluk = ""
    if 0 in uygunluk_list or 2 in uygunluk_list:
        uygunluk = "0"
    else:
        uygunluk = "1"
    return olcum_sonucu , uygunluk