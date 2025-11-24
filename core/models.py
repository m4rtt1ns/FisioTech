from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone

# --- 1. USUÁRIO BASE ---
class Usuario(AbstractUser):
    TIPO_CHOICES = (
        ('MEDICO', 'Médico'),
        ('PACIENTE', 'Paciente'),
        ('RECEPCAO', 'Recepção'),
    )
    tipo = models.CharField('Tipo de Usuário', max_length=10, choices=TIPO_CHOICES, default='PACIENTE')
    foto = models.ImageField('Foto de Perfil', upload_to='perfis/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_tipo_display()})"

# --- 2. TABELAS AUXILIARES ---
class Medicamento(models.Model):
    nome = models.CharField('Nome', max_length=100, unique=True)
    generico = models.CharField('Genérico', max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.nome

class LogAuditoria(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    acao = models.CharField(max_length=255)
    data_hora = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.usuario} - {self.acao}"

# --- 3. PERFIS ---
class Medico(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='medico')
    crm = models.CharField('CRM', max_length=20, unique=True)
    especialidade = models.CharField('Especialidade', max_length=100)
    
    def __str__(self):
        return f"Dr(a). {self.usuario.first_name}"

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
        return self.usuario.first_name

    def whatsapp_link(self):
        if not self.telefone: return None
        numeros = ''.join(filter(str.isdigit, self.telefone))
        if len(numeros) < 10: return None
        if not numeros.startswith('55'): numeros = f"55{numeros}"
        return f"https://wa.me/{numeros}"

# --- 4. AGENDAMENTO ---
class Agendamento(models.Model):
    STATUS_CHOICES = (
        ('AGENDADO', 'Agendado'),
        ('AGUARDANDO', 'Na Sala de Espera'),
        ('REALIZADO', 'Realizado'),
        ('CANCELADO', 'Cancelado'),
    )

    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='agenda')
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='consultas')
    data_horario = models.DateTimeField('Data e Hora')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='AGENDADO')
    observacoes = models.TextField('Queixa Inicial', blank=True, null=True)
    
    # Financeiro
    valor = models.DecimalField('Valor', max_digits=10, decimal_places=2, default=200.00)
    pago = models.BooleanField('Pago', default=False)
    
    # Avaliação
    avaliacao = models.IntegerField('Estrelas', blank=True, null=True)
    comentario_paciente = models.TextField('Comentário', blank=True, null=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data_horario']
        
    def __str__(self):
        return f"{self.medico} - {self.paciente}"

class Prontuario(models.Model):
    agendamento = models.OneToOneField(Agendamento, on_delete=models.CASCADE, related_name='prontuario')
    historico = models.TextField('Histórico')
    prescricao = models.TextField('Prescrição')
    nivel_dor = models.IntegerField('Nível de Dor', blank=True, null=True) 
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prontuário {self.agendamento.id}"