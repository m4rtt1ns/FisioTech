from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Paciente, Agendamento


class UsuarioCreationForm(UserCreationForm):
    class Meta:
        model = Usuario
        
        fields = ('username', 'email', 'tipo')
        
    def save(self, commit=True):
        
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['cpf', 'data_nascimento', 'telefone']
        
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