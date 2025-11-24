# 🧘‍♂️ FisioTech - Sistema de Gestão para Clínicas de Fisioterapia

![Status](https://img.shields.io/badge/Status-Concluído-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?style=for-the-badge&logo=bootstrap&logoColor=white)

Um sistema SaaS completo (Full Stack) focado na gestão de clínicas de fisioterapia e reabilitação. O projeto vai além do agendamento básico, oferecendo ferramentas visuais para acompanhamento da evolução do paciente, controle financeiro e conformidade com a LGPD.

---

## 🚀 Funcionalidades Exclusivas

### 🩺 Módulo do Fisioterapeuta
- **Gráfico de Evolução da Dor:** Visualização automática (Chart.js) da melhora do paciente baseada no histórico da Escala EVA.
- **Prontuário Visual:** Registro de sessão com **Slider de Dor Interativo** (0-10) e autocomplete de exercícios/condutas.
- **Dashboard Inteligente:** KPIs de qualidade (Nota Média), Faturamento do dia e Gráfico de Status (Rosca).
- **Fila em Tempo Real:** Identificação visual de pacientes que já realizaram check-in.

### 👤 Portal do Paciente
- **Login Simplificado:** Acesso via CPF.
- **Auto-Agendamento:** Calendário inteligente com bloqueio de horários passados e feriados.
- **Minha Evolução:** Acesso ao histórico de sessões e visualização de receitas/orientações.
- **Feedback:** Avaliação de atendimento (Estrelas) pós-consulta.
- **LGPD:** Ferramentas para gestão de privacidade e desativação de conta ("Direito ao Esquecimento").

### 🛎️ Recepção & Gestão
- **Integração WhatsApp:** Botão "Chamar no Zap" que abre conversa direta com o paciente com mensagem personalizada.
- **Triagem:** Confirmação de presença (Check-in) que notifica o painel médico.
- **Controle Financeiro:** Gestão de pagamentos (Pendente/Pago) e relatórios de caixa.

### 🎨 Interface e UX (User Experience)
- **Identidade Visual:** Design clean focado em saúde (Teal/Verde-Água).
- **Dark Mode Nativo:** Suporte completo a tema escuro/claro via Bootstrap 5.3.
- **Responsividade:** Layout adaptável para tablets e celulares.
- **Micro-interações:** Animações suaves (AOS) e feedback de carregamento.

---

## 🛠️ Tecnologias Utilizadas

- **Back-end:** Python 3, Django 5.
- **Front-end:** HTML5, CSS3, Bootstrap 5.3, JavaScript.
- **Visualização de Dados:** Chart.js (Gráficos de Rosca e Linha).
- **Banco de Dados:** PostgreSQL.
- **Segurança:** Hash de senhas Argon2, CSRF Protection, Auditoria de Logs (LGPD).
- **Deploy Ready:** Configurado com Gunicorn e WhiteNoise.

---

## ⚙️ Instalação e Configuração

Siga os passos abaixo para rodar o projeto localmente:

### 1. Clone o repositório
```bash
git clone [https://github.com/SEU-USUARIO/fisiotech.git](https://github.com/SEU-USUARIO/fisiotech.git)
cd fisiotech
````

2\. Crie o ambiente virtual

```bash
  Linux/Mac
python3 -m venv venv
source venv/bin/activate

  Windows
python -m venv venv
venv\Scripts\activate
```

### 3\. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4\. Configure o Banco de Dados

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5\. Popule o Banco com Dados Fictícios (Opcional)

O sistema possui um script para gerar médicos, pacientes e consultas automaticamente para teste:

```bash
python manage.py popular_banco
```

### 6\. Crie um Superusuário (Caso não use o script)

```bash
python manage.py createsuperuser
```

### 7\. Inicie o Servidor

```bash
python manage.py runserver
```

Acesse: `http://127.0.0.1:8000`

-----

## 🧪 Perfis de Acesso para Teste

Se você rodou o script `popular_banco`, use:

  * **Médico:** `dr_nome` / Senha: `123`
  * **Paciente:** `CPF_GERADO` / Senha: `123`

Para criar manualmente:

1.  **Médico:** Crie um usuário, marque tipo `MEDICO` e cadastre o perfil na tabela `Medicos`.
2.  **Recepção:** Crie um usuário e marque tipo `RECEPCAO`.

-----

## 📝 Licença

Projeto desenvolvido para fins acadêmicos (Extensão Universitária).

````

---

### Passo 3: Subir as Alterações para o GitHub

Agora é só mandar tudo para a nuvem:

```bash
git add .
git commit -m "Update Final: Design Fisioterapia, Gráficos de Evolução e LGPD"
git push
````