# BudgetLog

**BudgetLog** je výuková webová aplikace postavená na Django. Umožňuje evidovat transakce typu příjem a výdaj, seskupovat je do samostatných knih, třídit pomocí kategorií a tagů, filtrovat a vyhodnocovat v časových přehledech.

- **GitHub repository:** https://github.com/Hmyzaak/BudgetLog
- **Demonstrační instance:** https://budgetlog.pythonanywhere.com/
- **Jazyk uživatelského rozhraní:** čeština
- **Backend:** Python / Django 5.2.8
- **Databáze:** SQLite (výchozí konfigurace)

> **Rozsah dokumentace:** Tento dokument popisuje aktuální implementaci ve větvi `main`. Nezahrnuje budoucí návrhy. Opakované (recurring) transakce v této verzi implementovány nejsou.

## 1. Koncepce aplikace

Základním organizačním prvkem je **kniha (`Book`)**. Kniha není bankovní účet ani předem definovaný typ finančního produktu. Představuje samostatný pracovní prostor, který si uživatel může určit pro libovolnou oblast evidence – například osobní výdaje, domácnost, cestu nebo jiný oddělený soubor záznamů.

V aktuální implementaci se uvnitř knihy evidují transakce typu **příjem** (`income`) a **výdaj** (`expense`). Každá kniha má vlastní transakce, kategorie a tagy. Uživatel si vybírá aktivní knihu; její ID se ukládá do session a používá se při práci s daty.

## 2. Funkcionalita

### Uživatelské účty

- Registrace pomocí e-mailové adresy a hesla.
- Přihlášení a odhlášení.
- Vlastní uživatelský model `AppUser`, který dědí z `AbstractBaseUser`; přihlašovacím identifikátorem je e-mail.
- Zobrazení profilu, změna hesla a odstranění vlastního účtu.
- Obnovení zapomenutého hesla prostřednictvím e-mailu.
- Administrace přes vestavěnou Django administraci.

Po registraci je uživatel přesměrován do úvodního nastavení knihy.

### Knihy – samostatné pracovní prostory

- Jeden uživatel může vlastnit více knih.
- Uživatel může knihu vytvořit, upravit, odstranit a vybrat jako aktivní.
- Název knihy je jedinečný v rámci jednoho vlastníka.
- Aktivní kniha je uložena v session pod klíčem `current_book_id`.
- Každá kniha má vlastní transakce, kategorie a tagy.
- Při prvotním nastavení si uživatel zvolí název knihy a počáteční kategorie; může zadat i vlastní kategorie.

### Transakce

Transakce obsahuje:

- částku (`DecimalField`, 10 číslic celkem a 2 desetinná místa),
- typ `income` nebo `expense`,
- datum,
- knihu,
- volitelnou kategorii,
- žádný, jeden nebo více tagů,
- volitelný popis.

Uživatel může transakce vytvořit, zobrazit detail, upravit a odstranit. Vlastnost `adjusted_amount` vrací výdaj se záporným znaménkem a příjem s kladným znaménkem; pro výpočty souhrnů se obdobná logika používá v databázových agregacích.

### Kategorie a tagy

- Kategorie i tagy patří vždy do jedné knihy.
- Název kategorie je jedinečný v rámci knihy.
- Název tagu je jedinečný v rámci knihy.
- Kategorie i tag mají název, barvu a volitelný popis.
- Jedna transakce může mít více tagů a jeden tag může být přiřazen více transakcím (vazba M:N).
- Při vytvoření knihy vytvoří Django signál výchozí kategorii **Nezařazeno**.
- Výchozí kategorii nelze odstranit běžným uživatelským rozhraním. Před odstraněním jiné kategorie se její transakce přeřadí do výchozí kategorie.

### Seznam transakcí, filtrování a souhrny

Seznam transakcí nabízí filtrování podle:

- minimální a maximální částky,
- typu transakce,
- data od / do,
- kategorie,
- tagů,
- textu v popisu.

Při výběru více tagů se používá režim `conjoined=True`, tedy transakce musí odpovídat všem zvoleným tagům. Seznam je stránkovaný po 30 položkách. Nad filtrovaným souborem se počítají souhrnné hodnoty, zejména počet transakcí, průměr, maximum, minimum a bilance.

### Hromadné operace

Nad vybranými transakcemi jsou implementovány tyto operace:

- přiřazení tagu,
- odebrání tagu,
- změna kategorie,
- smazání,
- export do CSV,
- přesun do jiné knihy.

Při přesunu transakcí se v cílové knize dohledají nebo vytvoří odpovídající kategorie a tagy. Přesunutá transakce navíc dostane tag **Přesunuto**.

### Dashboard a přehledy

- Dashboard zobrazuje měsíce a roky, ve kterých existují transakce aktivní knihy.
- Měsíční detail nabízí souhrny příjmů, výdajů a bilance a přehled podle kategorií.
- Roční detail nabízí roční souhrny a bilanci kategorií v jednotlivých měsících.
- Grafy jsou vykreslovány na straně prohlížeče pomocí Chart.js.

### Import a export CSV

- Aplikace poskytuje stažení vzorového CSV souboru.
- Import používá středník (`;`) jako oddělovač.
- Detekce kódování využívá knihovnu `chardet`; podporována je i práce se soubory s BOM.
- Názvy sloupců mohou být české nebo anglické: `částka`/`amount`, `datum`/`datestamp`, `typ`/`type`, `kategorie`/`category`, `tagy`/`tags`, `popis`/`description`.
- Povinné sloupce jsou částka, datum, typ, kategorie a tagy. U jednotlivého řádku musí být vyplněna částka, datum, typ a kategorie; tagy mohou být prázdné.
- Podporované typy jsou `income` a `expense`.
- Podporované formáty data jsou `YYYY-MM-DD` a `DD.MM.YYYY`.
- Částka může obsahovat desetinnou tečku nebo čárku; současný parser odmítne zápis, který obsahuje obě.
- Volba `create_missing` umožňuje vytvořit chybějící kategorie a tagy. Neplatné nebo neúplné řádky se přeskočí a uvedou ve výsledném souhrnu.
- Export CSV je dostupný jako jedna z hromadných akcí a exportuje vybrané transakce.

## 3. Datový model

| Model | Význam | Hlavní vztahy |
|---|---|---|
| `AppUser` | Uživatelský účet | Vlastní 0 až N knih |
| `Book` | Samostatný pracovní prostor | Patří jednomu uživateli; obsahuje transakce, kategorie a tagy |
| `Transaction` | Záznam příjmu nebo výdaje | Patří jedné knize; může mít jednu kategorii a více tagů |
| `Category` | Klasifikace transakce | Patří jedné knize; může být přiřazena více transakcím |
| `Tag` | Doplňkové označení transakce | Patří jedné knize; vztah k transakcím je M:N |

Důležité databázové vazby:

- `AppUser 1 — 0..N Book`
- `Book 1 — 0..N Transaction`
- `Book 1 — 0..N Category`
- `Book 1 — 0..N Tag`
- `Category 0..1 — 0..N Transaction`
- `Transaction 0..N — 0..N Tag`

Podrobnější vizuální model je v souboru [`BudgetLog_UML.drawio`](BudgetLog_UML.drawio).

## 4. Technologie

| Oblast | Technologie |
|---|---|
| Jazyk | Python |
| Webový framework | Django 5.2.8 |
| Databáze | SQLite |
| Formuláře | django-crispy-forms, crispy-bootstrap5 |
| Filtrování | django-filter |
| CSV | Python `csv`, chardet |
| Proměnné prostředí | python-dotenv |
| Frontend | Django Templates, HTML, CSS, JavaScript, Bootstrap 5 |
| Grafy | Chart.js |

Přesné verze balíčků jsou definovány v `requirements.txt`. Django 5.2 vyžaduje Python 3.10 nebo novější.

## 5. Struktura projektu

```text
BudgetLog/
├── manage.py
├── requirements.txt
├── README.md
├── budgetlog_project/
│   ├── settings.py             # Konfigurace Django, DB, e-mailu a statických souborů
│   ├── urls.py                 # Kořenové URL
│   ├── asgi.py
│   └── wsgi.py
└── budgetlog/
    ├── models.py               # AppUser, Book, Transaction, Category, Tag
    ├── views.py                # Pohledy a aplikační procesy
    ├── forms.py                # Uživatelské a modelové formuláře
    ├── filters.py              # TransactionFilter
    ├── signals.py              # Automatické vytvoření výchozí kategorie
    ├── apps.py                 # Registrace signálů při startu aplikace
    ├── admin.py                # Django administrace
    ├── urls.py                 # URL aplikace
    ├── migrations/             # Databázové migrace
    ├── management/commands/    # populate_data, delete_data
    ├── templates/              # HTML šablony aplikace
    ├── static/                 # CSS, JavaScript, obrázky, favicon
    └── templatetags/           # Vlastní template tagy a filtry
```

### Odpovědnosti hlavních částí

- **`models.py`** – struktura a vztahy databázových entit.
- **`views.py`** – řízení požadavků, CRUD operace, filtrace, souhrny, CSV import/export a hromadné akce.
- **`forms.py`** – validace a zobrazení formulářů; `TransactionForm` omezuje volitelné kategorie a tagy na aktivní knihu.
- **`filters.py`** – definice filtrů seznamu transakcí.
- **`signals.py`** – vytvoření výchozí kategorie při vzniku knihy a přeřazení transakcí při mazání kategorie.
- **`BookContextMixin`** (ve `views.py`) – načítá aktivní knihu ze session a přidává kontext knihy do pohledů.
- **`TransactionSummaryMixin`** (ve `views.py`) – sdílené agregační výpočty.
- **`templates/` a `static/`** – serverově vykreslované stránky a klientská interakce.

## 6. Lokální instalace a spuštění

Následující postup předpokládá Windows a PowerShell. Pro Linux/macOS jsou alternativní příkazy uvedeny v komentářích.

### 1. Naklonování repository

```bash
git clone https://github.com/Hmyzaak/BudgetLog.git
cd BudgetLog
```

### 2. Vytvoření virtuálního prostředí

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Na Linuxu/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalace závislostí

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Konfigurace prostředí

Projekt načítá proměnné prostředí pomocí `python-dotenv`. Pro lokální vývoj vytvoř soubor `budgetlog_project/.env` a nastav minimálně:

```dotenv
SECRET_KEY=vlastni-tajny-klic
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

Tajný klíč lze vygenerovat například takto:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Hodnoty v `.env` jsou pouze příkladem. Soubor s tajnými údaji nepatří do veřejného repository. V produkčním prostředí nastav `DEBUG=False`, správný `ALLOWED_HOSTS` a vlastní `SECRET_KEY`.

### 5. Migrace a spuštění

```bash
python manage.py migrate
python manage.py runserver
```

Aplikace bude standardně dostupná na http://127.0.0.1:8000/.

Při prvním přihlášení nově zaregistrovaného uživatele aplikace nabídne vytvoření knihy a počátečních kategorií.

## 7. Konfigurace a nasazení

- Výchozí databáze je SQLite v souboru `db.sqlite3` v kořenovém adresáři projektu.
- Nastavení aplikace je v `budgetlog_project/settings.py`.
- E-mailové připojení se nastavuje pomocí proměnných prostředí `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER` a `EMAIL_HOST_PASSWORD`.
- `STATIC_ROOT` a `MEDIA_ROOT` jsou v aktuální konfiguraci nastaveny na absolutní cesty odpovídající nasazení na PythonAnywhere. Při lokálním nebo jiném nasazení je zkontroluj a podle potřeby uprav.
- Veřejná demonstrační instance je provozována na PythonAnywhere: https://budgetlog.pythonanywhere.com/.

Tento README není detailním deployment manuálem pro PythonAnywhere; produkční konfigurace, databáze a tajné údaje se spravují odděleně od lokálního vývoje.

## 8. Pomocné management commands

### Generování testovacích dat

```bash
python manage.py populate_data
```

Příkaz si vyžádá ID knihy a vytvoří v ní 5 kategorií, 9 tagů a 1 000 náhodných transakcí s daty z posledních přibližně 1 000 dnů.

### Mazání testovacích dat

```bash
python manage.py delete_data
```

Příkaz si vyžádá ID knihy a odstraní její transakce, kategorie a tagy. **Jde o destruktivní operaci.** Před spuštěním ověř databázi a ID knihy; nepoužívej ji nad daty, která chceš zachovat.

## 9. Testování a aktuální technická omezení

Testy lze spouštět příkazem:

```bash
python manage.py test
```

Aktuální `budgetlog/tests.py` je pozůstatek starší implementace: obsahuje odkazy na odstraněný model `Account` a názvy URL, které neodpovídají současnému routování. Funkce testů jsou navíc definovány mimo testovací třídu. Soubor proto nelze považovat za funkční a úplnou automatizovanou testovací sadu; před spoléháním na testovací výstup je potřeba jej přepracovat.

### Poznámky k přístupovým kontrolám

Datový model odděluje data podle knih a většina běžných pohledů pracuje s aktivní knihou. Při čtení aktuální implementace je však vhodné samostatně prověřit autorizaci ve dvou místech:

- `BulkTransactionActionView.post()` načítá vybrané transakce podle ID zaslaných klientem (`id__in`) bez dodatečného omezení querysetu na aktivní knihu.
- `BookDeleteView` používá obecný mazací pohled; na rozdíl od `BookUpdateView` zde není zřejmé omezení querysetu na vlastníka knihy.

Jde o kandidáty na bezpečnostní opravu a regresní testy. Dokumentace proto neprezentuje oddělení knih jako plně ověřenou bezpečnostní hranici.

## 10. Rozsah aktuální verze

Aktuální verze obsahuje správu uživatelů, knih, transakcí, kategorií a tagů, filtrování, souhrny, přehledy, CSV import/export a hromadné operace. **Opakované transakce nejsou implementovány** a nejsou součástí přiložených UML diagramů.

## Autor

JaVoj ([GitHub: @Hmyzaak](https://github.com/Hmyzaak)).
