document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('chartModal');
    const openModalButton = document.getElementById('openModalButton');
    const closeModalButton = document.getElementById('closeModalButton');
    const chartContainer = document.getElementById('chartContainer');
    const ctx = document.getElementById('transactionsChart').getContext('2d');
    let transactionsChart = null; // Uchováváme instanci grafu

    function parseJSONData(attribute) {
        try {
            return JSON.parse(attribute);
        } catch (error) {
            console.error('Chyba při parsování JSON dat:', error);
            return null; // Pokud parsování selže, vrátíme `null`
        }
    }

    // Funkce pro vykreslení grafu
    function renderChart() {
        if (transactionsChart) {
            transactionsChart.destroy(); // Pokud graf již existuje, zničíme ho
        }

        // Získání dat z `data-*` atributů
        const chartDataElement = document.getElementById('chartData');
        // Získání a validace dat
        const categories = parseJSONData(chartDataElement.getAttribute('data-categories'));
        const months = parseJSONData(chartDataElement.getAttribute('data-months'));
        const monthlyData = parseJSONData(chartDataElement.getAttribute('data-monthly-data'));

        if (!categories || !months || !monthlyData) {
            console.error('Data nejsou správně načtena. Graf nebude vykreslen.');
            return; // Ukončíme vykreslení, pokud data nejsou validní
        }

        // Mapping English month names to Czech
        const monthNames = {
            'January': 'Leden',
            'February': 'Únor',
            'March': 'Březen',
            'April': 'Duben',
            'May': 'Květen',
            'June': 'Červen',
            'July': 'Červenec',
            'August': 'Srpen',
            'September': 'Září',
            'October': 'Říjen',
            'November': 'Listopad',
            'December': 'Prosinec'
        };

        // Function to translate months to Czech
        function translateMonths(months) {
            return months.map(month => monthNames[month] || month);
        }

        const chartData = {
            labels: translateMonths(months), // Translate month names to Czech
            datasets: categories.map(category => ({
                label: category.name,
                data: monthlyData[category.name] || [],
                backgroundColor: category.color,
            }))
        };

        transactionsChart = new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false, // Zakazujeme udržování poměru stran
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Měsíce'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Bilance transakcí'
                        }
                    }
                },
                plugins: {
                    zoom: {
                        zoom: {
                            wheel: {
                                enabled: true
                            },
                            pinch: {
                                enabled: true
                            },
                            mode: 'xy'
                        }
                    }
                }
            }
        });
    }

    // Otevření modálního okna
    openModalButton.addEventListener('click', () => {
        modal.style.display = 'block';
        renderChart(); // Vykreslíme graf při otevření modálního okna
    });

    // Zavření modálního okna
    closeModalButton.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Zavření při kliknutí mimo obsah modálu
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Funkce pro drag-to-scroll
    let isDragging = false;
    let startX, scrollLeft;

    chartContainer.addEventListener('mousedown', (e) => {
        isDragging = true;
        chartContainer.style.cursor = 'grabbing';
        startX = e.pageX - chartContainer.offsetLeft;
        scrollLeft = chartContainer.scrollLeft;
    });

    chartContainer.addEventListener('mouseleave', () => {
        isDragging = false;
        chartContainer.style.cursor = 'grab';
    });

    chartContainer.addEventListener('mouseup', () => {
        isDragging = false;
        chartContainer.style.cursor = 'grab';
    });

    chartContainer.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        e.preventDefault();
        const x = e.pageX - chartContainer.offsetLeft;
        const walk = (x - startX) * 1.5; // Rychlost posunu
        chartContainer.scrollLeft = scrollLeft - walk;
    });
});