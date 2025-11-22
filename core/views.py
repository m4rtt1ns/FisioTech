from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.db.models import Q, Sum, Avg  # <--- Importante para Gráficos e Financeiro
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

# Seus Models
from .models import Usuario, Paciente, Medico, Agendamento, Prontuario, Medicamento

# Seus Forms (Incluindo o AvaliacaoForm)
from .forms import (
    UsuarioCreationForm, 
    PacienteForm, 
    AgendamentoForm, 
    ProntuarioForm, 
    UsuarioEditarForm, 
    AvaliacaoForm
)

# --- HOME ---
def home(request):
    return render(request, 'index.html')

# --- CADASTRO ---
def cadastro_paciente(request):
    if request.method == 'POST':
        form_usuario = UsuarioCreationForm(request.POST, request.FILES)
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
                messages.success(request, "Cadastro realizado com sucesso!")
                return redirect('home')
    else:
        form_usuario = UsuarioCreationForm()
        form_paciente = PacienteForm()

    return render(request, 'cadastro_paciente.html', {
        'form_usuario': form_usuario,
        'form_paciente': form_paciente
    })

# --- PACIENTE: AGENDAMENTO ---
@login_required
def agendar_consulta(request):
    if request.user.tipo != 'PACIENTE':
        messages.warning(request, "Apenas pacientes podem agendar.")
        return redirect('home')

    if request.method == 'POST':
        form = AgendamentoForm(request.POST)
        if form.is_valid():
            agendamento = form.save(commit=False)
            agendamento.paciente = request.user.paciente 
            agendamento.save()
            messages.success(request, "Agendamento realizado com sucesso!")
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
def cancelar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    if request.user.tipo == 'PACIENTE' and agendamento.paciente != request.user.paciente:
        messages.error(request, "Permissão negada.")
        return redirect('home')

    if agendamento.status == 'AGENDADO':
        agendamento.status = 'CANCELADO'
        agendamento.save()
        messages.success(request, "Consulta cancelada.")
    
    return redirect('listar_agendamentos')

# --- PACIENTE: AVALIAÇÃO ---
@login_required
def avaliar_consulta(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)

    if request.user != agendamento.paciente.usuario:
        messages.error(request, "Você não pode avaliar esta consulta.")
        return redirect('home')
    
    if agendamento.status != 'REALIZADO':
        messages.error(request, "Consulta não concluída.")
        return redirect('listar_agendamentos')

    if request.method == 'POST':
        form = AvaliacaoForm(request.POST, instance=agendamento)
        if form.is_valid():
            form.save()
            messages.success(request, "Obrigado pelo feedback! ⭐")
            return redirect('listar_agendamentos')
    else:
        form = AvaliacaoForm(instance=agendamento)

    return render(request, 'avaliar.html', {'form': form, 'agendamento': agendamento})

# --- MÉDICO: PAINEL ---
@login_required
def painel_medico(request):
    if request.user.tipo != 'MEDICO':
        messages.error(request, "Acesso negado.")
        return redirect('home')

    # 1. Filtros e Busca
    agendamentos = Agendamento.objects.filter(medico=request.user.medico).order_by('data_horario')
    
    query = request.GET.get('q')
    if query:
        agendamentos = agendamentos.filter(
            Q(paciente__usuario__username__icontains=query) | 
            Q(paciente__cpf__icontains=query)
        )

    # 2. Dados Estatísticos
    todos = Agendamento.objects.filter(medico=request.user.medico)
    
    # Financeiro (Soma)
    faturamento_total = todos.filter(pago=True).aggregate(Sum('valor'))['valor__sum'] or 0
    
    # Qualidade (Média)
    media_estrelas = todos.filter(status='REALIZADO').aggregate(Avg('avaliacao'))['avaliacao__avg'] or 0

    contexto = {
        'agendamentos': agendamentos,
        'total_agendado': todos.filter(status='AGENDADO').count(),
        'total_realizado': todos.filter(status='REALIZADO').count(),
        'total_cancelado': todos.filter(status='CANCELADO').count(),
        'faturamento_total': faturamento_total,
        'media_estrelas': round(media_estrelas, 1),
    }

    return render(request, 'painel_medico.html', contexto)

# --- MÉDICO: ATENDIMENTO ---
@login_required
def realizar_atendimento(request, agendamento_id):
    if request.user.tipo != 'MEDICO':
        return redirect('home')

    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    # Cria form vazio para garantir existência da variável
    form = ProntuarioForm()

    if request.method == 'POST':
        form = ProntuarioForm(request.POST)
        if form.is_valid():
            prontuario = form.save(commit=False)
            prontuario.agendamento = agendamento
            prontuario.save()
            
            agendamento.status = 'REALIZADO'
            agendamento.save()
            
            messages.success(request, "Atendimento finalizado!")
            return redirect('painel_medico')

    lista_medicamentos = Medicamento.objects.all()

    return render(request, 'atendimento.html', {
        'form': form,
        'agendamento': agendamento,
        'lista_medicamentos': lista_medicamentos
    })

@login_required
def visualizar_prontuario(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    try:
        prontuario = agendamento.prontuario
    except ObjectDoesNotExist:
        if request.user.tipo == 'MEDICO':
            messages.warning(request, "Prontuário não encontrado. Preencha agora.")
            return redirect('realizar_atendimento', agendamento_id=agendamento.id)
        else:
            messages.error(request, "Documento não disponível.")
            return redirect('home')

    return render(request, 'prontuario_view.html', {
        'prontuario': prontuario,
        'agendamento': agendamento
    })

# --- RECEPÇÃO ---
@login_required
def painel_recepcao(request):
    if request.user.tipo != 'RECEPCAO' and not request.user.is_superuser:
        messages.error(request, "Acesso restrito.")
        return redirect('home')

    hoje = timezone.now().date()
    agendamentos = Agendamento.objects.filter(data_horario__date=hoje).order_by('data_horario')

    return render(request, 'painel_recepcao.html', {'agendamentos': agendamentos})

@login_required
def confirmar_presenca(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    agendamento.status = 'AGUARDANDO'
    agendamento.save()
    messages.success(request, "Presença confirmada.")
    return redirect('painel_recepcao')

@login_required
def receber_pagamento(request, agendamento_id):
    if request.user.tipo != 'RECEPCAO' and not request.user.is_superuser:
        return redirect('home')

    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    agendamento.pago = True
    agendamento.save()
    
    messages.success(request, f"Pagamento de R$ {agendamento.valor} confirmado!")
    return redirect('painel_recepcao')

# --- PERFIL ---
@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = UsuarioEditarForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado!")
            if request.user.tipo == 'MEDICO':
                return redirect('painel_medico')
            return redirect('home')
    else:
        form = UsuarioEditarForm(instance=request.user)

    return render(request, 'editar_perfil.html', {'form': form})