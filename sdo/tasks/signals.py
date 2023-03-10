from datetime import date

from django.core.files.storage import default_storage
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import MyAttachment, Task


@receiver(post_save, sender=Task)
def update_attachment(sender, instance, created, **kwargs):
    today = date.today()
    attachments = MyAttachment.objects.filter(created__date=today, task=None)
    for attachment in attachments:
        if not attachment.task:
            attachment.task = instance
            attachment.save()
    attachment_trash = MyAttachment.objects.filter(task=None)
    if attachment_trash:
        for attachment in attachment_trash:
            attachment_path = str(attachment.file)
            attachment.delete()
            default_storage.delete(attachment_path)


@receiver(pre_delete, sender=Task)
def delete_attachments(sender, instance, **kwargs):
    # Get all attachments related to the Task instance being deleted
    attachments = MyAttachment.objects.filter(task=instance)
    # Delete each attachment from the database and storage
    print(attachments)
    for attachment in attachments:
        attachment_path = str(attachment.file)
        attachment.delete()
        default_storage.delete(attachment_path)