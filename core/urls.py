from django.urls import path
from . import views

urlpatterns = [
    # --- HOME ---
    path('', views.home, name='home'),
    
    # --- CADASTRO ---
    path('cadastro/', views.cadastro_paciente, name='cadastro_paciente'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfil/desativar/', views.desativar_conta, name='desativar_conta'),

    # --- PACIENTE ---
    path('agendar/', views.agendar_consulta, name='agendar_consulta'),
    path('meus-agendamentos/', views.listar_agendamentos, name='listar_agendamentos'),
    path('agendamento/cancelar/<int:agendamento_id>/', views.cancelar_agendamento, name='cancelar_agendamento'),
    path('avaliacao/criar/<int:agendamento_id>/', views.avaliar_consulta, name='avaliar_consulta'),
    
    # --- MÉDICO ---
    path('medico/painel/', views.painel_medico, name='painel_medico'),
    
    # AQUI ESTAVA O ERRO: Removemos o 'concluir_consulta' e usamos o 'realizar_atendimento'
    path('medico/atendimento/<int:agendamento_id>/', views.realizar_atendimento, name='realizar_atendimento'),
    
    # Visualizar Documento (Receita/Prontuário)
    path('documento/prontuario/<int:agendamento_id>/', views.visualizar_prontuario, name='visualizar_prontuario'),

    # --- RECEPÇÃO ---
    path('recepcao/', views.painel_recepcao, name='painel_recepcao'),
    path('recepcao/confirmar/<int:agendamento_id>/', views.confirmar_presenca, name='confirmar_presenca'),
    path('recepcao/pagamento/<int:agendamento_id>/', views.receber_pagamento, name='receber_pagamento'),
]