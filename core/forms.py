from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .models import Usuario, Paciente, Agendamento
from .models import Prontuario

class UsuarioCreationForm(UserCreationForm):
    class Meta:
        model = Usuario
        
        fields = ['username', 'email', 'tipo', 'foto']

    def save(self, commit=True):
        
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['cpf', 'data_nascimento', 'telefone', 'sexo']
        
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['medico', 'data_horario', 'observacoes']
        widgets = {

            'data_horario': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Medico
        self.fields['medico'].queryset = Medico.objects.all()

    def clean_data_horario(self):
        data = self.cleaned_data.get('data_horario')
        
        if data and data < timezone.now():
            raise forms.ValidationError("Você não pode agendar consultas no passado!")
        
        return data
    
class ProntuarioForm(forms.ModelForm):
    class Meta:
        model = Prontuario
        fields = ['historico', 'prescricao']
        widgets = {
            'historico': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'prescricao': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        }

class UsuarioEditarForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['email', 'foto']

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['avaliacao', 'comentario_paciente']
        widgets = {
            'avaliacao': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
            'comentario_paciente': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Elogios, críticas ou sugestões...'}),
        }