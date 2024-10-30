#answer:---
# Yes, Django signals run in the same thread as the caller. 
# You can check this by comparing the thread IDs of the caller and the signal handler.
import os
import django
from django.conf import settings
from django.db import models, connection
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import connection
import threading
import time

DB_PATH = 'test_db.sqlite3'

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': DB_PATH,
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


class Order(models.Model):
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        app_label = 'test_app'

@receiver(post_save, sender=Order)
def order_signal_handler(sender, instance, created, **kwargs):
    current_thread = threading.current_thread()
    print(f"Signal running in thread: {current_thread.name}")
    time.sleep(1)  

def create_tables():
    with connection.cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_app_order (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total DECIMAL(10, 2) NOT NULL
            )
        ''')

def create_order():
    
    from django.db import connection
    connection.close()
    
    current_thread = threading.current_thread()
    print(f"Creating order in thread: {current_thread.name}")
    Order.objects.create(total=99.99)
    print(f"Order created in thread: {current_thread.name}")
    
    
    connection.close()

def main():
    
    create_tables()
    
    print("\nTesting main thread:")
    create_order()
    
    print("\nTesting separate thread:")
    thread = threading.Thread(target=create_order, name="CustomThread")
    thread.start()
    thread.join()
    
    connection.close()
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

if __name__ == "__main__":
    main()