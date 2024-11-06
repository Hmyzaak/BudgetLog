// Funkce pro kontrolu URL a vymazání `selectedTransactions`, pokud URL neobsahuje "/transactions/"
function checkAndClearSelectedTransactions() {
    const currentUrl = window.location.href;

    // Kontrola, zda URL obsahuje "/transactions/"
    if (!currentUrl.includes('/transaction')) {
        console.log('URL není transakční stránka, mažu vybrané transakce.');
        localStorage.removeItem('selectedTransactions');  // Vymazání uložených transakcí
    } else {
        console.log('URL je transakční stránka, ponechávám vybrané transakce.');
    }
}

// Spustíme funkci při načtení stránky
window.addEventListener('DOMContentLoaded', function() {
    checkAndClearSelectedTransactions();
});
