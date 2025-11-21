from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.db import transaction
from .forms import UsuarioCreationForm, PacienteForm
from .forms import AgendamentoForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Usuario, Paciente, Agendamento
from django.shortcuts import get_object_or_404
from django.db.models import Q

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
    
    if request.user.tipo != 'PACIENTE':
        
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
    
    if request.user.tipo != 'PACIENTE':
        return redirect('home')
    
    agendamentos = Agendamento.objects.filter(paciente=request.user.paciente).order_by('data_horario')
    
    return render(request, 'minhas_consultas.html', {'agendamentos': agendamentos})

@login_required
def painel_medico(request):
    
    if request.user.tipo != 'MEDICO':
        messages.error(request, "Acesso negado. Área restrita para médicos.")
        return redirect('home')

    agendamentos = Agendamento.objects.filter(medico=request.user.medico).order_by('data_horario')
    
    return render(request, 'painel_medico.html', {'agendamentos': agendamentos})

@login_required
def concluir_consulta(request, agendamento_id):
    
    if request.user.tipo != 'MEDICO':
        messages.error(request, "Apenas médicos podem concluir consultas.")
        return redirect('home')

    agendamento = get_object_or_404(Agendamento, id=agendamento_id)

    if agendamento.medico != request.user.medico:
        messages.error(request, "Esse agendamento não é seu!")
        return redirect('painel_medico')

    agendamento.status = 'REALIZADO'
    agendamento.save()
    
    messages.success(request, f"Consulta de {agendamento.paciente} concluída!")
    return redirect('painel_medico')

@login_required
def painel_medico(request):
    if request.user.tipo != 'MEDICO':
        messages.error(request, "Acesso negado. Área restrita para médicos.")
        return redirect('home')

    agendamentos = Agendamento.objects.filter(medico=request.user.medico).order_by('data_horario')

    query = request.GET.get('q')
    
    if query:
        
        agendamentos = agendamentos.filter(
            Q(paciente__usuario__username__icontains=query) | 
            Q(paciente__cpf__icontains=query)
        )

    return render(request, 'painel_medico.html', {'agendamentos': agendamentos})