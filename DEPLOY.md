Guia mínimo de deploy (exemplo com Gunicorn + Nginx)

1. Configure variáveis de ambiente: SECRET_KEY, DEBUG=False, DATABASE_URL, ALLOWED_HOSTS.
2. Instale deps em virtualenv e rode `python manage.py migrate` e `collectstatic`.
3. Gunicorn: `gunicorn setup.wsgi:application --workers 3`
4. Nginx: configurar proxy_pass para o Gunicorn socket/porta.
5. Use systemd para rodar Gunicorn como serviço.

Opcional: usar Docker / docker-compose — mover instruções para DOCKER.md.