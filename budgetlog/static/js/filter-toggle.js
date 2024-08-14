document.addEventListener('DOMContentLoaded', function () {
    const toggleButton = document.getElementById('toggle-filter');
    const filterSection = document.getElementById('filter-section');

    // Načíst stav rozbalení z localStorage
    const isFilterVisible = localStorage.getItem('filter-visible') === 'true';

    if (isFilterVisible) {
        filterSection.classList.remove('d-none');
        toggleButton.textContent = 'Skrýt filtry';
    } else {
        filterSection.classList.add('d-none');
        toggleButton.textContent = 'Filtrovat transakce';
    }

    toggleButton.addEventListener('click', function () {
        if (filterSection.classList.contains('d-none')) {
            filterSection.classList.remove('d-none');
            toggleButton.textContent = 'Skrýt filtry';
            localStorage.setItem('filter-visible', 'true');
        } else {
            filterSection.classList.add('d-none');
            toggleButton.textContent = 'Filtrovat transakce';
            localStorage.setItem('filter-visible', 'false');
        }
    });
});
