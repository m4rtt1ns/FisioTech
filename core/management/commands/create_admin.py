from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Cria um superusuário automaticamente via Variáveis de Ambiente'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Pega os dados das variáveis do Render (vamos configurar jajá)
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@clinica.com')

        if not username or not password:
            self.stdout.write(self.style.WARNING('Variáveis de admin não encontradas. Pulando criação.'))
            return

        if not User.objects.filter(username=username).exists():
            self.stdout.write(f'Criando superusuário: {username}...')
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS('Superusuário criado com sucesso!'))
        else:
            self.stdout.write('Superusuário já existe.')