// Event listener na odeslání formuláře
document.getElementById('bulk-action-form').addEventListener('submit', function(event) {
    updateSelectedTransactionsInput();  // Aktualizace skrytého pole s transakcemi

    console.log('Hodnota skrytého pole před odesláním:', document.getElementById('selected-transactions').value);

    // Odstraníme atribut "name" z checkboxů, aby nebyly součástí odeslaných dat
    document.querySelectorAll('.transaction-checkbox').forEach(function(checkbox) {
        checkbox.removeAttribute('name');
    });

    // Odeslání formuláře přes AJAX, aby bylo možné čekat na odpověď
    event.preventDefault();  // Zabraňte klasickému odeslání formuláře

    const formData = new FormData(this);  // Vytvoříme FormData objekt z formuláře
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;  // Získáme CSRF token

    const activeButton = document.activeElement;  // Získáme aktivní tlačítko
    formData.set('action', activeButton.value);  // Aktualizujeme hodnotu action v FormData

    // Použijte explicitní URL pro odesílání požadavku
    const actionUrl = this.getAttribute('action');

    fetch(actionUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken,
        },
    })
    .then(response => {
        if (response.ok) {
            return response.json();  // Předpokládáme, že dostaneme JSON odpověď
        } else {
            throw new Error('Nastala chyba při zpracování akce.');
        }
    })
    .then(data => {
        // Po úspěšné akci vymažeme vybrané transakce z localStorage a checkboxů
        clearSelectedTransactions()

        // Přesměrujeme uživatele zpět na aktuální stránku s filtrem a stránkováním
        window.location.href = data.redirect_url || window.location.href;
    })
    .catch(error => {
        console.error('Chyba při odesílání formuláře:', error);
    });
});

// Event listener pro kliknutí na tlačítko "Export do CSV"
document.getElementById('export-csv-btn').addEventListener('click', function() {
    updateSelectedTransactionsInput();  // Aktualizace skrytého pole s vybranými transakcemi
    console.log('Hodnota skrytého pole před odesláním:', document.getElementById('selected-transactions').value);

    // Odstraníme atribut "name" ze všech checkboxů
    document.querySelectorAll('.transaction-checkbox').forEach(function(checkbox) {
        checkbox.removeAttribute('name');
    });

    const formData = new FormData(document.getElementById('bulk-action-form'));
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    formData.set('action', 'export_csv');  // Specifikujeme, že jde o export CSV

    // Poslání přes AJAX
    fetch("{% url 'bulk-transaction-action' %}", {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken,
        },
    })
    .then(response => {
        if (response.headers.get('content-type').includes('application/json')) {
            return response.json();  // Očekáváme JSON odpověď (přesměrování)
        } else {
            return response.blob();  // Očekáváme, že backend vrátí CSV (blob)
        }
    })
    .then(data => {
        if (data.redirect_url) {
            // Pokud je vrácen JSON s URL, přesměrujeme uživatele
            window.location.href = data.redirect_url;
        } else {
            // Pokud je vráceno CSV, stáhneme soubor
            const url = window.URL.createObjectURL(data);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'transactions.csv';  // Jméno souboru
            document.body.appendChild(a);
            a.click();
            a.remove();
        }
    })
    .catch(error => {
        console.error('Chyba při odesílání exportu do CSV:', error);
    });
});

// Uchovávej seznam vybraných transakcí pomocí localStorage
let selectedTransactions = new Set(JSON.parse(localStorage.getItem('selectedTransactions')) || []);
let selectAll = false;

// Funkce pro aktualizaci skrytého pole s vybranými transakcemi před odesláním formuláře
function updateSelectedTransactionsInput() {
    document.getElementById('selected-transactions').value = Array.from(selectedTransactions).join(',');
    console.log('Aktuální vybrané transakce:', Array.from(selectedTransactions));
}

// Funkce pro ukládání seznamu vybraných transakcí do localStorage
function saveSelectedTransactions() {
    localStorage.setItem('selectedTransactions', JSON.stringify(Array.from(selectedTransactions)));
}

// Funkce pro zaškrtnutí/odškrtnutí všech checkboxů na aktuální stránce
function checkAllVisibleCheckboxes(checked) {
    document.querySelectorAll('.transaction-checkbox').forEach(function(checkbox) {
        checkbox.checked = checked;
        if (checked) {
            selectedTransactions.add(checkbox.value.toString());  // Ukládáme jako řetězce
        } else {
            selectedTransactions.delete(checkbox.value.toString());
        }
    });
    updateSelectedTransactionsInput();
    saveSelectedTransactions();
}

// Při kliknutí na checkbox "vybrat vše"
document.getElementById('select-all').addEventListener('click', function() {
    selectAll = this.checked;
    document.getElementById('select-all-input').value = selectAll ? 'true' : 'false';

    if (selectAll) {
        // Při zaškrtnutí "vybrat vše" uložíme všechny transakce z aktuálního filtru
        fetchAllTransactionIds().then(allTransactionIds => {
            allTransactionIds.forEach(id => selectedTransactions.add(id.toString()));  // Ukládáme jako řetězce
            updateSelectedTransactionsInput();
            saveSelectedTransactions();

            // Po získání všech ID aktualizujeme vizuálně všechny checkboxy
            checkAllVisibleCheckboxes(true);  // Zajistí zaškrtnutí všech checkboxů na aktuální stránce
        });
    } else {
        // Pokud odškrtneme "vybrat vše", vymažeme všechny vybrané transakce
        clearSelectedTransactions()
    }
});

// Přidání/odebrání transakcí při výběru checkboxů
document.querySelectorAll('.transaction-checkbox').forEach(function(checkbox) {
    checkbox.addEventListener('change', function() {
        const id = this.value.toString();  // Pracujeme s řetězci
        if (this.checked) {
            selectedTransactions.add(id);
        } else {
            selectedTransactions.delete(id);
        }
        updateSelectedTransactionsInput();
        saveSelectedTransactions();
    });

    // Pokud už je transakce ve vybraných, automaticky ji zaškrtneme
    if (selectedTransactions.has(checkbox.value.toString())) {
        checkbox.checked = true;
    }
});

// Funkce pro vymazání vybraných transakcí z localStorage
function clearSelectedTransactions() {
    selectedTransactions.clear();
    updateSelectedTransactionsInput();
    saveSelectedTransactions();
    checkAllVisibleCheckboxes(false);
}

// Event listener pro načtení stránky
window.addEventListener('DOMContentLoaded', function () {
    const selectedValues = JSON.parse(localStorage.getItem('selectedTransactions')) || [];
    selectedValues.forEach(function(value) {
        selectedTransactions.add(value.toString());  // Zajišťujeme, že všechna ID jsou řetězce
    });

    // Při načtení stránky zaškrtni všechny checkboxy, které jsou již vybrané
    document.querySelectorAll('.transaction-checkbox').forEach(function(checkbox) {
        if (selectedTransactions.has(checkbox.value.toString())) {
            checkbox.checked = true;
        }
    });

    updateSelectedTransactionsInput();
});

// Funkce pro získání všech transakčních ID z aktuálního filtru (přes AJAX)
function fetchAllTransactionIds() {
    return fetch(window.location.href, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => data.transaction_ids.map(id => id.toString()));  // Konvertujeme všechna ID na řetězce
}

//Čistič filtrů v localStorage
document.addEventListener('DOMContentLoaded', function () {
    const urlParams = new URLSearchParams(window.location.search);
    const hasFilters = urlParams.toString().includes('amount_min') ||
                       urlParams.toString().includes('amount_max') ||
                       urlParams.toString().includes('type') ||
                       urlParams.toString().includes('datestamp__gte') ||
                       urlParams.toString().includes('datestamp__lte') ||
                       urlParams.toString().includes('category') ||
                       urlParams.toString().includes('tags') ||
                       urlParams.toString().includes('description');

    if (!hasFilters) {
        localStorage.removeItem('filter-visible'); // Čistíme stav filtru, pokud nejsou aplikovány žádné filtry
    }
});