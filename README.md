# 🏥 Clínica Tech - Sistema de Gestão Hospitalar (SaaS)

Atualizado: documentação completa do projeto, instruções para rodar localmente, links para arquivos-chave e arquivos de documentação recomendados.

Status: Concluído  
Tecnologias: Python 3.10+, Django 5, Bootstrap 5, SQLite, Pillow

Sumário
- Visão geral
- Como rodar localmente (dev)
- Estrutura do projeto & links (arquivos-chave)
- Modelos, Forms e Views principais (links para símbolos)
- Templates
- Migrações / Banco de dados
- Admin / superuser
- Testes
- Notas sobre mídia / uploads
- Arquivos de documentação recomendados
- Comandos úteis

Visão geral
Um sistema completo para gestão de clínica: agendamento, triagem (recepção), área do médico, prontuário eletrônico, perfil do paciente com upload de foto, pagamento simples e avaliações.

Como rodar localmente (desenvolvimento)
1. Crie e ative o virtualenv (exemplo Unix):
```sh
python3 -m venv venv
source venv/bin/activate
```
2. Instale as dependências:
```sh
pip install -r requirements.txt
```
3. Acesse o diretório do projeto (onde está o `manage.py`):
```sh
cd caminho/para/o/projeto
```
4. Aplique as migrações iniciais:
```sh
python manage.py migrate
```
5. Crie um superusuário para acessar o admin:
```sh
python manage.py createsuperuser
```
6. Inicie o servidor local:
```sh
python manage.py runserver
```
7. Acesse o sistema em: [http://127.0.0.1:8000](http://127.0.0.1:8000)

Estrutura do projeto & links (arquivos-chave)
- Entrypoint do projeto: [manage.py](manage.py)
- Configurações: [`setup.settings`](setup/settings.py) — ver [setup/settings.py](setup/settings.py)
- URLs principais: [`setup.urls`](setup/urls.py) — ver [setup/urls.py](setup/urls.py) e app: [core/urls.py](core/urls.py)

Modelos, Forms e Views principais (links para símbolos)
Modelos principais (app core):
- [`core.models.Usuario`](core/models.py)
- [`core.models.Medico`](core/models.py)
- [`core.models.Paciente`](core/models.py)
- [`core.models.Agendamento`](core/models.py)
- [`core.models.Prontuario`](core/models.py)  
(arquivo: [core/models.py](core/models.py))

Forms importantes:
- [`core.forms.UsuarioCreationForm`](core/forms.py)
- [`core.forms.UsuarioEditarForm`](core/forms.py)
- [`core.forms.AgendamentoForm`](core/forms.py)
- [`core.forms.ProntuarioForm`](core/forms.py)  
(arquivo: [core/forms.py](core/forms.py))

Views principais:
- Cadastro / auth: [`core.views.cadastro_paciente`](core/views.py)
- Agendamento: [`core.views.agendar_consulta`](core/views.py), [`core.views.listar_agendamentos`](core/views.py)
- Painéis: [`core.views.painel_medico`](core/views.py), [`core.views.painel_recepcao`](core/views.py)
- Atendimento / prontuário: [`core.views.realizar_atendimento`](core/views.py), [`core.views.visualizar_prontuario`](core/views.py)
- Operações rápidas: [`core.views.confirmar_presenca`](core/views.py), [`core.views.cancelar_agendamento`](core/views.py), [`core.views.concluir_consulta`](core/views.py)  
(arquivo: [core/views.py](core/views.py))

Templates:
- Pasta: [core/templates](core/templates)
  - login: [core/templates/login.html](core/templates/login.html)
  - home/index: [core/templates/index.html](core/templates/index.html)
  - agendar: [core/templates/agendar.html](core/templates/agendar.html)
  - painel médico: [core/templates/painel_medico.html](core/templates/painel_medico.html)
  - painel recepção: [core/templates/painel_recepcao.html](core/templates/painel_recepcao.html)
  - prontuário visualização: [core/templates/prontuario_view.html](core/templates/prontuario_view.html)
  - editar perfil: [core/templates/editar_perfil.html](core/templates/editar_perfil.html)
  - minhas consultas: [core/templates/minhas_consultas.html](core/templates/minhas_consultas.html)

Migrações / Banco de dados:
- Pasta: [core/migrations](core/migrations) — por exemplo [core/migrations/0001_initial.py](core/migrations/0001_initial.py), [core/migrations/0002_prontuario.py](core/migrations/0002_prontuario.py), [core/migrations/0003_usuario_foto.py](core/migrations/0003_usuario_foto.py)

Admin / superuser
Acesse o admin em: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) com o superusuário criado.

Testes
Para rodar os testes:
```sh
python manage.py test
```

Notas sobre mídia / uploads
Pasta de uploads: `media/` (ver `settings.py`)

Arquivos de documentação recomendados
- [Documentação do Django](https://docs.djangoproject.com/en/stable/)
- [Documentação do Bootstrap](https://getbootstrap.com/docs/5.0/getting-started/introduction/)
- [Documentação do SQLite](https://www.sqlite.org/docs.html)

Comandos úteis
- Rodar o servidor: `python manage.py runserver`
- Criar migrações: `python manage.py makemigrations`
- Aplicar migrações: `python manage.py migrate`
- Criar superusuário: `python manage.py createsuperuser`
- Rodar testes: `python manage.py test`