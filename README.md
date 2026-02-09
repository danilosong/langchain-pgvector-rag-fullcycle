# Ingestão e Busca Semântica com LangChain e PostgreSQL

Este projeto implementa um sistema de RAG (Retrieval-Augmented Generation) que ingere um PDF em um banco de dados vetorial (PostgreSQL + pgVector) e permite fazer perguntas sobre o conteúdo via CLI.

## Tecnologias

- **Python 3.10+**
- **LangChain** (Orquestração)
- **PostgreSQL** + **pgVector** (Banco Vetorial)
- **OpenAI** ou **Gemini** (Embeddings e LLM)
- **Docker** (Execução do Banco)

## Estrutura

```
├── docker-compose.yml   # Banco de dados
├── requirements.txt     # Dependências Python
├── .env.example         # Template de Variáveis de Ambiente
├── src/
│   ├── ingest.py        # Ingestão do PDF
│   ├── search.py        # Lógica de Busca
│   └── chat.py          # Interface de Chat CLI
├── document.pdf         # Arquivo alvo (exemplo)
└── README.md
```

## Configuração

1. **Crie e ative um ambiente virtual:**
   ```bash
   apt install python3.13-venv
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente:**
   Copie o arquivo `.env.example` para `.env` e adicione sua chave (OpenAI ou Google).
   ```bash
   cp .env.example .env
   # Edite o .env com sua chave
   ```

> **Nota:** No Ubuntu, é essencial usar o ambiente virtual (`venv`) como descrito no passo 1 para evitar erros de permissão (`externally-managed-environment`).


4. **Inicie o Banco de Dados:**
   ```bash
   docker compose up -d
   ```

## Execução (Padrão)

Conforme os requisitos do projeto, a execução dos scripts Python é feita localmente:

1. **Crie ou Adicione um PDF:**
   Você pode gerar um PDF de exemplo com o script fornecido:
   ```bash
   python create_sample_pdf.py
   ```
   Ou coloque seu próprio arquivo como `document.pdf` na raiz.

2. **Execute a Ingestão:**
   Isso lerá o PDF, criará os embeddings e salvará no Postgres.
   ```bash
   python src/ingest.py
   ```

3. **Inicie o Chat:**
   Faça perguntas sobre o documento.
   ```bash
   python src/chat.py
   ```

## Execução via Docker (Opcional/Bônus)

Caso prefira rodar tudo em containers (ignorando o `venv` local):

1. **Suba tudo e construa a imagem:**
   ```bash
   docker compose up -d --build
   ```

2. **Execute via Docker:**
   ```bash
   docker compose run --rm app python src/ingest.py
   docker compose run --rm app python src/chat.py
   ```

## Funcionalidades

- **Ingestão**:
  - Chunks de 1000 caracteres (overlap 150).
  - Embeddings usando OpenAI (`text-embedding-3-small`) ou Gemini (`embedding-001`).
- **Busca**:
  - Busca vetorial com distância (similarity search).
  - Retorna top 10 resultados.
- **Chat**:
  - Responde apenas com base no contexto.
  - Responde "Não tenho informações necessárias..." para perguntas fora do escopo.
