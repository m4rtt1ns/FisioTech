from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from .models import Usuario, Paciente, Agendamento, Prontuario, Medicamento

# --- 1. CADASTRO DE PACIENTE ---
class CadastroPacienteForm(UserCreationForm):
    first_name = forms.CharField(label='Nome', max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Sobrenome', max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='E-mail', required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    termo_aceite = forms.BooleanField(
        required=True, 
        label="Li e concordo com o tratamento dos meus dados sensíveis para fins médicos (LGPD).",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'foto')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo = 'PACIENTE'
        if commit:
            user.save()
        return user

# --- 2. DADOS DO PACIENTE ---
class PacienteDadosForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['cpf', 'data_nascimento', 'telefone', 'sexo']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'cpf': forms.TextInput(attrs={'placeholder': '000.000.000-00', 'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        return ''.join(filter(str.isdigit, cpf))

# --- 3. LOGIN ---
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='CPF ou Usuário', 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu CPF (pacientes) ou Usuário'})
    )
    password = forms.CharField(
        label='Senha', 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

# --- 4. AGENDAMENTO ---
class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['medico', 'data_horario', 'observacoes']
        widgets = {
            'data_horario': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'medico': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Medico
        self.fields['medico'].queryset = Medico.objects.all()

    def clean_data_horario(self):
        data = self.cleaned_data.get('data_horario')
        if not data: return None
        if data < timezone.now():
            raise forms.ValidationError("Você não pode agendar consultas no passado!")
        hora = data.hour
        if hora < 8 or hora >= 18:
            raise forms.ValidationError("A clínica funciona apenas das 08:00 às 18:00.")
        if data.weekday() == 6:
            raise forms.ValidationError("A clínica não abre aos domingos.")
        return data

# --- 5. PRONTUÁRIO (CORRIGIDO AQUI) ---
class ProntuarioForm(forms.ModelForm):
    class Meta:
        model = Prontuario
        fields = ['historico', 'prescricao', 'nivel_dor']
        widgets = {
            'historico': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Evolução do paciente...'}),
            'prescricao': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'id': 'id_prescricao', 'placeholder': 'Exercícios e orientações...'}),
            
            # FIXAMOS O ID AQUI PARA O JAVASCRIPT FUNCIONAR
            'nivel_dor': forms.NumberInput(attrs={
                'id': 'slider_dor_input', 
                'type': 'range', 
                'min': 0, 
                'max': 10, 
                'step': 1, 
                'class': 'form-range'
            }),
        }

# --- 6. AVALIAÇÃO ---
class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['avaliacao', 'comentario_paciente']
        widgets = {
            'avaliacao': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control', 'placeholder': 'Nota de 1 a 5'}),
            'comentario_paciente': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Elogios, críticas ou sugestões...'}),
        }

# --- 7. PERFIL ---
class UsuarioEditarForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['email', 'foto']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }