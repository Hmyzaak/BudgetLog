from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Category, Book, Transaction


@receiver(post_save, sender=Book)
def create_default_category_and_account(sender, instance, created, **kwargs):
    if created:
        Category.objects.create(name='Nezařazeno', book=instance, is_default=True)


@receiver(pre_delete, sender=Category)
def assign_default_category(sender, instance, **kwargs):
    try:
        default_category = Category.objects.get(book=instance.book, is_default=True)
    except Category.DoesNotExist:
        # Zajištění, že existuje výchozí kategorie
        default_category = Category.objects.create(name='Nezařazeno', book=instance.book, is_default=True)

    Transaction.objects.filter(category=instance).update(category=default_category)
