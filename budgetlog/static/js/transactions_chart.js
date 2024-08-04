document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('transactionsChart').getContext('2d');
    const categories = JSON.parse(document.getElementById('categoriesData').textContent);
    const months = JSON.parse(document.getElementById('monthsData').textContent);
    const monthlyData = JSON.parse(document.getElementById('monthlyData').textContent);

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
        labels: translateMonths(months),  // Translate month names to Czech
        datasets: categories.map(category => ({
            label: category.name,
            data: monthlyData[category.name],
            backgroundColor: category.color,
        }))
    };

    const transactionsChart = new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: {
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
            }
        }
    });

    document.querySelectorAll('input[name="categories"]').forEach(checkbox => {
        checkbox.addEventListener('change', function () {
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
