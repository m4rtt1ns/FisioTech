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
    
    def __str__(self):
        nome = self.usuario.get_full_name()
        return f"Paciente: {nome if nome else self.usuario.username}"



class Agendamento(models.Model):
    STATUS_CHOICES = (
        ('AGENDADO', 'Agendado'),
        ('CANCELADO', 'Cancelado'),
        ('REALIZADO', 'Realizado'),
    )

    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='agenda')
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='consultas')
    
    data_horario = models.DateTimeField('Data e Hora')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='AGENDADO')
    observacoes = models.TextField('Observações', blank=True, null=True)
    
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