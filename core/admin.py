from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Medico, Paciente, Agendamento, Prontuario, Medicamento

class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Cargo / Tipo', {'fields': ('tipo',)}),
    )
    list_display = ('username', 'email', 'tipo', 'is_staff')

class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('medico', 'paciente', 'data_horario', 'status')
    list_filter = ('status', 'medico')

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Medico)
admin.site.register(Paciente)
admin.site.register(Agendamento, AgendamentoAdmin)

@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'generico')
    search_fields = ('nome',)