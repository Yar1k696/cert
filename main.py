from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timezone
import os


# Сертифікат живе 15 днив
# Перевірка на термін дії серттфікату
# 123
def certificate(file: str):
    if not os.path.exists(file):
        raise FileNotFoundError('Файл не знайдено')

    if not os.access(file, os.R_OK):
        raise PermissionError('Немає прав доступа до файлу')

    with open(file, 'rb') as f:
        cert_date = f.read()

        cert = x509.load_pem_x509_certificate(cert_date)

    # Час закинчення сертефіката
    expiry_date = cert.not_valid_after_utc

    # Дізнаємся поточний час
    current_date = datetime.now(timezone.utc)

    # дізнаемся скільки днів залишилося
    days_left = (expiry_date - current_date).days

    if days_left <= 0:
        raise ValueError('Сертифікат згорив')

    elif days_left < 15:
        return f'залишилося {days_left} днів, потрібно оновить'
    else:
        return 'Сертифткат в порядку'


# перевірка на безпеку

def protection_certifi(file):
    if not os.path.exists(file):
        raise FileNotFoundError('Файл не знайденно')
    # чи можна його прочитати
    if not os.access(file, os.R_OK):
        raise PermissionError('Немає прав доступа до файлу')

    with open(file, 'rb') as f:
        cert_reaf = f.read()

        cert = x509.load_pem_x509_certificate(cert_reaf)

        # Витягуємо публичній ллюч
        public_key = cert.public_key()
        # Певірка на розмір ключа
        if isinstance(public_key, rsa.RSAPublicKey):
            if public_key.key_size >= 2048:
                return 'Сертифікат безпечний'
            else:
                raise ValueError('Слабкий захист')
