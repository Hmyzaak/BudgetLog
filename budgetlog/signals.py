from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from .models import *

@receiver(post_save, sender=Book)
def create_default_category_and_account(sender, instance, created, **kwargs):
    if created:
        Category.objects.create(name='Nezařazeno', book=instance, is_default=True)

@receiver(pre_delete, sender=Category)
def assign_default_category(sender, instance, **kwargs):
    default_category = Category.objects.get(book=instance.book, is_default=True)
    Transaction.objects.filter(category=instance).update(category=default_category)
