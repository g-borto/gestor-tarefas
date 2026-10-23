# Planejamento no Jira — Gestor de Tarefas

Estrutura pronta para cadastro manual no Jira. As chaves `S1-01`, `S2-01` etc. são apenas
referências deste documento; o Jira gera as chaves reais (ex.: `GT-1`) ao criar as tarefas.

## Configuração do board

- **Tipo de projeto:** Kanban (com o recurso *Sprints* habilitado nas configurações do projeto,
  para permitir a divisão em duas Sprints).
- **Colunas do board:** `A Fazer` → `Em Andamento` → `Em Teste` → `Concluído`
- **Sprints:**
  - **Sprint 1 — Planejamento, ambiente e backend** (6 h)
  - **Sprint 2 — Frontend, testes, deploy e documentação** (6 h)
- **Tipo de item:** Tarefa, com *Estimativa original* preenchida em horas.

---

## Sprint 1 — 6 horas

| Ref.  | Tarefa | Fase | Estimativa |
|-------|--------|------|-----------:|
| S1-01 | Planejamento do projeto: definir escopo e requisitos | Planejamento | 1h |
| S1-02 | Configuração do ambiente de desenvolvimento | Desenvolvimento | 1h |
| S1-03 | Modelagem do banco de dados (usuários e tarefas) | Desenvolvimento | 0,5h |
| S1-04 | Implementação da autenticação (registro, login, logout) | Desenvolvimento | 1,5h |
| S1-05 | Desenvolvimento do Backend – Parte 1: API CRUD de tarefas com autenticação | Desenvolvimento | 1,5h |
| S1-06 | Validação de dados e tratamento de erros da API | Desenvolvimento | 0,5h |
| | **Total** | | **6h** |

### S1-01 — Planejamento do projeto: definir escopo e requisitos (1h)
**Descrição:** Ler o enunciado, listar requisitos obrigatórios, escolher a stack (Flask, SQLite, HTML/CSS/JS) e cadastrar as tarefas das duas Sprints no Jira.
**Critérios de conclusão:**
- Requisitos de autenticação, CRUD, frontend, backend e banco listados.
- Stack definida.
- Tarefas das Sprints 1 e 2 cadastradas com estimativas.

### S1-02 — Configuração do ambiente de desenvolvimento (1h)
**Descrição:** Preparar ambiente para backend, frontend e banco de dados.
**Critérios de conclusão:**
- Repositório Git criado e publicado no GitHub (público).
- Ambiente virtual Python com Flask instalado; `requirements.txt` e `.gitignore` criados.
- Estrutura de pastas (`app.py`, `static/`, `tests/`) criada; aplicação inicia em `http://127.0.0.1:5000`.

### S1-03 — Modelagem do banco de dados (0,5h)
**Descrição:** Criar `schema.sql` com as tabelas `users` (nome, e-mail, senha com hash) e `tasks` (título, descrição, usuário, data de criação).
**Critérios de conclusão:**
- E-mail único; título obrigatório; chave estrangeira `tasks.user_id → users.id`.
- Banco criado automaticamente ao iniciar a aplicação.

### S1-04 — Implementação da autenticação (1,5h)
**Descrição:** Criar rotas de registro, login e logout com sessão do Flask.
**Critérios de conclusão:**
- `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/logout` e `GET /api/auth/me` funcionando.
- Senhas armazenadas com hash (Werkzeug).
- E-mail duplicado retorna 409; credenciais inválidas retornam 401.

### S1-05 — Desenvolvimento do Backend – Parte 1: API CRUD de tarefas (1,5h)
**Descrição:** Implementar rotas de listar, criar, detalhar, editar e excluir tarefas, protegidas por login.
**Critérios de conclusão:**
- Rotas `GET/POST /api/tasks` e `GET/PUT/DELETE /api/tasks/<id>` funcionando.
- Sem login → 401.
- Cada usuário acessa somente as próprias tarefas (tarefa de outro usuário → 404).
- Listagem em ordem de criação.

### S1-06 — Validação de dados e tratamento de erros (0,5h)
**Descrição:** Validar entradas e padronizar respostas de erro em JSON.
**Critérios de conclusão:**
- Título vazio → 400; nome, e-mail e senha validados no registro.
- Erros 404/405/500 retornam JSON com mensagem.

---

## Sprint 2 — 6 horas

| Ref.  | Tarefa | Fase | Estimativa |
|-------|--------|------|-----------:|
| S2-01 | Desenvolvimento do Frontend – Parte 2: telas de login, registro e logout | Desenvolvimento | 1,5h |
| S2-02 | Desenvolvimento do Frontend – Parte 2: telas do CRUD de tarefas | Desenvolvimento | 1,5h |
| S2-03 | Testes funcionais | Testes | 1h |
| S2-04 | Correções dos problemas encontrados nos testes | Testes | 0,5h |
| S2-05 | Deploy da aplicação | Deploy | 0,5h |
| S2-06 | Documentação final (README, GitHub e Jira) | Deploy/Documentação | 1h |
| | **Total** | | **6h** |

### S2-01 — Frontend: login, registro e logout (1,5h)
**Descrição:** Criar telas de login e registro integradas à API, e botão de sair.
**Critérios de conclusão:**
- Usuário consegue se registrar, entrar e sair pela interface.
- Mensagens de erro exibidas (credenciais inválidas, e-mail duplicado).
- Layout utilizável em celular e desktop.

### S2-02 — Frontend: CRUD de tarefas (1,5h)
**Descrição:** Criar interface para cadastrar, listar, visualizar, editar e excluir tarefas.
**Critérios de conclusão:**
- Formulário com título obrigatório e descrição opcional.
- Lista em ordem de criação com ações Ver, Editar e Excluir (com confirmação).
- Tela de detalhes da tarefa.

### S2-03 — Testes funcionais (1h)
**Descrição:** Testar todas as funcionalidades com testes automatizados (`unittest`) e verificação manual no navegador.
**Critérios de conclusão:**
- Testados: registro/login, acesso sem autenticação, criar/listar/editar/excluir, isolamento entre usuários, título obrigatório e persistência.
- Todos os testes passando (`python -m unittest discover -s tests -v`).

### S2-04 — Correções dos problemas encontrados (0,5h)
**Descrição:** Corrigir falhas identificadas na S2-03.
**Critérios de conclusão:**
- Problemas registrados no Jira e corrigidos.
- Testes executados novamente sem falhas.

### S2-05 — Deploy da aplicação (0,5h)
**Descrição:** Publicar a aplicação em um serviço gratuito (ex.: PythonAnywhere), quando viável. Se não for viável, garantir a execução local pelas instruções do README.
**Critérios de conclusão:**
- URL pública funcionando com `SECRET_KEY` configurada; **ou**
- Justificativa registrada no Jira e execução local validada.

### S2-06 — Documentação final (1h)
**Descrição:** Finalizar README e organizar o GitHub e o Jira.
**Critérios de conclusão:**
- README com instalação, configuração, execução e testes.
- Código final enviado ao repositório público no GitHub.
- Todas as tarefas do Jira em `Concluído`, com link do repositório (e da URL de deploy, se houver).
- Sprint 2 encerrada.
