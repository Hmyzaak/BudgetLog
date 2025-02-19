# Django importy
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# Create your models here.
class UserManager(BaseUserManager):
    """Správa uživatelů a administrátorů."""

    def create_user(self, email, password=None):
        """Vytvoří a uloží uživatele s daným e-mailem a heslem."""
        if not email:
            raise ValueError("E-mail musí být zadán.")
        if not password:
            raise ValueError("Heslo musí být zadáno.")

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Vytvoří a uloří superuživatele s daným e-maliem a heslem."""
        user = self.create_user(email, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class AppUser(AbstractBaseUser):
    """Model reprezentující uživatele."""

    email = models.EmailField(max_length=100, unique=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Uživatel"
        verbose_name_plural = "Uživatelé"

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        """Textová reprezentace uživatele jako jeho mailu."""
        return f"email: {self.email}"

    def save(self, *args, **kwargs):
        """Před uložením převede e-mail na malá písmena."""
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    @property
    def is_staff(self):
        """Vrací True, pokud je uživatel administrátor."""
        return self.is_admin

    def has_perm(self, perm, obj=None):
        """Vrací True, pokud má uživatel povolení (= je aktivován)."""
        return self.is_active

    def has_module_perms(self, app_label):
        """Vrací True, pokud má uživatel povolení pro daný modul."""
        return self.is_active


class Book(models.Model):
    """Model reprezentující knihu záznamů pro uživatele."""

    name = models.CharField(max_length=100, verbose_name="Jméno knihy", help_text="Uveďte jméno knihy")
    description = models.TextField(null=True, blank=True, verbose_name="Popis knihy",
                                   help_text="Popis knihy (volitelný)")
    owner = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='books',
                              verbose_name="Majitel", help_text="Majitel knihy")

    class Meta:
        verbose_name = "Kniha"
        verbose_name_plural = "Knihy"
        constraints = [
            models.UniqueConstraint(fields=['name', 'owner'], name='unique_book_name_owner')
        ]

    object_plural_genitiv = "knih"
    object_singular_akluzativ = "knihu"

    def __str__(self):
        """Textová reprezentace modelu Book."""
        return f"{self.name} (Majitel: {self.owner.email})"


class Category(models.Model):
    """Model pro kategorizaci transakcí."""

    name = models.CharField(max_length=200, verbose_name="Název",
                            help_text="Uveď název kategorie pro transakce (např. potraviny, doprava, zábava)")
    color = models.CharField(max_length=7, default='#000000', verbose_name="Barva kategorie",
                             help_text="Barva kategorie pro zobrazení v grafu ročního přehledu")
    description = models.TextField(null=True, blank=True, verbose_name="Popis",
                                   help_text="Detailnější popis kategorie pro transakce (volitelný)")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Kniha", related_name='categories',
                             help_text="Vyberte knihu, ke které patří tato kategorie")
    is_default = models.BooleanField(default=False)  # Přidání příznaku pro výchozí kategorii, hodnota True umožní nesmazatelnost

    class Meta:
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorie"
        constraints = [
            models.UniqueConstraint(fields=['name', 'book'], name='unique_category_name_book')
        ]

    object_plural_genitiv = "kategorií"
    object_singular_akluzativ = "kategorii"

    def __str__(self):
        """Textová reprezentace modelu Category."""
        return self.name


class Tag(models.Model):
    """Model reprezentující tag, který může být přiřazen k více transakcím."""

    name = models.CharField(max_length=25, verbose_name="Název tagu",
                            help_text="Uveď název tagu.")
    color = models.CharField(max_length=7, default='#000000', verbose_name="Barva tagu",
                             help_text="Barva tagu.")
    description = models.TextField(null=True, blank=True, verbose_name="Popis tagu",
                                   help_text="Popis tagu (volitelný).")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Kniha",
                             help_text="Vyberte knihu, ke které patří tento tag")

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tagy"
        constraints = [
            models.UniqueConstraint(fields=['name', 'book'], name='unique_tag_name_book')
        ]

    object_plural_genitiv = "tagů"
    object_singular_akluzativ = "tag"

    def __str__(self):
        return self.name


class Transaction(models.Model):
    """Model reprezentující záznam o finanční transakci."""

    TYPE_CHOICES = (
        ('income', 'Příjem'),
        ('expense', 'Výdaj')
    )
    # Definuje tuple pro typ transakce, který voláme níže

    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Kniha",
                             help_text="Vyberte knihu, ke které patří tato transakce")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Částka",
                                 help_text="Uveďte částku transakce v [CZK].")
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL, verbose_name="Kategorie",
                                 help_text="Vyberte kategorii pro tuto transakci.")  # on_delete=models.SET_NULL
    # nastaví hodnotu na NULL při smazání související kategorie, což zajistí, že transakce nebude smazána.
    datestamp = models.DateField(default=timezone.now, verbose_name="Datum",
                                 help_text="Datum provedení transakce.")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Tagy",
                                  related_name='transactions', help_text="Vyberte tagy pro tuto transakci.")
    description = models.TextField(null=True, blank=True, verbose_name="Popis",
                                   help_text="Zadejte detailnější popis transakce (volitelný).")
    type = models.CharField(max_length=7, choices=TYPE_CHOICES, default='expense', verbose_name="Typ",
                            help_text="Zvolte, zda je tato transakce výdaj nebo příjem.")

    class Meta:
        verbose_name = "Transakce"
        verbose_name_plural = "Transakce"

    object_plural_genitiv = "transakcí"
    object_singular_akluzativ = "transakci"

    def display_tags(self, transaction):
        return ', '.join(tag.name for tag in transaction.tags.all())
    display_tags.short_description = 'Tagy'

    def __str__(self):
        """Textová reprezentace modelu pro transakci."""
        type_display = dict(self.TYPE_CHOICES).get(self.type, self.type)
        return f"{type_display}: {self.adjusted_amount} CZK {self.datestamp}"

    @property
    def adjusted_amount(self):
        """Vrátí částku s upraveným znaménkem podle typu transakce (výdaj bude záporný)."""
        if self.type == 'expense':
            return -self.amount
        return self.amount
    """
    Django neumožňuje použít adjusted_amount přímo v anotacích a agregacích, protože adjusted_amount je vlastnost (
    property) modelu a ne skutečné pole v databázi. Pokud chceme filtrovat nebo agregovat ve views podle upravených 
    částek, musíme to udělat pomocí amount a přizpůsobit SQL dotaz.
    """
