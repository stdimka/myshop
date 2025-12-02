# main/local_settings.py

# Настройки для Gmail (или другого SMTP-сервера)
EMAIL_HOST_USER = 'dimkadimko88@gmail.com'  # <- Тут настоящий email
EMAIL_HOST_PASSWORD = 'qvnbtwblsjsphxoa'  # <- Тут настоящий пароль (лучше использовать App Password для Gmail)
SERVER_EMAIL = 'dimkadimko88@gmail.com'      # <- Тоже реальный email, от кого будут приходить ошибки (если DEBUG=False)
DEFAULT_FROM_EMAIL = 'dimkadimko88@gmail.com' # <- От кого будут приходить обычные письма (например, подтверждение регистрации)

# Если у тебя есть SECRET_KEY в settings.py как переменная окружения — тоже можно сюда:
# SECRET_KEY = 'your_actual_secret_key_here'

# Если хочешь использовать другой SITE_URL на проде:
# SITE_URL = 'https://yourrealwebsite.com'