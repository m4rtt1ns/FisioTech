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
from .models import Prontuario
from .forms import ProntuarioForm
from django.core.exceptions import ObjectDoesNotExist
from .forms import UsuarioEditarForm
from django.utils import timezone

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

@login_required
def cancelar_agendamento(request, agendamento_id):
    
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    if request.user.tipo == 'PACIENTE' and agendamento.paciente != request.user.paciente:
        messages.error(request, "Você não tem permissão para cancelar este agendamento.")
        return redirect('home')

    if agendamento.status != 'AGENDADO':
        messages.warning(request, "Esta consulta não pode ser cancelada (já foi realizada ou cancelada).")
        return redirect('listar_agendamentos')

    agendamento.status = 'CANCELADO'
    agendamento.save()
    
    messages.success(request, "Consulta cancelada com sucesso.")
    return redirect('listar_agendamentos')

@login_required
def realizar_atendimento(request, agendamento_id):
    
    if request.user.tipo != 'MEDICO':
        messages.error(request, "Apenas médicos podem acessar essa tela.")
        return redirect('home')

    agendamento = get_object_or_404(Agendamento, id=agendamento_id)

    if agendamento.medico != request.user.medico:
        messages.error(request, "Você não pode atender paciente de outro médico!")
        return redirect('painel_medico')

    if request.method == 'POST':
        form = ProntuarioForm(request.POST)
        if form.is_valid():
            
            prontuario = form.save(commit=False)
            prontuario.agendamento = agendamento
            prontuario.save()
            
            agendamento.status = 'REALIZADO'
            agendamento.save()
            
            messages.success(request, "Atendimento concluído com sucesso!")
            return redirect('painel_medico')
    else:
        form = ProntuarioForm()

    return render(request, 'atendimento.html', {
        'form': form, 
        'agendamento': agendamento
    })

@login_required
def visualizar_prontuario(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    try:
        prontuario = agendamento.prontuario
    except ObjectDoesNotExist:
        
        if request.user.tipo == 'MEDICO':

            messages.warning(request, "Este atendimento não possui prontuário salvo. Por favor, preencha agora.")
            return redirect('realizar_atendimento', agendamento_id=agendamento.id)
        
        else:

            messages.error(request, "O documento desta consulta ainda não está disponível.")
            return redirect('home')

    eh_medico_dono = (request.user.tipo == 'MEDICO' and agendamento.medico == request.user.medico)
    eh_paciente_dono = (request.user.tipo == 'PACIENTE' and agendamento.paciente == request.user.paciente)
    
    if not (eh_medico_dono or eh_paciente_dono):
        messages.error(request, "Você não tem permissão para ver este documento.")
        return redirect('home')

    return render(request, 'prontuario_view.html', {
        'prontuario': prontuario,
        'agendamento': agendamento
    })


@login_required
def painel_medico(request):
    if request.user.tipo != 'MEDICO':
        messages.error(request, "Acesso negado.")
        return redirect('home')

    # 1. Filtros básicos
    agendamentos = Agendamento.objects.filter(medico=request.user.medico).order_by('data_horario')
    
    # 2. Busca
    query = request.GET.get('q')
    if query:
        agendamentos = agendamentos.filter(
            Q(paciente__usuario__username__icontains=query) | 
            Q(paciente__cpf__icontains=query)
        )

    # 3. DADOS DO GRÁFICO (Isso é obrigatório!)
    todos = Agendamento.objects.filter(medico=request.user.medico)
    contexto = {
        'agendamentos': agendamentos,
        'total_agendado': todos.filter(status='AGENDADO').count(),
        'total_realizado': todos.filter(status='REALIZADO').count(),
        'total_cancelado': todos.filter(status='CANCELADO').count(),
    }

    return render(request, 'painel_medico.html', contexto)

@login_required
def editar_perfil(request):
    if request.method == 'POST':
        # Carrega o formulário com os dados que vieram da tela (POST) + Arquivos (FILES)
        # instance=request.user diz para ATUALIZAR o usuário logado, e não criar um novo
        form = UsuarioEditarForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            
            # Redireciona para a home certa dependendo do tipo
            if request.user.tipo == 'MEDICO':
                return redirect('painel_medico')
            else:
                return redirect('home')
    else:
        # Se for GET (apenas abrir a página), carrega os dados atuais do usuário
        form = UsuarioEditarForm(instance=request.user)

    return render(request, 'editar_perfil.html', {'form': form})

@login_required
def painel_recepcao(request):
    # 1. Segurança: Só Recepcionista (ou Admin) entra
    # Se você ainda não criou o user RECEPCAO, pode testar com SUPERUSER também
    if request.user.tipo != 'RECEPCAO' and not request.user.is_superuser:
        messages.error(request, "Acesso negado. Área restrita à recepção.")
        return redirect('home')

    # 2. Filtra agendamentos de HOJE (independente do médico)
    hoje = timezone.now().date()
    agendamentos = Agendamento.objects.filter(data_horario__date=hoje).order_by('data_horario')

    return render(request, 'painel_recepcao.html', {'agendamentos': agendamentos})

@login_required
def confirmar_presenca(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    # Muda status para 'Na Sala de Espera'
    agendamento.status = 'AGUARDANDO'
    agendamento.save()
    
    messages.success(request, f"Paciente {agendamento.paciente} confirmado na sala de espera.")
    return redirect('painel_recepcao')