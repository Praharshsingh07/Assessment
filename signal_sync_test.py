#answer:----By default, Django signals are executed synchronously. 
# This means that the signal handler will complete its execution before the caller function proceeds.
import os
import django
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import AppConfig
from django.db import connection
from datetime import datetime
import time

# Configure Django settings first
if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
        USE_TZ=False,
        MIDDLEWARE=[],
    )
    django.setup()

class TestAppConfig(AppConfig):
    name = 'test_app'
    label = 'test_app'

class UserProfile(models.Model):
    name = models.CharField(max_length=100)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'test_app'

@receiver(post_save, sender=UserProfile)
def slow_signal_handler(sender, instance, created, **kwargs):
    time.sleep(2) 
    print(f"Signal processed at: {datetime.now()}")

def create_tables():
    with connection.cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_app_userprofile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                last_updated DATETIME NOT NULL
            )
        ''')

def main():
    create_tables()
    start_time = datetime.now()
    print(f"Creating user at: {start_time}")
    
    user = UserProfile.objects.create(name="Test User")
    
    end_time = datetime.now()
    print(f"User created at: {end_time}")
    print("This line executes after signal completion")
    print(f"Total time taken: {end_time - start_time}")

if __name__ == "__main__":
    main()