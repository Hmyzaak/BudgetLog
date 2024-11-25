# Název aplikace
*Krátký popis aplikace, například: Aplikace pro správu financí s možností zaznamenávání transakcí, správy kategorií a analýzy výdajů.*

---

## Obsah
1. [Funkce aplikace](#funkce-aplikace)
2. [Požadavky na prostředí](#požadavky-na-prostředí)
3. [Instalace a spuštění](#instalace-a-spuštění)
4. [Použití](#použití)
5. [Architektura projektu](#architektura-projektu)
6. [Testování](#testování)
7. [Contributing](#contributing)
8. [Licence](#licence)
9. [Autoři a poděkování](#autoři-a-poděkování)
10. [Známé problémy a plánovaný vývoj](#známé-problémy-a-plánovaný-vývoj)

---

## Funkce aplikace
- **Hlavní funkce:**
  - Vytváření a správa finančních transakcí.
  - Přiřazování kategorií a tagů transakcím.
  - Analýza výdajů dle kategorií a časových období.

---

## Požadavky na prostředí
- **Jazyk:** Python 3.10+
- **Framework:** Django 4.x
- **Databáze:** SQLite (nebo jiná podporovaná databáze)
- Další požadavky naleznete v souboru `requirements.txt`.

---

## Instalace a spuštění
1. **Naklonování repozitáře:**
   ```bash
   git clone https://github.com/uzivatel/BudgetLog.git
   cd BudgetLog

2. **Vytvoření a aktivace virtuálního prostředí:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Na Windows: venv\Scripts\activate

3. **Instalace závislostí:**
   ```bash
   pip install -r requirements.txt
   
4. **Migrace databáze:**
    ```bash
    python manage.py migrate

5. **Spuštění aplikace:**
    ```bash
    python manage.py runserver

---

## Použití
- Po spuštění aplikace přejděte na adresu **http://127.0.0.1:8000.**
- Přihlaste se nebo vytvořte nový účet.
- Zaznamenávejte transakce, spravujte kategorie a analyzujte výdaje.

---

## Architektura projektu
- **budgetlog/**: Hlavní aplikace (modely, pohledy, šablony, formuláře).
- **budgetlog_project/**: Nastavení projektu Django.
- **templates/**: HTML šablony.
- **static/**: Statické soubory (CSS, JavaScript).
- **media/**: Uživatelské soubory (např. obrázky).
- **management/commands/**: Vlastní Django příkazy.

---

## Testování
- **Spuštění všech testů:**
    ```bash
    python manage.py test
- Ujistěte se, že jste vytvořili testovací data.

---

## Contributing
Přispěvatelé mohou posílat pull requesty na větev main.
Pro větší změny vytvořte předem issue a projednejte návrhy.

---

## Licence
Uveďte typ licence (např. MIT nebo GPL-3.0) a odkaz na soubor LICENSE.

---

## Autoři a poděkování
**Autor**: JakVoj

---

## Známé problémy a plánovaný vývoj
- **Známé problémy:**
  - Problémy s výkonem při velkém množství dat.
  - Omezené možnosti exportu dat.
- **Plánovaný vývoj:**
  - Úprava grafických souhrnů.
  - Přidání grafického přehledu transakcí.
  - Rozšíření API pro integrace s dalšími aplikacemi.