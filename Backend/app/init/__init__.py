from decouple import config

settings = dict(
    SMTP_USERNAME=config('SMTP_USERNAME'),
    SMTP_PASSWORD=config('SMTP_PASSWORD'),
    SMTP_SERVER=config('SMTP_SERVER'),
    SMTP_PORT=config('SMTP_PORT')
)
