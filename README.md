# CineAI Backend

Este é o back-end do projeto CineAI, um sistema de auxílio a roteiristas utilizando Inteligência Artificial.

## 🚀 Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e de alta performance.
- **MongoDB (CosmoDB)**: Banco de dados NoSQL para persistência de chats e usuários.
- **OpenAI / OpenRouter**: Integração com modelos de linguagem (Gemini, Stepfun, Minimax, Gemma).
- **JWT (PyJWT)**: Autenticação baseada em tokens.
- **Argon2**: Hashing de senhas seguro.
- **Pydantic**: Validação de dados e esquemas.

## 🏗️ Arquitetura do Projeto

O projeto segue uma **Arquitetura Multicamada (Layered Architecture)** para garantir escalabilidade, testabilidade e manutenibilidade:

```text
src/
├── api/            # Camada de Apresentação (FastAPI Routers e Dependências)
│   └── v1/         # Versão 1 da API
├── core/           # Configurações globais, segurança e constantes
├── db/             # Inicialização da conexão com o banco de dados
├── models/         # Modelos de domínio e tipos (Enums)
├── repositories/   # Camada de Acesso a Dados (Interação com MongoDB)
├── services/       # Camada de Regras de Negócio (Lógica de Auth, IA)
└── schemas/        # Esquemas de validação Pydantic (Request/Response)
```

### Por que esta arquitetura?
1. **Separação de Preocupações (SoC)**: A lógica de banco de dados não se mistura com a lógica de roteamento.
2. **Reutilização**: Repositórios e serviços podem ser usados em diferentes partes do sistema.
3. **Facilidade de Teste**: É fácil criar mocks para serviços ou repositórios em testes unitários.

## 📋 Funcionalidades

- **Autenticação**: Login, Registro, Logout e Refresh Token (via Cookies HttpOnly).
- **Conversas**:
  - Criação de novos chats.
  - Listagem e deleção de conversas.
  - Atualização de títulos.
  - Histórico de mensagens persistente.
- **Inteligência Artificial**:
  - Respostas em tempo real (Streaming).
  - Suporte aos modelos Gemini 3 Flash, Stepfun 3.5 Flash, Minimax M2.5 e Gemma 4.
  - Personas configuráveis (ex: Roteirista).

## 🛠️ Como Executar

### Pré-requisitos
- Python 3.10+
- Instância do MongoDB (ou CosmoDB)
- API Key do OpenRouter (ou OpenAI)

### Instalação

1.  Clone o repositório:
    ```bash
    git clone https://github.com/seu-usuario/cineai-back.git
    cd cineai-back
    ```

2.  Crie um ambiente virtual e ative-o:
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Linux/Mac:
    source venv/bin/activate
    ```

3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4.  Configure as variáveis de ambiente:
    Crie um arquivo `.env` na raiz do projeto com:
    ```env
    DATABASE_URL=seu_mongodb_url
    API_KEY=sua_openrouter_api_key
    SECRET_KEY=sua_chave_secreta_jwt
    FRONTEND_URLS=http://localhost:5173
    DEVELOPMENT=true
    ```

5.  Execute o servidor:
    ```bash
    python main.py
    ```
    A API estará disponível em `http://localhost:8000/api/v1`.
    A documentação automática (Swagger) pode ser acessada em `http://localhost:8000/docs`.

## 🧪 Testes

O projeto utiliza **Pytest** para testes unitários e de integração.

### Como Executar os Testes

1.  Instale as dependências de desenvolvimento:
    ```bash
    pip install -r requirements-dev.txt
    ```

2.  Execute todos os testes:
    ```bash
    pytest
    ```

## 📜 Licença

Este projeto é para fins acadêmicos.
