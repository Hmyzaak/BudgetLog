document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('chartModal');
    const openModalButton = document.getElementById('openModalButton');
    const closeModalButton = document.getElementById('closeModalButton');
    const ctx = document.getElementById('transactionsChart').getContext('2d');
    let transactionsChart = null; // Uchováváme instanci grafu

    // Funkce pro vykreslení grafu
    function renderChart() {
        if (transactionsChart) {
            transactionsChart.destroy(); // Pokud graf již existuje, zničíme ho
        }

        const categories = JSON.parse('{{ categories_json|escapejs }}');
        const months = JSON.parse('{{ months_json|escapejs }}');
        const monthlyData = JSON.parse('{{ monthly_data_json|escapejs }}');

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
                data: monthlyData[category.name],
                backgroundColor: category.color,
            }))
        };

        transactionsChart = new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: true, // Zachová fixní poměr stran
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

    // Aktualizace grafu na základě výběru kategorií
    document.querySelectorAll('input[name="categories"]').forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            const categories = JSON.parse('{{ categories_json|escapejs }}');
            const monthlyData = JSON.parse('{{ monthly_data_json|escapejs }}');
            const selectedCategories = Array.from(document.querySelectorAll('input[name="categories"]:checked'))
                .map(cb => cb.value);

            transactionsChart.data.datasets = categories
                .filter(category => selectedCategories.includes(category.name))
                .map(category => ({
                    label: category.name,
                    data: monthlyData[category.name],
                    backgroundColor: category.color,
                }));
            transactionsChart.update();
        });
    });
});