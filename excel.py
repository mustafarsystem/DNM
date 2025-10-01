# Excel dosyası oluşturma

wb = Workbook()
ws = wb.active
ws['A1'] = lot.lot_no
ws['B1'] = ur_adet
excel_path = f"lot_{lot.lot_no}_bilgi.xlsx"
wb.save(excel_path)