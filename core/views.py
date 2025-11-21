from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.db import transaction
from .forms import UsuarioCreationForm, PacienteForm
from .forms import AgendamentoForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Usuario, Paciente, Agendamento

def cadastro_paciente(request):
    
    if request.method == 'POST':
        
        form_usuario = UsuarioCreationForm(request.POST)
        form_paciente = PacienteForm(request.POST)

    
        if form_usuario.is_valid() and form_paciente.is_valid():
            
            with transaction.atomic():
                
                user = form_usuario.save(commit=False)
                user.tipo = 'PACIENTE' 
                user.save() 
                
                
                paciente = form_paciente.save(commit=False)
                paciente.usuario = user 
                paciente.save() 
                
                login(request, user)
                
                return redirect('home') 

    else:

        form_usuario = UsuarioCreationForm()
        form_paciente = PacienteForm()

    contexto = {
        'form_usuario': form_usuario,
        'form_paciente': form_paciente
    }
    
    return render(request, 'cadastro_paciente.html', contexto)

def home(request):
    return render(request, 'index.html')

@login_required
def agendar_consulta(request):
    # BLINDAGEM: Verifica se o usuário tem perfil de paciente
    if request.user.tipo != 'PACIENTE':
        # Se não for paciente, manda de volta pra home com um erro
        messages.warning(request, "Apenas pacientes podem agendar consultas.")
        return redirect('home')

    if request.method == 'POST':
        form = AgendamentoForm(request.POST)
        if form.is_valid():
            agendamento = form.save(commit=False)
            agendamento.paciente = request.user.paciente 
            agendamento.save()
            messages.success(request, "Agendamento realizado com sucesso!") # Feedback visual
            return redirect('home')
    else:
        form = AgendamentoForm()

    return render(request, 'agendar.html', {'form': form})

@login_required
def listar_agendamentos(request):
    # Verifica se é paciente
    if request.user.tipo != 'PACIENTE':
        return redirect('home')
    
    # Busca as consultas do paciente logado, ordenadas por data
    agendamentos = Agendamento.objects.filter(paciente=request.user.paciente).order_by('data_horario')
    
    return render(request, 'minhas_consultas.html', {'agendamentos': agendamentos})