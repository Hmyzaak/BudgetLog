# BudgetLog

**BudgetLog** je webová aplikace pro osobní evidenci příjmů a výdajů. Umožňuje rozdělit záznamy do samostatných finančních knih, kategorizovat transakce, označovat je tagy, filtrovat je a zobrazovat souhrny za vybraná období.

- **Repository:** https://github.com/Hmyzaak/BudgetLog
- **Testovací instance:** https://budgetlog.pythonanywhere.com/ (dostupnost a aktuální stav instance je potřeba ověřit)
- **Jazyk uživatelského rozhraní:** čeština
- **Framework:** Django 5.2.8

> **Rozsah této dokumentace:** Popis odpovídá zdrojovému kódu ve větvi `main` při přípravě tohoto souboru. Opakované/recurring transakce v této verzi nejsou implementovány.

## Funkcionalita

### Uživatelské účty

- Registrace a přihlašování pomocí e-mailové adresy a hesla.
- Odhlášení.
- Zobrazení profilu, změna hesla a odstranění účtu.
- Obnovení zapomenutého hesla prostřednictvím e-mailu.
- Vlastní uživatelský model `AppUser`; e-mail slouží jako přihlašovací identifikátor.

### Finanční knihy

- Jeden uživatel může vlastnit více knih.
- Kniha obsahuje vlastní transakce, kategorie a tagy.
- Název knihy musí být v rámci jednoho uživatele jedinečný.
- Uživatel si vybírá aktivní knihu; její identifikátor se ukládá do session.
- Přístup k datům se omezuje na knihy přihlášeného uživatele.

Při vytvoření knihy se prostřednictvím Django signálu vytvoří výchozí kategorie **Nezařazeno**. Tuto výchozí kategorii nelze odstranit přes běžné uživatelské rozhraní. Při odstranění jiné kategorie se její transakce převádějí do výchozí kategorie.

### Transakce

Transakce obsahuje:

- částku (desetinné číslo, dvě desetinná místa),
- typ: příjem (`income`) nebo výdaj (`expense`),
- datum,
- kategorii,
- žádný, jeden nebo více tagů,
- volitelný popis,
- příslušnou knihu.

Uživatel může transakce vytvářet, zobrazovat, upravovat a mazat. Při výpočtu bilance se příjem započítává kladně a výdaj záporně podle hodnoty pole `type`; běžným vstupem je kladná částka.

### Kategorie a tagy

- Kategorie i tagy patří vždy do konkrétní knihy.
- Název kategorie je jedinečný v rámci knihy.
- Název tagu je jedinečný v rámci knihy.
- Kategorie i tagy mají název, barvu a volitelný popis.
- Jedna transakce může mít více tagů; stejný tag lze přiřadit více transakcím.

### Filtrování, souhrny a hromadné operace

Seznam transakcí lze filtrovat podle:

- minimální a maximální částky,
- typu transakce,
- počátečního a koncového data,
- kategorie,
- tagů,
- textu v popisu.

Seznam je stránkovaný (30 položek na stránku). Nad filtrovanou množinou se zobrazují souhrny: počet transakcí, průměrná, nejvyšší a nejnižší částka a bilance.

Pro vybrané transakce jsou dostupné hromadné operace:

- přiřazení tagu,
- odebrání tagu,
- změna kategorie,
- smazání,
- export do CSV,
- přesun do jiné knihy.

### Přehledy a grafy

- Dashboard nabízí přehled dostupných roků a měsíců.
- Měsíční detail zobrazuje souhrn příjmů, výdajů a bilance a přehled podle kategorií.
- Roční detail zobrazuje roční souhrny a bilanci podle kategorií a měsíců.
- Grafy jsou vykreslovány pomocí Chart.js.

### Import a export CSV

- Aplikace umožňuje stáhnout vzorový CSV soubor.
- Importované sloupce mohou používat české nebo anglické názvy: `částka`/`amount`, `datum`/`datestamp`, `typ`/`type`, `kategorie`/`category`, `tagy`/`tags`, `popis`/`description`.
- Import se pokouší rozpoznat kódování souboru.
- Výchozím oddělovačem CSV je středník (`;`).
- Podporované typy jsou `income` a `expense`.
- Datum je podporováno ve formátu `YYYY-MM-DD` nebo `DD.MM.YYYY`.
- Částku lze zadat s desetinnou tečkou nebo čárkou.
- Volba importu umožňuje vytvořit chybějící kategorie a tagy; problematické řádky se přeskočí a vypíší se v souhrnu.
- Export do CSV je součástí hromadných akcí nad vybranými transakcemi.

## Technologie

| Oblast | Použitá technologie |
|---|---|
| Jazyk | Python |
| Backend | Django 5.2.8 |
| Databáze ve výchozí konfiguraci | SQLite |
| Formuláře | django-crispy-forms, crispy-bootstrap5 |
| Filtrování | django-filter |
| Detekce kódování CSV | chardet |
| Načítání proměnných prostředí | python-dotenv |
| Frontend | Django Templates, HTML, CSS, JavaScript, Bootstrap 5 |
| Grafy | Chart.js (načítá se z CDN) |

Přesné verze Python balíčků jsou uvedeny v `requirements.txt`. Django 5.2 vyžaduje Python 3.10 nebo novější.

## Struktura projektu

Základní odpovědnosti hlavních částí projektu:

```text
BudgetLog/
├── manage.py
├── requirements.txt
├── README.md
├── budgetlog_project/
│   ├── settings.py       # Konfigurace Django, databáze, e-mailu a statických souborů
│   ├── urls.py           # Kořenové URL projektu
│   ├── asgi.py
│   └── wsgi.py
└── budgetlog/
    ├── models.py         # AppUser, Book, Transaction, Category, Tag
    ├── views.py          # Zpracování požadavků a aplikační procesy
    ├── forms.py          # Formuláře
    ├── filters.py        # Filtry transakcí
    ├── signals.py        # Automatické akce při změně modelů
    ├── admin.py          # Konfigurace Django administrace
    ├── urls.py           # URL aplikace
    ├── management/commands/  # Pomocné Django management commands
    ├── migrations/       # Databázové migrace
    ├── templates/        # HTML šablony
    ├── static/           # CSS, JavaScript, obrázky a favicon
    └── templatetags/     # Vlastní template filtry a tagy
```

### Hlavní doménové vztahy

- `AppUser` vlastní jednu nebo více `Book`.
- `Book` vlastní transakce, kategorie a tagy.
- `Transaction` patří právě do jedné knihy.
- `Transaction` může mít jednu kategorii (nebo žádnou, protože pole je nullable).
- `Transaction` může mít více tagů a tag může být přiřazen více transakcím.

## Lokální instalace a spuštění

Následující kroky předpokládají lokální vývojové prostředí a SQLite.

### 1. Naklonování repository

```bash
git clone https://github.com/Hmyzaak/BudgetLog.git
cd BudgetLog
```

### 2. Vytvoření virtuálního prostředí

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

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

Nastavení čte proměnné prostředí prostřednictvím `python-dotenv`. Vytvoř lokální soubor `budgetlog_project/.env` a nastav alespoň vlastní tajný klíč a povolené hostitele:

```dotenv
SECRET_KEY=sem_vloz_vlastni_tajny_klic
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# SMTP je potřeba pro odesílání e-mailů, například při obnově hesla.
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

Tajný klíč vytvoříš například příkazem:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Soubor `.env` ani produkční tajné údaje neukládej do Git repository. Pro produkční prostředí nastav `DEBUG=False` a správnou hodnotu `ALLOWED_HOSTS`.

### 5. Migrace databáze

```bash
python manage.py migrate
```

### 6. Spuštění vývojového serveru

```bash
python manage.py runserver
```

Aplikace bude standardně dostupná na http://127.0.0.1:8000/.

Po registraci uživatelského účtu aplikace provede uživatele vytvořením první knihy a výběrem počátečních kategorií.

## Konfigurace a nasazení

- Výchozí konfigurace používá SQLite databázi `db.sqlite3` v kořenovém adresáři projektu.
- Produkční konfigurace na PythonAnywhere se musí lišit od lokální vývojové konfigurace zejména cestami pro statické a mediální soubory, proměnnými prostředí a nastavením povolených hostitelů.
- V aktuálním `settings.py` jsou `STATIC_ROOT` a `MEDIA_ROOT` nastaveny absolutními cestami pro konkrétní nasazení. Před nasazením do jiného prostředí je nutné tyto cesty upravit.
- Přihlašovací údaje SMTP jsou konfigurovány přes proměnné prostředí.

Tento README není kompletním návodem pro nasazení na PythonAnywhere; pro něj je vhodné udržovat samostatný deployment postup.

## Pomocné management commands

V aplikaci jsou také dva příkazy pro práci s testovacími daty:

- `python manage.py populate_data` – interaktivně si vyžádá ID knihy a vytvoří v ní testovací kategorie, tagy a 1 000 náhodných transakcí.
- `python manage.py delete_data` – interaktivně si vyžádá ID knihy a maže její transakce, kategorie a tagy.

> **Varování:** `delete_data` je destruktivní příkaz. Nespouštěj jej nad produkčními daty. Před použitím kteréhokoli příkazu si ověř vybranou databázi a ID knihy.

## Testování

Spuštění Django testů:

```bash
python manage.py test
```

**Poznámka k aktuálnímu stavu:** Soubor `budgetlog/tests.py` v repository obsahuje starší/neúplný testovací kód a odkazy na model `Account`, který v aktuálním datovém modelu není. Automatizované testy je proto potřeba nejprve aktualizovat a ověřit; tento příkaz zatím nepovažuj za potvrzení, že je pokrytí testy kompletní.

## Aktuální omezení a stav vývoje

- Opakované (recurring) transakce nejsou v aktuální verzi implementovány.
- Testovací sada potřebuje aktualizaci podle současných modelů a procesů.
- Licence není v repository jednoznačně uvedena. Dokud nebude přidán soubor `LICENSE` a zvolena licence, nepředpokládej, že je kód uvolněn pod konkrétní open-source licencí.

## Licence

Licence zatím není specifikována. Před veřejným šířením nebo opětovným použitím kódu je potřeba doplnit odpovídající soubor `LICENSE` a informaci do této sekce.

## Autor

JaVoj (GitHub: [@Hmyzaak](https://github.com/Hmyzaak)).
