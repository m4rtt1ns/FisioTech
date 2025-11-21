from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Medico, Paciente, Agendamento

# 1. Configuração para o Usuário Customizado
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Cargo / Tipo', {'fields': ('tipo',)}),
    )
    list_display = ('username', 'email', 'tipo', 'is_staff')

# 2. Configuração para os Agendamentos
# A CORREÇÃO ESTÁ AQUI EMBAIXO (admin.ModelAdmin e não admin.site.ModelAdmin)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('medico', 'paciente', 'data_horario', 'status')
    list_filter = ('status', 'medico')

# 3. Registrar tudo no Painel
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Medico)
admin.site.register(Paciente)
admin.site.register(Agendamento, AgendamentoAdmin)