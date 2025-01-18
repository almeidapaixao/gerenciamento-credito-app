
# Gerenciamento de Crédito

## DOCUMENTAÇÃO IMPORTANTE (2 <DOIS> LINKS ABAIXO):

- [Design low level da aplicação, com detalhes internos ->](https://miro.com/welcomeonboard/akVrWDRLcVVsc2hpZTQ4eHlqMmZBUVF1MGkxUDdPQVNTQ1AweFF0Z21uWGcrdVVYT1pFdGpQbyttN2NDTU8vUy82dmpoV2RHdXBHanllYld0bitsbVhDZWY2ajZGem9YSlhCUVZBRjRWWjJtZjVmVTZUQ0hBTTFGZTRpc2hMR3MhZQ==?share_link_id=366214079812)

- [Design high-level, com a arquitetura completa da aplicação ->](https://miro.com/welcomeonboard/UW5wOHR6MWhIOXR4ZzhmcWV1NU9tbk0rcnVGSTRVT1BRYnE0ZUw1c0JQZlVDMW9qMWhuVlFSNnh5QithZmVMNG1rVG94YklTaUNHM2hybDgwL3pxK0hDZWY2ajZGem9YSlhCUVZBRjRWWjJtZjVmVTZUQ0hBTTFGZTRpc2hMR3MhZQ==?share_link_id=301784557842)

Este é um sistema de **Gerenciamento de Crédito** desenvolvido em Django, que gerencia contratos de crédito, permite consultas com filtros, e oferece um endpoint de resumo para obter informações agregadas sobre os contratos. A aplicação também utiliza JWT para autenticação e implementa rate limiting para evitar abuso de API.

## Funcionalidades

- **Criação, Listagem, Atualização e Exclusão de Contratos**.
- **Filtros**:
  - Filtragem por **ID** do contrato.
  - Filtragem por **CPF** do tomador.
  - Filtragem por **Data de Emissão** do contrato.
  - Filtragem por **Estado** do endereço do tomador.
- **Resumo dos Contratos**: Endpoint que retorna informações agregadas sobre os contratos, como o valor total a receber, valor total desembolsado, número total de contratos e a taxa média dos contratos.
- **Autenticação via JWT**: Tokens JWT são utilizados para autenticação, incluindo tokens com validade de 30 dias.
- **Rate Limiting**: Limita as requisições a 50 por minuto por usuário para evitar sobrecarga do servidor.

## Tecnologias Utilizadas

- **Django** (Framework para backend)
- **Django REST Framework** (API para o backend)
- **Django Simple JWT** (Autenticação via JWT)
- **SQLite** (Banco de dados)
- **Gunicorn** (Servidor de produção)

## Endpoints Disponíveis

### 1. **`POST /api/token/`** – Obtenção de Token JWT

- **Descrição**: Obtém um token de acesso e um token de atualização para o usuário autenticado.
- **Autenticação**: Não é necessário.
- **Parâmetros**:
  - `username`: Nome de usuário.
  - `password`: Senha do usuário.
- **Resposta**:
  - `access`: Token de acesso (válido por 5 minutos).
  - `refresh`: Token de atualização.
  
**Exemplo de resposta**:
```json
{
  "access": "access_token_here",
  "refresh": "refresh_token_here"
}
```

### 2. **`POST /api/token/30days/`** – Obtenção de Token de 30 Dias

- **Descrição**: Obtém um token de acesso válido por 30 dias para o usuário autenticado.
- **Autenticação**: Requer autenticação via JWT.
- **Resposta**:
  - `access`: Token de acesso válido por 30 dias.
  
**Exemplo de resposta**:
```json
{
  "access": "30_days_access_token_here",
  "refresh": "refresh_token_here"
}
```

### 3. **`/api/contratos/`** – CRUD para Contratos

- **Descrição**: Endpoint para **listar**, **criar**, **atualizar** e **deletar** contratos.
- **Autenticação**: Requer autenticação via JWT.
  
#### A. **GET /api/contratos/** – Listar Contratos
  - **Descrição**: Retorna a lista de contratos cadastrados.
  - **Filtros**:
    - `id`: Filtra pelo ID do contrato.
    - `cpf`: Filtra pelo CPF do tomador.
    - `data_emissao`: Filtra pela data de emissão do contrato.
    - `estado`: Filtra pelo estado do endereço do tomador.
  
  **Exemplo de resposta**:
  ```json
  [
    {
      "id": 1,
      "data_emissao": "2025-01-17",
      "data_nascimento_tomador": "1990-05-10",
      "valor_desembolsado": 1000.00,
      "numero_documento": "12345678901",
      "endereco_tomador": {"estado": "SP", "cidade": "São Paulo", "pais": "Brasil"},
      "telefone_tomador": "11987654321",
      "taxa_contrato": 5.00
    }
  ]
  ```

#### B. **POST /api/contratos/** – Criar Contrato
  - **Descrição**: Cria um novo contrato de crédito.
  - **Exemplo de dados para criação**:
  ```json
  {
    "data_emissao": "2025-01-18",
    "data_nascimento_tomador": "1992-02-20",
    "valor_desembolsado": 1500.00,
    "numero_documento": "10987654321",
    "endereco_tomador": {"estado": "RJ", "cidade": "Rio de Janeiro", "pais": "Brasil"},
    "telefone_tomador": "2123456789",
    "taxa_contrato": 7.00,
    "parcelas": [
      {"numero_parcela": 1, "valor_parcela": 300.00, "data_vencimento": "2025-03-01"}
    ]
  }
  ```

#### C. **PUT /api/contratos/{id}/** – Atualizar Contrato
  - **Descrição**: Atualiza os dados de um contrato existente.
  - **Exemplo de dados para atualização**:
  ```json
  {
    "data_emissao": "2025-01-18",
    "data_nascimento_tomador": "1992-02-20",
    "valor_desembolsado": 1600.00,
    "numero_documento": "10987654321",
    "endereco_tomador": {"estado": "MG", "cidade": "Belo Horizonte", "pais": "Brasil"},
    "telefone_tomador": "31987654321",
    "taxa_contrato": 6.00,
    "parcelas": [
      {"numero_parcela": 1, "valor_parcela": 350.00, "data_vencimento": "2025-03-10"}
    ]
  }
  ```

#### D. **DELETE /api/contratos/{id}/** – Deletar Contrato
  - **Descrição**: Deleta um contrato existente.

### 4. **`GET /api/contratos/resumo/`** – Resumo dos Contratos

- **Descrição**: Retorna um resumo dos contratos, com valores agregados como:
  - **valor_total_a_receber**: Soma total dos valores das parcelas.
  - **valor_total_desembolsado**: Soma total dos valores desembolsados.
  - **numero_total_de_contratos**: Número total de contratos.
  - **taxa_media_dos_contratos**: Taxa média dos contratos.

- **Filtros**:
  - `cpf`: Filtra pelo CPF do tomador.
  - `data_emissao`: Filtra pela data de emissão.
  - `estado`: Filtra pelo estado do tomador.

**Exemplo de resposta**:
```json
{
  "valor_total_a_receber": 2500.00,
  "valor_total_desembolsado": 2500.00,
  "numero_total_de_contratos": 5,
  "taxa_media_dos_contratos": 5.0
}
```

## Configuração do Projeto

### Banco de Dados

- O projeto está configurado para usar **SQLite** como banco de dados.
- A aplicação cria automaticamente o banco de dados na primeira execução.
  
### Rate Limiting

- **Limite de 50 requisições por minuto** para cada usuário autenticado.
- A limitação é configurada com o Django REST Framework e a classe `UserRateThrottle`.

### Token de Autenticação

- O **Token JWT** é utilizado para autenticação.
- O token de acesso padrão tem uma expiração de 5 minutos.
- O token de acesso de 30 dias pode ser obtido através do endpoint `/api/token/30days/` com o token de acesso padrão (Bearer <token de acesso padrão>)
- Após gerar o token de 30 dias, ele será valido pelos próximos 30 dias, tendo a necessidade de renovar
por questões de segurança.

## Como Rodar o Projeto Localmente

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/seu_usuario/gerenciamento_credito.git
   cd gerenciamento_credito
   ```

2. **Crie um ambiente virtual**:
   ```bash
   python -m venv venv
   ```

3. **Ative o ambiente virtual**:
   - **Windows**: `venv\Scripts\activate`
   - **Linux/Mac**: `source venv/bin/activate`

4. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Aplique as migrações**:
   ```bash
   python manage.py migrate
   ```

6. **Crie um superusuário** (opcional, para acessar o admin):
   ```bash
   python manage.py createsuperuser
   ```

7. **Rodando o servidor de desenvolvimento**:
   ```bash
   python manage.py runserver
   ```
