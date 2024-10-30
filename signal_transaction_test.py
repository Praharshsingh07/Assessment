#Answer: Yes, Django signals run in the same database transaction as the caller, by default. 
# This can be demonstrated by observing the atomicity of the transaction.
import os
import django
from django.conf import settings
from django.db import models, transaction, connection
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import AppConfig
import time

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

class BankAccount(models.Model):
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        app_label = 'test_app'

class TransactionLog(models.Model):
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        app_label = 'test_app'

@receiver(post_save, sender=BankAccount)
def log_balance_change(sender, instance, created, **kwargs):
    TransactionLog.objects.create(
        account=instance,
        amount=instance.balance
    )

def create_tables():
    with connection.cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_app_bankaccount (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                balance DECIMAL(10, 2) NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_app_transactionlog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount DECIMAL(10, 2) NOT NULL,
                account_id INTEGER NOT NULL REFERENCES test_app_bankaccount(id)
            )
        ''')

def main():
    create_tables()
    
    print("Testing transaction behavior:")
    try:
        with transaction.atomic():
            account = BankAccount.objects.create(balance=1000.00)
            print("Created account and transaction log")
            raise Exception("Forced error")
            
    except Exception as e:
        print("\nChecking if records were rolled back:")
        account_exists = BankAccount.objects.filter(balance=1000.00).exists()
        log_exists = TransactionLog.objects.filter(amount=1000.00).exists()
        
        print(f"Account exists: {account_exists}")
        print(f"Transaction log exists: {log_exists}")
        print("\nIf both are False, it proves they were in the same transaction")

if __name__ == "__main__":
    main()