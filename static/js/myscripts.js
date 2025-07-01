function myCreateFunction() {
    var table = document.getElementById("myTable");
    var row = table.insertRow(-1);
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);
    var cell3 = row.insertCell(2);
    var cell4 = row.insertCell(3);
    var cell5 = row.insertCell(4);
    var cell6 = row.insertCell(5);
    var cell7 = row.insertCell(6);
    var cell8 = row.insertCell(7);
    var cell9 = row.insertCell(8);
    cell1.innerHTML = '<input type="text" id="satır-no" class="form-control form-control-sm modal-form-alt-1 " name="order_items[][satır-no]" required>';
    cell2.innerHTML = '<input type="text" id="urun-kodu-modal" class="form-control form-control-sm modal-form-alt-2 " name="order_items[][urun-kodu]" required>';
    cell3.innerHTML = '<input type="text" id="tek-res-no-modal" class="form-control form-control-sm modal-form-alt-3 " name="order_items[][teknik-resim-no]" required>';
    cell4.innerHTML = '<input type="text" id="rev-no-modal" class="form-control form-control-sm modal-form-alt-4 " name="order_items[][rev-no]" required>';
    cell5.innerHTML = '<input type="text" id="urun-tanım-modal" class="form-control form-control-sm modal-form-alt-5 " name="order_items[][urun-tanımı]" required>';
    cell6.innerHTML = '<input type="number" id="ad" class="form-control form-control-sm modal-form-alt-6 " name="order_items[][adet]" required>';
    cell7.innerHTML = '<input type="date" id="ter-tarih" class="form-control form-control-sm modal-form" name="order_items[][ter-tarih]" required>';
    cell8.innerHTML = '<select class="form-select form-select-sm filtre-form" id="kal" aria-label="Small select example" name="order_items[][kalifikasyon]"><option value="1">Evet</option><option value="0">Hayır</option></select>';
    cell9.innerHTML = '<select class="form-select form-select-sm filtre-form" id="kal-class" aria-label="Small select example" name="order_items[][kal-sınıfı]"><option value="0">N/A</option><option value="A">A Sınıfı</option><option value="B">B Sınıfı</option><option value="C">C Sınıfı</option></select>';

}

let rowno = 0;

function myCreateFunction2() {
    rowno++;
    var table = document.getElementById("myTable2");
    var row = table.insertRow(-1);
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);
    var cell3 = row.insertCell(2);
    var cell4 = row.insertCell(3);
    var cell5 = row.insertCell(4);
    var cell6 = row.insertCell(5);
    var cell7 = row.insertCell(6);
    var cell8 = row.insertCell(7);
    var cell9 = row.insertCell(8);
    cell1.innerHTML = '<input type="text" id="satır-no2'+ rowno +'" class="form-control form-control-sm modal-form-alt-1 " name="order_items1[][satır-no]" required>';
    cell2.innerHTML = '<input type="text" id="urun-kodu-modal2'+ rowno +'" class="form-control form-control-sm modal-form-alt-2 " name="order_items1[][urun-kodu]" required>';
    cell3.innerHTML = '<input type="text" id="tek-res-no-modal2'+ rowno +'" class="form-control form-control-sm modal-form-alt-3 " name="order_items1[][teknik-resim-no]" required>';
    cell4.innerHTML = '<input type="text" id="rev-no-modal2'+ rowno +'" class="form-control form-control-sm modal-form-alt-4 " name="order_items1[][rev-no]" required>';
    cell5.innerHTML = '<input type="text" id="urun-tanım-modal2'+ rowno +'" class="form-control form-control-sm modal-form-alt-5 " name="order_items1[][urun-tanımı]" required>';
    cell6.innerHTML = '<input type="number" id="ad2'+ rowno +'" class="form-control form-control-sm modal-form-alt-6 " name="order_items1[][adet]" required>';
    cell7.innerHTML = '<input type="date" id="ter-tarih2'+ rowno +'" class="form-control form-control-sm modal-form" name="order_items1[][ter-tarih]" required>';
    cell8.innerHTML = '<select class="form-select form-select-sm filtre-form" id="kal2'+ rowno +'" aria-label="Small select example" name="order_items1[][kalifikasyon]"><option value="1">Evet</option><option value="0">Hayır</option></select>';
    cell9.innerHTML = '<select class="form-select form-select-sm filtre-form" id="kal-class2'+ rowno +'" aria-label="Small select example" name="order_items1[][kal-sınıfı]"><option value="0">N/A</option><option value="A">A Sınıfı</option><option value="B">B Sınıfı</option><option value="C">C Sınıfı</option></select>';

}






function firmaSec(firma) {
          document.getElementById('firma').value = firma; // Seçilen firmayı inputa yerleştir
          document.getElementById('firmaSonuclari').style.display = 'none'; // Sonuç listesini gizle
}

function validateFirma() {
    const searchInput = document.getElementById('firma');
    const enteredValue = searchInput.value.trim().toLowerCase();
    const firmaListesi = document.getElementById('firmaListesi');
    const options = firmaListesi.getElementsByTagName('li');
    let isValid = false;

    for (let i = 0; i < options.length; i++) {
        const firmName = options[i].textContent.trim().toLowerCase();
        if (firmName === enteredValue) {
            isValid = true; // Girilen firma listede varsa doğrula
            break;
        }
    }

    if (isValid == false) {
        document.getElementById('error-message').style.display = 'block'; // Hata mesajı göster
        searchInput.focus(); // Kullanıcıdan yeni giriş bekle
    }
    if (isValid) {
        document.getElementById('error-message').style.display = 'none'; // Hata mesajı göster

    }

}







function firmaAra() {
          const query = document.getElementById('firma').value.toLowerCase(); // Kullanıcıdan alınan terimi al
          const firmaListesi = document.getElementById('firmaListesi');
          const items = firmaListesi.getElementsByTagName('li');

          // Tüm firmaları gizle
          for (let item of items) {
              if (item.textContent.toLowerCase().includes(query)) {
                  item.style.display = 'list-item'; // Eşleşenleri göster
              } else {
                  item.style.display = 'none'; // Eşleşmeyenleri gizle
              }
          }

          // Eğer görünür sonuç yoksa listeyi gizle
          const anyVisible = Array.from(items).some(item => item.style.display === 'list-item');
          document.getElementById('firmaSonuclari').style.display = anyVisible ? 'block' : 'none';
}






document.addEventListener('click', function(event) {
        const firmaSonuclari = document.getElementById('firmaSonuclari');
        const firmaInput = document.getElementById('firma');
        const firmaAra = document.getElementById('firma-ara');

        // Eğer açılır liste açık değilse, tıklama yeri üzerinde denetim yapın
        if (firmaSonuclari.style.display === 'block') {
            if (event.target !== firmaInput && !firmaSonuclari.contains(event.target) && !firmaAra.contains(event.target)) {
                firmaSonuclari.style.display = 'none'; // Açılır listeyi gizle
            }
        }
});




        function deleteLastRow() {
        var table = document.getElementById("myTable");
        var rowCount = table.rows.length;
        if (rowCount > 2) { // Tablo başlığını korumak için en az bir satır olmalı
            table.deleteRow(rowCount - 1); // Son satırı siler
        }
}


document.addEventListener('DOMContentLoaded', function() {
    const today = new Date();
    
    // Başlangıç tarihi: Bugünden 6 ay öncesi
    const startDate = new Date(today);
    startDate.setMonth(today.getMonth() - 6);
    const formattedStartDate = startDate.toISOString().split('T')[0];

    // Bitiş tarihi: Bugünden 1 ay sonrası
    const endDate = new Date(today);
    endDate.setMonth(today.getMonth() + 1);
    const formattedEndDate = endDate.toISOString().split('T')[0];

    // Input alanlarına varsayılan değerleri ata
    document.getElementById('b-tarih').value = formattedStartDate;
    document.getElementById('s-tarih').value = formattedEndDate;
});

function enableEditing() {
            // Form elemanlarını düzenlenebilir hale getir
            var formElements = document.querySelectorAll('.editable-form input, .editable-form select, .editable-form textarea');
            formElements.forEach(function(element) {
                element.disabled = false; // Tüm elemanları enable yap
            });




        }


function toggleDeleteButtons() {
        // Tüm silme butonlarının görünür olup olmadığını kontrol et
        const deleteButtons = document.querySelectorAll('.delete-row');

        // Her butonun durumunu değiştir
        deleteButtons.forEach(button => {
            if (button.style.display === 'none') {
                button.style.display = 'inline-block'; // Silme butonlarını göster
            } else {
                button.style.display = 'none'; // Silme butonlarını gizle
            }
        });
        document.getElementById('editButton').style.display = 'none'; // Düzenle butonunu gizle
            document.getElementById('saveButton').style.display = 'block'; // Kaydet butonunu göster
            document.getElementById('deleteButton').style.display = 'block';
            document.getElementById('firma-ara').style.display = 'block';
            document.getElementById('s-ekle-button').style.display = 'block';


                // Form elemanlarını düzenlenebilir hale getir
            var formElements = document.querySelectorAll('.editable-form input, .editable-form select, .editable-form textarea');
            formElements.forEach(function(element) {
                element.disabled = false; // Tüm elemanları enable yap
            });
    }


let orderCount;
document.addEventListener('DOMContentLoaded', function() {
    getOrderCount();
});

function getOrderCount() {
    const orderRows = document.querySelectorAll('#orderBody tr');
    orderCount = orderRows.length;
    console.log('Sipariş sayısı:', orderCount);
}

function deleteLastRow2() {
        var table = document.getElementById("myTable2");
        var rowCount = table.rows.length;
        if (rowCount > (orderCount + 1) ) { // Tablo başlığını korumak için en az bir satır olmalı
            table.deleteRow(rowCount - 1); // Son satırı siler
        }
}

function popupAc() {
  window.open(
    '/proje-ekle',           // açılacak sayfa
    'Proje Girişi',           // pencere adı
    'width=700,height=500'    // boyut
  );
}

$(document).ready(function() {
    $('#malzeme').select2({
      placeholder: 'Malzeme seçiniz',
      allowClear: true
    });
  });

 $(document).ready(function() {
    $('#malzemestan').select2({
      placeholder: 'Malzeme standardı seçiniz',
      allowClear: true
    });
  });

function openPopup() {
    window.open(
      '/mastar-sec',           // açılacak sayfanın URL’si
      'popupWindow',          // pencere ismi (isteğe bağlı)
      'width=800,height=600,resizable=yes,scrollbars=yes' // pencere özellikleri
    );
  }


function rezerveEt(cncId, planId, selectIdSuffix) {
    const selectElement = document.getElementById('malzeme_select_' + selectIdSuffix);
    const selectedMalzId = selectElement.value;

    if (selectedMalzId === "0") {
      alert("Lütfen bir malzeme seçiniz.");
      return;
    }

    const url = `/malz-rez?cnc_id=${cncId}&plan_id=${planId}&malz_id=${selectedMalzId}`;
    window.location.href = url; // Sayfayı yönlendir
  }

 function openPrintWindow(url) {
    window.open(url, '_blank', 'width=800,height=1000');
  }