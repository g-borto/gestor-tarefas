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
└── tests/
    └── test_app.py   # Testes funcionais
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

## Deploy

A aplicação está publicada no PythonAnywhere:
**https://bortolotto.pythonanywhere.com**

### Como foi feito o deploy (PythonAnywhere)

1. Criar uma conta gratuita (*Beginner*) em https://www.pythonanywhere.com.
2. Abrir um console **Bash** e executar:
   ```bash
   git clone https://github.com/<seu-usuario>/gestor-tarefas.git
   cd gestor-tarefas
   pip3.10 install --user -r requirements.txt
   python3.10 -c "import secrets; print(secrets.token_hex(32))"   # gera a SECRET_KEY
   ```
3. Na aba **Web**: **Add a new web app** → **Manual configuration** → **Python 3.10**.
4. Em **Code**, definir *Source code* e *Working directory* como `/home/<usuario>/gestor-tarefas`.
5. Substituir o conteúdo do **WSGI configuration file** por:
   ```python
   import os
   import sys

   path = '/home/<usuario>/gestor-tarefas'
   if path not in sys.path:
       sys.path.insert(0, path)

   os.environ['SECRET_KEY'] = '<chave-gerada-no-passo-2>'

   from app import create_app
   application = create_app()
   ```
6. Clicar em **Reload** e acessar `https://<usuario>.pythonanywhere.com`.

Para atualizar após novos commits: `cd ~/gestor-tarefas && git pull` no console e **Reload** na aba Web.

> A `SECRET_KEY` fica apenas no arquivo WSGI do servidor e não é versionada no repositório.
