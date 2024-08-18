document.addEventListener('DOMContentLoaded', function () {
    var slider = document.getElementById('amount-range-slider');

    // Získání maximální částky z datového atributu
    var maxAmount = parseInt(slider.getAttribute('data-max-amount'));

    // Načtení aktuálních hodnot z datových atributů
    var currentMin = parseInt(slider.getAttribute('data-current-min')) || 0;
    var currentMax = parseInt(slider.getAttribute('data-current-max')) || maxAmount;

    noUiSlider.create(slider, {
        start: [currentMin, currentMax],  // Použití aktuálních hodnot jako výchozí
        connect: true,
        range: {
            'min': 0,
            'max': maxAmount+1
        },
        tooltips: [true, true],
        format: {
            to: function (value) {
                return parseInt(value, 10);
            },
            from: function (value) {
                return parseInt(value, 10);
            }
        }
    });

    slider.noUiSlider.on('update', function (values, handle) {
        document.getElementById('amount_min').value = values[0];
        document.getElementById('amount_max').value = values[1];
    });

    var tooltips = slider.getElementsByClassName('noUi-tooltip');
    for (var i = 0; i < tooltips.length; i++) {
        tooltips[i].classList.add('hidden-tooltip');
    }

    slider.addEventListener('mouseover', function () {
        for (var i = 0; i < tooltips.length; i++) {
            tooltips[i].classList.remove('hidden-tooltip');
        }
    });

    slider.addEventListener('mouseout', function () {
        for (var i = 0; i < tooltips.length; i++) {
            tooltips[i].classList.add('hidden-tooltip');
        }
    });
});
