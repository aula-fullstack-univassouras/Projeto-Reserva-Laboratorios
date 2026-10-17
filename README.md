# Sistema de Reservas de Laboratórios — Aulas 9, 10 e 11

Projeto integrado de programação Full Stack. O PDF identifica os conteúdos como Encontros 1, 2 e 3; conforme a organização da disciplina informada, eles correspondem respetivamente à **Aula 9 (Encontro 1), Aula 10 (Encontro 2) e Aula 11 (Encontro 3)**. Este repositório reúne a aplicação final, as alterações solicitadas, as respostas às perguntas de verificação e um guia para executar e demonstrar o projeto.

## Integrantes

1. Ângelo Mateus - 202323348
2. Esequias Ferraz De Andrade - 202411248
3. Felipe Ramos Da Silva - 202221884
4. Thiago Marsol Almeida Baião - 202323232
5. Juberto Junior Marques Coutinho - 202321179
6. Wallace Gustavo Da Silva - 202411248

## Objetivo e resultado

A aplicação permite cadastrar, listar, filtrar, consultar, editar e excluir reservas de laboratórios. A interface comunica com uma API HTTP, a API valida os dados, aplica a regra de conflito de horário e guarda os registros permanentemente numa base SQLite.

O percurso completo é:

```text
HTML/CSS → JavaScript/Fetch → HTTP → FastAPI → Pydantic → serviços/regras → SQLite
         ← resposta JSON/HTTP ←──────────────────────────────────────────────────
```

### Requisitos implementados a partir do PDF

- `GET /api/status`: devolve estado `online`, para comprovar que a API está em execução (Encontro 1). A página verifica e mostra o estado da API.
- Contrato do `POST /api/reservas` com `quantidade_alunos`, campo obrigatório inteiro entre **1 e 40**, presente no HTML, JavaScript/JSON, Pydantic e resposta da API (Encontro 2).
- CRUD completo com SQLite e persistência após reiniciar a API (Encontro 3).
- Base de dados em `dados/reservas.db`, **fora de `backend/`**, como solicitado no roteiro.
- Prevenção de conflito: duas reservas não canceladas para o mesmo laboratório, data e turno não podem coexistir. A API responde `409`.
- Filtros de coleção por status e parte do nome do laboratório, exclusão pela interface e códigos `200`, `201`, `204`, `404`, `409` e `422` de acordo com o caso.
- Testes automatizados da API.

## Estrutura do repositório

```text
exemplo_reservas_laboratorios/
├── README.md
├── .gitignore
├── backend/
│   ├── main.py              # Rotas HTTP, CORS, lifespan e códigos de resposta
│   ├── models.py            # Contratos e validação Pydantic
│   ├── services.py          # CRUD, consultas SQL e regra de conflito
│   └── requirements.txt     # Dependências Python
├── dados/
│   └── reservas.db          # Criado automaticamente na primeira execução
├── frontend/
│   ├── index.html           # Formulário, status, filtros e tabela
│   ├── styles.css           # Aparência responsiva
│   └── app.js               # Fetch, JSON, DOM e ações da interface
└── tests/
    └── test_api.py          # Testes de integração
```

`dados/` e `reservas.db` são criados automaticamente quando a aplicação inicia. O banco local está no `.gitignore`: ele não deve ser publicado com dados pessoais; o código cria uma base vazia no computador de quem clonar o repositório.

## O que foi feito em cada encontro

### Aula 9 — Encontro 1: ambiente e primeira integração

O roteiro solicita abrir a pasta raiz no VSCode, reconhecer a responsabilidade de cada camada, preparar o ambiente virtual, iniciar a API e servir o frontend por HTTP. A rota `GET /api/status` comprova o primeiro caminho navegador → JavaScript → FastAPI → JSON. O frontend chama a rota ao carregar e apresenta “API online” ou “API offline”.

**Arquivos e responsabilidades:** `backend/main.py` registra a rota de status; `backend/requirements.txt` declara as dependências; `frontend/index.html` estrutura a página; `frontend/styles.css` define aparência; `frontend/app.js` chama a API e atualiza o DOM.

**Como observar:** Swagger em `/docs`, painel Network do navegador, Console, terminal do Uvicorn e terminal do servidor estático. As falhas controladas do guia podem ser reproduzidas: parar a API produz falha de conexão; alterar temporariamente a URL da rota para uma inexistente produz 404; abrir o HTML por `file://` difere de servi-lo por `http://localhost:5500` e pode causar problemas de origem/CORS.

### Aula 10 — Encontro 2: contrato HTTP e validação

O `POST /api/reservas` recebe JSON validado pelo modelo `ReservaEntrada`. O novo campo chama-se exatamente `quantidade_alunos`, como no PDF; é obrigatório e deve ser um número inteiro de 1 a 40. O JavaScript converte o valor do campo HTML para número antes de usar `JSON.stringify`. O campo também aparece nos cartões/linhas da interface e no JSON de saída.

**Arquivos alterados:** `frontend/index.html` contém o input numérico com mínimo e máximo; `frontend/app.js` lê o valor, inclui `quantidade_alunos` no objeto enviado e renderiza a quantidade; `backend/models.py` valida `Field(ge=1, le=40)`; `backend/database.py` e `backend/services.py` persistem o valor; `tests/test_api.py` verifica limites.

### Aula 11 — Encontro 3: CRUD, regras de negócio e SQLite

A lista volátil é substituída por operações SQLite. O `lifespan` do FastAPI prepara a tabela ao iniciar. `services.py` centraliza `INSERT`, `SELECT`, `UPDATE`, `DELETE`, filtros e regra de conflito; `database.py` abre a conexão, cria a pasta `dados/` se necessário e cria a tabela. As consultas usam parâmetros SQL, evitando concatenação de valores no comando. O contexto `with conectar()` confirma alterações ao terminar com sucesso.

A aplicação oferece criar (POST/201), listar e consultar (GET/200), atualizar (PUT/200) e excluir (DELETE/204). Um ID inexistente dá 404; uma reserva que conflita dá 409. A base em arquivo permanece após encerrar e reiniciar o Uvicorn.

## Contrato e endpoints

| Método e caminho | Função | Sucesso / erros principais |
|---|---|---|
| `GET /api/status` | Verifica se a API está operacional | 200 |
| `POST /api/reservas` | Cria reserva | 201, 409 conflito, 422 validação |
| `GET /api/reservas` | Lista reservas | 200 |
| `GET /api/reservas?status_reserva=confirmada` | Filtra por status | 200 |
| `GET /api/reservas?laboratorio=Lab` | Busca trecho do nome do laboratório | 200 |
| `GET /api/reservas/{id}` | Consulta reserva por ID | 200 ou 404 |
| `PUT /api/reservas/{id}` | Substitui os campos editáveis | 200, 404 ou 409 |
| `DELETE /api/reservas/{id}` | Exclui reserva sem corpo de resposta | 204 ou 404 |

Exemplo de corpo para criação:

```json
{
  "laboratorio": "Lab 01",
  "responsavel": "Ana Lima",
  "data": "2026-10-10",
  "turno": "manha",
  "finalidade": "Aula prática",
  "quantidade_alunos": 25,
  "status": "confirmada"
}
```

Turnos válidos: `manha`, `tarde`, `noite`. Status: `confirmada`, `pendente`, `cancelada`. Reservas canceladas não impedem nova reserva do mesmo horário.

## Respostas às perguntas do PDF

### Aula 9 (Encontro 1) — Perguntas 17 a 23

**17. `app = FastAPI()` inicia o servidor? Justifique.** Não. Essa linha cria e configura o objeto ASGI da aplicação. É o Uvicorn que inicia o processo servidor, por exemplo com `python -m uvicorn main:app --reload`.

**18. Qual processo atende à porta 8000?** O servidor Uvicorn que executa a aplicação FastAPI.

**19. Qual processo atende à porta 5500?** O servidor HTTP estático iniciado por `python -m http.server 5500`, que entrega os arquivos do frontend.

**20. Onde a rota `/api/status` é definida?** Em `backend/main.py`, na função `consultar_status`, decorada com `@app.get("/api/status")`.

**21. Qual evidência comprova que a requisição alcançou o backend?** A entrada correspondente no terminal do Uvicorn (por exemplo `GET /api/status 200 OK`). A resposta 200 e o JSON no Swagger/Network também comprovam que a rota foi atendida.

**22. Por que abrir a pasta raiz no VSCode facilita a compreensão?** Permite ver frontend, backend, testes, dependências e documentação em conjunto; facilita navegar entre as camadas, rodar comandos a partir de locais conhecidos e compreender a estrutura do projeto.

**23. Qual a diferença entre Console, Network e terminal da API?** Console mostra erros JavaScript e mensagens do navegador; Network mostra cada requisição (URL, método, status, cabeçalhos, payload e resposta); terminal da API mostra o processo Uvicorn e requisições que chegaram ao FastAPI.

### Aula 10 (Encontro 2) — Perguntas 5 a 9

**5. Por que a validação HTML não substitui Pydantic?** Validação HTML ajuda a pessoa no navegador, mas pode ser contornada ou não existir em outro cliente. O backend precisa validar de forma independente tudo o que recebe; Pydantic protege o contrato para qualquer cliente.

**6. Por que `JSON.stringify` é necessário?** O objeto JavaScript existe em memória e não é, por si só, o texto JSON que será enviado no corpo HTTP. `JSON.stringify` serializa o objeto para JSON; o cabeçalho `Content-Type: application/json` informa o formato à API.

**7. Onde o código 201 é definido?** Na declaração da rota POST em `backend/main.py`, com `status_code=201`. Esse código significa que a reserva foi criada.

**8. O que acontece se o JavaScript enviar `quantidadeAlunos`?** O nome não corresponde a `quantidade_alunos`. O Pydantic não preenche o campo obrigatório esperado; a API responde 422 indicando que `quantidade_alunos` está ausente (e pode também indicar campo extra, conforme configuração). Nomes do JSON e do modelo devem coincidir.

**9. Como provar que a requisição alcançou o servidor?** Conferir a linha da requisição no terminal do Uvicorn e, no Network/Swagger, a URL, o método e a resposta HTTP. Uma resposta HTTP da API como 201 ou 422 confirma que chegou ao backend; um erro de rede sem resposta não.

### Aula 11 (Encontro 3) — Perguntas de registro

**Por que commit é necessário depois de INSERT, UPDATE e DELETE?** `commit` confirma a transação e torna as mudanças persistentes no arquivo do banco. Sem confirmação, alterações podem ser revertidas quando a conexão é fechada. Neste projeto, o `with conectar() as conn` confirma automaticamente se o bloco terminar sem erro e faz rollback em caso de falha.

**Por que Pydantic não detecta sozinho o conflito de horário?** Pydantic valida o formato e as restrições de cada pedido isoladamente. Para saber se já há reserva ativa do mesmo laboratório/data/turno, é preciso consultar o estado atual do banco e aplicar uma regra de negócio no serviço.

**Qual diferença entre `/reservas/5` e `/reservas?laboratorio=Lab`?** `/reservas/5` usa um segmento de caminho para identificar um recurso individual (ID 5). `?laboratorio=Lab` é parâmetro de consulta que filtra a coleção de reservas; não identifica uma reserva única.

**Por que DELETE retorna 204 sem JSON?** HTTP 204 significa que a operação foi concluída sem conteúdo de resposta. O cliente já sabe que o item foi removido pelo status; por convenção não se envia corpo JSON com 204.

## Passo a passo desde o início no VSCode

### 1. Abrir o projeto

1. Extraia o ZIP do projeto.
2. Abra o VSCode e escolha **Arquivo > Abrir Pasta…** (File > Open Folder).
3. Selecione a pasta raiz `exemplo_reservas_laboratorios`, não a pasta `backend` nem `frontend` isoladamente.
4. No Explorer do VSCode, confirme que aparecem `backend`, `frontend`, `tests` e `README.md`.
5. Instale a extensão **Python** da Microsoft, se ainda não estiver instalada.

### 2. Criar o ambiente Python e instalar bibliotecas

Abra **Terminal > Novo Terminal**. Os comandos abaixo partem da raiz do projeto.

**Windows PowerShell:**

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Se o PowerShell bloquear a ativação, execute apenas nessa janela: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, e depois repita a ativação. Alternativamente use Command Prompt e `.venv\Scripts\activate.bat`.

**macOS/Linux:**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Confirme `python --version` e `python -m pip --version`. No VSCode, `Ctrl+Shift+P` (macOS: `Cmd+Shift+P`) → **Python: Select Interpreter** → escolha o Python dentro de `backend/.venv`.

### 3. Iniciar o backend

No mesmo terminal, ainda dentro de `backend`, rode:

```bash
python -m uvicorn main:app --reload
```

Mantenha esse terminal aberto. A API escuta em `http://127.0.0.1:8000`. O `lifespan` cria a pasta `dados/` e o arquivo `dados/reservas.db` na raiz do projeto. Abra `http://127.0.0.1:8000/docs` e execute `GET /api/status`; o esperado é código 200 e JSON com `"status": "online"`.

### 4. Iniciar o frontend num segundo terminal

No VSCode, escolha **Terminal > Novo Terminal**. Se o novo terminal não estiver na raiz, volte à raiz com `cd ..` conforme necessário.

**Windows:**
```powershell
cd frontend
py -m http.server 5500
```
**macOS/Linux:**
```bash
cd frontend
python3 -m http.server 5500
```

Mantenha também este terminal aberto e visite `http://localhost:5500`. A página deve informar que a API está online. Não abra `index.html` por duplo clique: use o servidor HTTP para ter a origem permitida pelo CORS.

### 5. Exercitar a aplicação

1. Preencha os campos do formulário. Para `Quantidade de alunos`, experimente primeiro `25`.
2. Salve e observe a reserva na tabela e a resposta 201 no Network.
3. Tente quantidade `1` e `40`: são valores válidos. `0`, `41` e campo ausente devem resultar em 422 se enviados pelo Swagger/API.
4. Crie uma reserva ativa e tente outra com mesmo laboratório, data e turno: a segunda deve retornar 409.
5. Use os filtros, edite uma reserva e exclua outra. Exclusão bem-sucedida retorna 204.
6. Crie uma reserva, pare e reinicie o Uvicorn: o registro deve continuar, pois está no SQLite em disco.
7. Consulte `GET /api/reservas/999999` (ou outro ID inexistente): resultado 404.

### 6. Ver as evidências no navegador

Abra as ferramentas de desenvolvedor com `F12` → **Network**. Limpe os registros, recarregue a página e selecione `status` ou `reservas`. Registre URL, método, status, payload e response. O terminal do Uvicorn exibe também as chamadas atendidas. **Console** é usado para erros JavaScript/CORS; **Network** para tráfego HTTP; terminal Uvicorn para evidência de chegada ao backend.

Para gerar as capturas pedidas pelo roteiro, tire capturas de tela no seu próprio VSCode/navegador mostrando: (A) árvore de arquivos; (B) ambiente/dependências e os dois servidores em execução; (C) `/api/status` com 200; (D) interface indicando API online; (E) requisição de criação 201 e uma validação 422; (F) persistência após reinício; (G) conflito 409 e ausência 404. Evidências visuais dependem da execução local e não são arquivos pré-fabricados neste repositório.

## Testes automatizados

Ative o ambiente virtual no terminal. Na raiz do projeto, execute:

```bash
python -m pytest -v
```

Os testes verificam status da API, criação/listagem/consulta, conflito 409, validação 422, filtros, exclusão 204/404 e quantidade de alunos. Os testes limpam a tabela antes de cada caso; não os execute se quiser preservar dados reais já armazenados na base local. Para demonstração, use dados descartáveis.

## Resolução de problemas

- **`uvicorn` não encontrado:** confirme que o ambiente `(.venv)` está ativo e instale `pip install -r requirements.txt`; use `python -m uvicorn main:app --reload`.
- **Interface diz API offline / `Failed to fetch`:** confirme o terminal do backend, a porta 8000 e o endereço `127.0.0.1`.
- **Erro CORS:** acesse a interface exatamente por `http://localhost:5500` ou `http://127.0.0.1:5500`, não por `file://`.
- **404:** confirme rota e ID; `/api/statu` é diferente de `/api/status`.
- **422:** confira o payload e os nomes do contrato; `quantidade_alunos` é obrigatório e inteiro de 1 a 40.
- **409:** já existe reserva não cancelada para o mesmo laboratório, data e turno; mude um desses valores ou cancele a reserva existente.
- **Porta ocupada:** encerre o processo que usa a porta ou configure outra porta e ajuste as origens CORS correspondentes.
