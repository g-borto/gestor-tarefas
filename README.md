# Gestor de Tarefas

Aplicação web simples com autenticação de usuários e CRUD de tarefas, desenvolvida para a
**Prova de Suficiência da Fábrica de Software – UTFPR-DV**.

- **Backend:** Python 3 + Flask (autenticação por sessão)
- **Frontend:** HTML, CSS e JavaScript puro (responsivo)
- **Banco de dados:** SQLite (criado automaticamente na primeira execução)

## Funcionalidades

- Registro, login e logout de usuários (senhas armazenadas com hash).
- Cadastro de tarefas com título (obrigatório) e descrição (opcional).
- Listagem das tarefas em ordem de criação, visualização de detalhes, edição e exclusão.
- Cada usuário acessa somente as próprias tarefas.

## Requisitos

- Python 3.10 ou superior
- pip

## Como executar localmente

```bash
# 1. Clonar o repositório
git clone https://github.com/<seu-usuario>/gestor-tarefas.git
cd gestor-tarefas

# 2. Criar e ativar um ambiente virtual
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Executar a aplicação
python app.py
```

Acesse **http://127.0.0.1:5000** no navegador, crie uma conta e comece a cadastrar tarefas.

O banco `database.db` é criado automaticamente na pasta do projeto a partir de `schema.sql`.

### Configuração (opcional)

| Variável      | Uso                                                                                       |
|---------------|-------------------------------------------------------------------------------------------|
| `SECRET_KEY`  | Chave usada para assinar a sessão. Se não for definida, uma chave aleatória é gerada a cada execução (os usuários precisam fazer login novamente após reiniciar o servidor). **Defina-a em produção.** |
| `DATABASE`    | Caminho do arquivo SQLite (padrão: `database.db` na pasta do projeto).                     |
| `FLASK_DEBUG` | Use `1` para ativar o modo de depuração durante o desenvolvimento.                         |

Exemplo (Linux/macOS):

```bash
export SECRET_KEY="uma-chave-longa-e-aleatoria"
python app.py
```

## Testes

Os testes funcionais usam apenas a biblioteca padrão (`unittest`):

```bash
python -m unittest discover -s tests -v
```

Cobrem: registro e login, rotas protegidas sem autenticação, criação/listagem/edição/exclusão,
ordem de criação, título obrigatório, isolamento entre usuários, hash da senha e persistência.

## Estrutura do projeto

```
gestor-tarefas/
├── app.py            # Aplicação Flask (rotas de autenticação e API de tarefas)
├── schema.sql        # Tabelas users e tasks
├── requirements.txt
├── static/
│   ├── index.html    # Telas de login, registro, lista, formulário e detalhes
│   ├── style.css
│   └── app.js        # Comunicação com a API
├── tests/
│   └── test_app.py   # Testes funcionais
└── docs/
    └── JIRA.md       # Planejamento das Sprints no Jira
```

## API

Todas as rotas de tarefas exigem login (sessão). Corpo das requisições em JSON.

| Método | Rota                   | Descrição                         | Respostas principais |
|--------|------------------------|-----------------------------------|----------------------|
| POST   | `/api/auth/register`   | Registrar (`name`, `email`, `password`) | 201, 400, 409  |
| POST   | `/api/auth/login`      | Login (`email`, `password`)       | 200, 401             |
| POST   | `/api/auth/logout`     | Logout                            | 204                  |
| GET    | `/api/auth/me`         | Usuário logado                    | 200, 401             |
| GET    | `/api/tasks`           | Listar tarefas (ordem de criação) | 200, 401             |
| POST   | `/api/tasks`           | Criar (`title`, `description`)    | 201, 400, 401        |
| GET    | `/api/tasks/<id>`      | Detalhes da tarefa                | 200, 401, 404        |
| PUT    | `/api/tasks/<id>`      | Editar (`title`, `description`)   | 200, 400, 401, 404   |
| DELETE | `/api/tasks/<id>`      | Excluir                           | 204, 401, 404        |

Tarefas de outro usuário retornam **404**, sem revelar que existem.

## Gestão do projeto

O planejamento no Jira (board Kanban, duas Sprints de 6 horas) está descrito em
[`docs/JIRA.md`](docs/JIRA.md).
