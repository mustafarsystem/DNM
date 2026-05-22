/*!
* Start Bootstrap - Clean Blog v6.0.9 (https://startbootstrap.com/theme/clean-blog)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-clean-blog/blob/master/LICENSE)
*/
window.addEventListener('DOMContentLoaded', () => {
    let scrollPos = 0;
    const mainNav = document.getElementById('mainNav');
    const headerHeight = mainNav.clientHeight;
    window.addEventListener('scroll', function() {
        const currentTop = document.body.getBoundingClientRect().top * -1;
        if ( currentTop < scrollPos) {
            // Scrolling Up
            if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-visible');
            } else {
                console.log(123);
                mainNav.classList.remove('is-visible', 'is-fixed');
            }
        } else {
            // Scrolling Down
            mainNav.classList.remove(['is-visible']);
            if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-fixed');
            }
        }
        scrollPos = currentTop;
    });
})

// PDK Böl Modal dinamik satır ve adet kontrolü

document.addEventListener('DOMContentLoaded', function() {
    const rowsContainer = document.getElementById('pdkBolRows');
    const adetUyari = document.getElementById('adetUyari');

    function toplamAdetHesapla() {
        let toplam = 0;
        document.querySelectorAll('.adet-input').forEach(input => {
            toplam += parseInt(input.value) || 0;
        });
        return toplam;
    }

    function getMaxAdet() {
        // progress.html'de bir elemente pdk.ad değerini ekleyip JS'de okuyacağız
        const maxAdetElem = document.getElementById('maxAdet');
        return parseInt(maxAdetElem.textContent) || 1000;
    }

    function adetKontrol() {
        const toplam = toplamAdetHesapla();
        const maxAdet = getMaxAdet();
        if (toplam > maxAdet) {
            adetUyari.textContent = `Toplam adet ${maxAdet}'i geçemez!`;
            adetUyari.classList.remove('d-none');
        } else {
            adetUyari.classList.add('d-none');
        }
    }

    rowsContainer.addEventListener('input', function(e) {
        if (e.target.classList.contains('adet-input')) {
            adetKontrol();
        }
    });

    rowsContainer.addEventListener('click', function(e) {
        if (e.target.classList.contains('add-row')) {
            e.preventDefault();
            const newRow = document.createElement('div');
            newRow.className = 'row mb-2 pdk-row align-items-center';
            newRow.innerHTML = `
                <div class="col-6 d-flex align-items-center">
                  <span class="fw-bold">Yeni PDK adedi:</span>
                </div>
                <div class="col-5">
                  <input type="number" name="pdk_adet[]" class="form-control adet-input" placeholder="Adet" min="1">
                </div>
                <div class="col-1">
                  <button type="button" class="btn btn-success add-row">+</button>
                </div>
            `;
            rowsContainer.appendChild(newRow);
        }
    });
});
