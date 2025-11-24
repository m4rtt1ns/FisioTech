from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.db.models import Q, Sum, Avg
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime

from .models import (
    Usuario, 
    Paciente, 
    Medico, 
    Agendamento, 
    Prontuario, 
    Medicamento, 
    LogAuditoria
)

from .forms import (
    CadastroPacienteForm, 
    PacienteDadosForm, 
    AgendamentoForm, 
    ProntuarioForm, 
    UsuarioEditarForm, 
    AvaliacaoForm
)

def home(request):
    return render(request, 'index.html')

def cadastro_paciente(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form_usuario = CadastroPacienteForm(request.POST, request.FILES)
        form_paciente = PacienteDadosForm(request.POST)

        if form_usuario.is_valid() and form_paciente.is_valid():
            try:
                with transaction.atomic():
                    user = form_usuario.save(commit=False)
                    cpf_limpo = form_paciente.cleaned_data['cpf']
                    user.username = cpf_limpo 
                    user.tipo = 'PACIENTE' 
                    user.save()
                    
                    paciente = form_paciente.save(commit=False)
                    paciente.usuario = user
                    paciente.cpf = cpf_limpo
                    paciente.save()
                    
                    login(request, user)
                    messages.success(request, f"Cadastro realizado! Seu login é: {cpf_limpo}")
                    return redirect('home')
            except Exception as e:
                messages.error(request, f"Erro ao cadastrar: {e}")
    else:
        form_usuario = CadastroPacienteForm()
        form_paciente = PacienteDadosForm()

    return render(request, 'cadastro_paciente.html', {
        'form_usuario': form_usuario,
        'form_paciente': form_paciente
    })

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
            messages.success(request, "Agendamento realizado com sucesso!")
            return redirect('home')
    else:
        form = AgendamentoForm()

    return render(request, 'agendar.html', {'form': form})

@login_required
def listar_agendamentos(request):
    if request.user.tipo != 'PACIENTE':
        return redirect('home')
    
    agendamentos = Agendamento.objects.filter(paciente=request.user.paciente).order_by('-data_horario')
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
    else:
        messages.warning(request, "Não é possível cancelar esta consulta.")
    
    return redirect('listar_agendamentos')

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

@login_required
def painel_medico(request):
    if request.user.tipo != 'MEDICO':
        messages.error(request, "Acesso negado.")
        return redirect('home')

    agendamentos = Agendamento.objects.filter(medico=request.user.medico).order_by('data_horario')
    
    query = request.GET.get('q')
    if query:
        agendamentos = agendamentos.filter(
            Q(paciente__usuario__first_name__icontains=query) | 
            Q(paciente__usuario__last_name__icontains=query) |
            Q(paciente__cpf__icontains=query)
        )

    todos = Agendamento.objects.filter(medico=request.user.medico)
    
    faturamento_total = todos.filter(pago=True).aggregate(Sum('valor'))['valor__sum'] or 0
    
    media_estrelas = todos.filter(status='REALIZADO').aggregate(Avg('avaliacao'))['avaliacao__avg'] or 0

    contexto = {
        'agendamentos': agendamentos,
        'total_agendado': todos.filter(status__in=['AGENDADO', 'AGUARDANDO']).count(),
        'total_realizado': todos.filter(status='REALIZADO').count(),
        'total_cancelado': todos.filter(status='CANCELADO').count(),
        'faturamento_total': faturamento_total,
        'media_estrelas': round(media_estrelas, 1),
    }

    return render(request, 'painel_medico.html', contexto)

@login_required
def realizar_atendimento(request, agendamento_id):
    if request.user.tipo != 'MEDICO':
        return redirect('home')

    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    form = ProntuarioForm()

    if request.method == 'POST':
        form = ProntuarioForm(request.POST)
        if form.is_valid():
            prontuario = form.save(commit=False)
            prontuario.agendamento = agendamento
            prontuario.save()
            
            agendamento.status = 'REALIZADO'
            agendamento.save()
            
            LogAuditoria.objects.create(
                usuario=request.user,
                acao=f"Realizou atendimento {agendamento.id}",
                ip=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, "Atendimento finalizado com sucesso!")
            return redirect('painel_medico')

    lista_medicamentos = Medicamento.objects.all()

    historico_paciente = Agendamento.objects.filter(
        paciente=agendamento.paciente,
        status='REALIZADO'
    ).order_by('data_horario')

    datas_grafico = []
    dores_grafico = []

    for consulta in historico_paciente:
        if hasattr(consulta, 'prontuario'):
            datas_grafico.append(consulta.data_horario.strftime('%d/%m'))
            dores_grafico.append(consulta.prontuario.nivel_dor)

    return render(request, 'atendimento.html', {
        'form': form,
        'agendamento': agendamento,
        'lista_medicamentos': lista_medicamentos,
        'datas_grafico': datas_grafico,
        'dores_grafico': dores_grafico
    })

@login_required
def visualizar_prontuario(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    try:
        prontuario = agendamento.prontuario
        
        LogAuditoria.objects.create(
            usuario=request.user,
            acao=f"Visualizou prontuário {agendamento.id}",
            ip=request.META.get('REMOTE_ADDR')
        )

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

@login_required
def painel_recepcao(request):
    if request.user.tipo != 'RECEPCAO' and not request.user.is_superuser:
        messages.error(request, "Acesso restrito à recepção.")
        return redirect('home')

    data_get = request.GET.get('data')
    if data_get:
        try:
            data_filtrada = datetime.strptime(data_get, '%Y-%m-%d').date()
        except ValueError:
            data_filtrada = timezone.now().date()
    else:
        data_filtrada = timezone.now().date()

    agendamentos = Agendamento.objects.filter(data_horario__date=data_filtrada).order_by('data_horario')

    return render(request, 'painel_recepcao.html', {
        'agendamentos': agendamentos,
        'data_atual': data_filtrada
    })

@login_required
def confirmar_presenca(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    agendamento.status = 'AGUARDANDO'
    agendamento.save()
    messages.success(request, f"Check-in realizado: {agendamento.paciente}")
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

@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = UsuarioEditarForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado!")
            
            if request.user.tipo == 'MEDICO':
                return redirect('painel_medico')
            elif request.user.tipo == 'RECEPCAO':
                return redirect('painel_recepcao')
            else:
                return redirect('home')
    else:
        form = UsuarioEditarForm(instance=request.user)

    return render(request, 'editar_perfil.html', {'form': form})

@login_required
def desativar_conta(request):
    if request.method == 'POST':
        user = request.user
        user.is_active = False
        user.save()
        messages.info(request, "Conta desativada com sucesso.")
        return redirect('login')
    
    return render(request, 'desativar_conta.html')