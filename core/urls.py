from django.urls import path
from . import views

urlpatterns = [
   
    path('cadastro/', views.cadastro_paciente, name='cadastro_paciente'),
    path('', views.home, name='home'), 
    path('agendar/', views.agendar_consulta, name='agendar_consulta'),
    path('meus-agendamentos/', views.listar_agendamentos, name='listar_agendamentos'),
    path('medico/painel/', views.painel_medico, name='painel_medico'),
    path('medico/concluir/<int:agendamento_id>/', views.concluir_consulta, name='concluir_consulta'),
]