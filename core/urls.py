from django.urls import path
from . import views

urlpatterns = [
   
    path('cadastro/', views.cadastro_paciente, name='cadastro_paciente'),
    path('', views.home, name='home'), 
    path('agendar/', views.agendar_consulta, name='agendar_consulta'),
    path('meus-agendamentos/', views.listar_agendamentos, name='listar_agendamentos'),
    path('medico/painel/', views.painel_medico, name='painel_medico'),
    path('medico/concluir/<int:agendamento_id>/', views.concluir_consulta, name='concluir_consulta'),
    path('agendamento/cancelar/<int:agendamento_id>/', views.cancelar_agendamento, name='cancelar_agendamento'),
    path('medico/atendimento/<int:agendamento_id>/', views.realizar_atendimento, name='realizar_atendimento'),
    path('documento/prontuario/<int:agendamento_id>/', views.visualizar_prontuario, name='visualizar_prontuario'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('recepcao/', views.painel_recepcao, name='painel_recepcao'),
    path('recepcao/confirmar/<int:agendamento_id>/', views.confirmar_presenca, name='confirmar_presenca'),
]