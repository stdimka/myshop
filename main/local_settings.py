# main/local_settings.py

# Настройки для Gmail (или другого SMTP-сервера)
EMAIL_HOST_USER = 'dimkadimko88@gmail.com'  # <- Тут настоящий email
EMAIL_HOST_PASSWORD = 'qvnbtwblsjsphxoa'  # <- Тут настоящий пароль (лучше использовать App Password для Gmail)
SERVER_EMAIL = 'dimkadimko88@gmail.com'      # <- Тоже реальный email, от кого будут приходить ошибки (если DEBUG=False)
DEFAULT_FROM_EMAIL = 'dimkadimko88@gmail.com' # <- От кого будут приходить обычные письма (например, подтверждение регистрации)

# Если у тебя есть SECRET_KEY в settings.py как переменная окружения — тоже можно сюда:
SECRET_KEY = 'django-insecure-@mr9eqs$njns*ewg4emy85416bz=@&b+zh1^qe1y9msyzst-_y'

# Если хочешь использовать другой SITE_URL на проде:
# SITE_URL = 'https://yourrealwebsite.com'

#$token.access eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY1MTQzNzYwLCJpYXQiOjE3NjUxNDM0NjAsImp0aSI6IjU3YTgxNjRmZTRmNDQ2YWQ5OWUxMDM5MzM5ZDhkMWYwIiwidXNlcl9pZCI6IjM3In0.Vbd1WW2fNHzw-4jukSi3ApJQ4k_Ptb-cb6VzUBUL2a4
#$token.refresh eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2NTIyOTg2MCwiaWF0IjoxNzY1MTQzNDYwLCJqdGkiOiI3YjEzNTkzZWMzN2E0OTk1ODc0M2I0YjUxY2I2OGQ5NiIsInVzZXJfaWQiOiIzNyJ9.Dj4PhqkQMg63fAKjTqIeGzQYbShxv8vKSnakdl4cStw

