
from django.db import models
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import pytz

from message_send.tasks import send_post_date

d = [(f'{i[0]}', i) for i in pytz.all_timezones]

class Client(models.Model):
    phone_number = models.CharField(validators=[RegexValidator(r'7\d{10}')], max_length=11)
    operator_code = models.CharField(max_length=30)
    tag = models.CharField(max_length=15)
    time_location = models.CharField(choices=d, max_length=100)





class Message(models.Model):
    date = models.DateField(auto_now_add=True)
    send_status = models.BooleanField(default=False)
    text = models.TextField(max_length=1000)
    client_id = models.ForeignKey(Client, related_name='client_message',on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'Clients: {self.client_id}'

class Mailing(models.Model):

    filters = models.CharField(max_length=1000, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    message_id = models.ForeignKey(Message, related_name='message', on_delete=models.SET_NULL, null=True)

@receiver(signal=post_save, sender=Mailing)
def mailing_was_saved(sender='Модель', instance='Объект модели', created='Bool true or false',  **kwargs):
    text = instance.message_id.text
    if created:
        for user in instance.message_id.client_id.all():
            send_post_date.apply_async(text, user, instance)






