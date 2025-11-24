from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Usuario, Medico, Paciente, Agendamento, Medicamento
from faker import Faker
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados fictícios para teste'

    def handle(self, *args, **kwargs):
        fake = Faker('pt_BR') # Gera dados em Português do Brasil
        
        self.stdout.write(self.style.WARNING('Iniciando o processo de população...'))

        # 1. LIMPEZA (Opcional: descomente se quiser limpar antes de criar)
        # Agendamento.objects.all().delete()
        # Paciente.objects.all().delete()
        # Medico.objects.all().delete()
        # Usuario.objects.filter(is_superuser=False).delete()

        # 2. CRIAR MEDICAMENTOS
        medicamentos_lista = ['Dipirona', 'Paracetamol', 'Ibuprofeno', 'Amoxicilina', 'Dorflex', 'Omeprazol', 'Simeticona', 'Torsilax']
        for med in medicamentos_lista:
            Medicamento.objects.get_or_create(nome=med, defaults={'generico': med})
        self.stdout.write(self.style.SUCCESS(f'{len(medicamentos_lista)} Medicamentos criados.'))

        # 3. CRIAR MÉDICOS (5 Médicos)
        especialidades = ['Fisioterapia Esportiva', 'Ortopedia', 'Pilates', 'Osteopatia', 'Neurologia']
        medicos_objs = []
        
        for i in range(5):
            nome = fake.first_name()
            sobrenome = fake.last_name()
            username = f"dr_{nome.lower()}"
            
            if not Usuario.objects.filter(username=username).exists():
                user = Usuario.objects.create_user(
                    username=username,
                    email=fake.email(),
                    password='123', # Senha padrão para testes
                    first_name=nome,
                    last_name=sobrenome,
                    tipo='MEDICO'
                )
                medico = Medico.objects.create(
                    usuario=user,
                    crm=f"{random.randint(10000, 99999)}-SP",
                    especialidade=random.choice(especialidades)
                )
                medicos_objs.append(medico)
                self.stdout.write(f'Médico criado: Dr. {nome}')

        # 4. CRIAR PACIENTES (20 Pacientes)
        pacientes_objs = []
        for i in range(20):
            nome = fake.first_name()
            sobrenome = fake.last_name()
            cpf_raw = fake.cpf().replace('.', '').replace('-', '') # Remove pontos
            
            if not Usuario.objects.filter(username=cpf_raw).exists():
                user = Usuario.objects.create_user(
                    username=cpf_raw, # Login é o CPF
                    email=fake.email(),
                    password='123',
                    first_name=nome,
                    last_name=sobrenome,
                    tipo='PACIENTE'
                )
                paciente = Paciente.objects.create(
                    usuario=user,
                    cpf=cpf_raw,
                    data_nascimento=fake.date_of_birth(minimum_age=18, maximum_age=90),
                    telefone=fake.phone_number(),
                    sexo=random.choice(['M', 'F'])
                )
                pacientes_objs.append(paciente)
        
        self.stdout.write(self.style.SUCCESS(f'{len(pacientes_objs)} Pacientes criados.'))

        # 5. CRIAR AGENDAMENTOS (Histórico e Futuro)
        # Se não tiver médicos ou pacientes novos, tenta pegar os existentes
        if not medicos_objs:
            medicos_objs = list(Medico.objects.all())
        if not pacientes_objs:
            pacientes_objs = list(Paciente.objects.all())

        if medicos_objs and pacientes_objs:
            for _ in range(100): # Cria 100 consultas
                medico = random.choice(medicos_objs)
                paciente = random.choice(pacientes_objs)
                
                # Data aleatória entre 30 dias atrás e 30 dias a frente
                dias = random.randint(-30, 30)
                hora = random.randint(8, 17)
                data_hora = timezone.now() + timedelta(days=dias)
                data_hora = data_hora.replace(hour=hora, minute=0, second=0)

                # Define status baseado na data
                status = 'AGENDADO'
                pago = False
                avaliacao = None
                
                if dias < 0: # Passado
                    status = 'REALIZADO'
                    pago = random.choice([True, True, False]) # Mais chance de estar pago
                    if pago:
                        avaliacao = random.randint(3, 5) # Nota 3 a 5
                elif dias == 0: # Hoje
                    status = random.choice(['AGENDADO', 'AGUARDANDO'])
                
                # Cria o agendamento
                Agendamento.objects.create(
                    medico=medico,
                    paciente=paciente,
                    data_horario=data_hora,
                    status=status,
                    valor=200.00,
                    pago=pago,
                    avaliacao=avaliacao
                )

            self.stdout.write(self.style.SUCCESS('Agendamentos gerados com sucesso!'))
        else:
            self.stdout.write(self.style.ERROR('Não há médicos ou pacientes suficientes para gerar agendamentos.'))

        self.stdout.write(self.style.SUCCESS('--- PROCESSO CONCLUÍDO! ---'))
        self.stdout.write(self.style.SUCCESS('Login dos Médicos: dr_nome / senha: 123'))
        self.stdout.write(self.style.SUCCESS('Login dos Pacientes: CPF / senha: 123'))