from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone

class Usuario(AbstractUser):
    """
    Estende o usuário padrão do Django.
    Não precisamos recriar nome, email ou senha, o AbstractUser já tem.
    """
    TIPO_CHOICES = (
        ('MEDICO', 'Médico'),
        ('PACIENTE', 'Paciente'),
        ('RECEPCAO', 'Recepção'),
    )
    tipo = models.CharField(
        'Tipo de Usuário', 
        max_length=10, 
        choices=TIPO_CHOICES, 
        default='PACIENTE'
    )
    tipo = models.CharField('Tipo de Usuário', max_length=10, choices=TIPO_CHOICES, default='PACIENTE')

    foto = models.ImageField('Foto de Perfil', upload_to='perfis/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_tipo_display()})"




class Medico(models.Model):

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='medico')
    crm = models.CharField('CRM', max_length=20, unique=True)
    especialidade = models.CharField('Especialidade', max_length=100)
    
    def __str__(self):
        
        nome = self.usuario.get_full_name()
        return f"Dr(a). {nome if nome else self.usuario.username}"

class Paciente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='paciente')
    cpf = models.CharField('CPF', max_length=14, unique=True)
    data_nascimento = models.DateField('Data de Nascimento')
    telefone = models.CharField('Telefone', max_length=20, blank=True, null=True)

    SEXO_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    )
    sexo = models.CharField('Sexo', max_length=1, choices=SEXO_CHOICES, default='O')
    
    def __str__(self):
        nome = self.usuario.get_full_name()
        return f"Paciente: {nome if nome else self.usuario.username}"
    
    def whatsapp_link(self):
        """
        Limpa o telefone para gerar o link do WhatsApp.
        Remove parenteses, traços e espaços.
        Adiciona o código do Brasil (55) se não tiver.
        """
        if not self.telefone:
            return None
            
        numeros = ''.join(filter(str.isdigit, self.telefone))
        
        if len(numeros) < 10:
            return None
    
        if not numeros.startswith('55'):
            numeros = f"55{numeros}"
            
        return f"https://wa.me/{numeros}"



class Agendamento(models.Model):
    STATUS_CHOICES = (
        ('AGENDADO', 'Agendado'),
        ('AGUARDANDO', 'Na Sala de Espera'),
        ('CANCELADO', 'Cancelado'),
        ('REALIZADO', 'Realizado'),
    )

    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='agenda')
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='consultas')
    
    data_horario = models.DateTimeField('Data e Hora')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='AGENDADO')
    valor = models.DecimalField('Valor da Consulta', max_digits=10, decimal_places=2, default=200.00)
    pago = models.BooleanField('Está Pago?', default=False)
    observacoes = models.TextField('Observações', blank=True, null=True)
    avaliacao = models.IntegerField('Avaliação (1-5)', blank=True, null=True)
    comentario_paciente = models.TextField('Comentário', blank=True, null=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['data_horario']
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        
    def __str__(self):
        return f"{self.medico} - {self.paciente} - {self.data_horario.strftime('%d/%m/%Y %H:%M')}"

    def clean(self):
        """
        Regra de Negócio: Validação personalizada para evitar choque de horário.
        """

        if self.status == 'AGENDADO':

            conflito = Agendamento.objects.filter(
                medico=self.medico,
                data_horario=self.data_horario,
                status='AGENDADO'
            ).exclude(id=self.id) 

            if conflito.exists():
                raise ValidationError(f"O médico já possui um agendamento para {self.data_horario.strftime('%d/%m/%Y às %H:%M')}.")

    def save(self, *args, **kwargs):
        
        self.clean()
        super().save(*args, **kwargs)

class Prontuario(models.Model):
    
    agendamento = models.OneToOneField(Agendamento, on_delete=models.CASCADE, related_name='prontuario')
    
    historico = models.TextField('Histórico / Queixas', help_text='Descreva os sintomas do paciente')
    prescricao = models.TextField('Prescrição / Receita', help_text='Medicamentos e orientações')
    
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prontuário - {self.agendamento.paciente}"
    
class Medicamento(models.Model):
    nome = models.CharField('Nome do Medicamento', max_length=100, unique=True)
    generico = models.CharField('Nome Genérico', max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.nome