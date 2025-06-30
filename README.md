# Monitor de Preço de Bitcoin com Kestra e Streamlit

Este projeto monitora o preço do Bitcoin em tempo real, armazena os dados em um banco de dados PostgreSQL e os exibe em um dashboard interativo construído com Streamlit. A orquestração do pipeline de dados é feita com o Kestra.

## Dashboard

![Dashboard](img/dashboard.png)

## Arquitetura

![Diagrama](img/diagram.png)

## Funcionalidades

- **Coleta de Dados:** Busca o preço do Bitcoin a cada 5 minutos utilizando a biblioteca `yfinance`.
- **Armazenamento:** Salva o histórico de preços em um banco de dados PostgreSQL.
- **Orquestração:** Utiliza o Kestra para automatizar o processo de coleta e armazenamento de dados.
- **Visualização:** Apresenta um dashboard com o histórico de preços das últimas 24 horas, atualizável em tempo real.

## Como Executar

Existem duas maneiras de executar o projeto: manualmente ou com o Kestra (recomendado).

### Pré-requisitos

- Python 3.12 ou superior
- Docker e Docker Compose

### 1. Execução com Kestra (Recomendado)

Esta abordagem utiliza o Kestra para orquestrar o fluxo de dados de forma automática.

**Passo 1: Configurar Variáveis de Ambiente**

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis de ambiente para o banco de dados se quiser usar o mesmo banco do Kestra:

```
DB_HOST=postgres
DB_PORT=5432
DB_NAME=kestra
DB_USER=kestra
DB_PASSWORD=k3str4
```

Caso queira utilizar um banco de dados diferente, configure as variáveis de ambiente conforme suas preferências.

**Passo 2: Iniciar os Serviços com Docker Compose**

O `docker-compose.yml` irá configurar e iniciar os contêineres do Kestra e do PostgreSQL.

```bash
docker-compose up -d
```

**Passo 3: Configurar o Flow no Kestra**

1. Acesse a interface do Kestra em `http://localhost:8080`.
2. Crie um novo "Flow".
3. Copie o conteúdo do arquivo `flows/bitcoin_flow.yml` e cole no editor do Kestra.
4. Salve e ative o Flow.

O Kestra irá executar o fluxo a cada 5 minutos, coletando e salvando o preço do Bitcoin.

### 2. Execução Manual do Script

Você pode executar o script de coleta de dados manualmente.

**Passo 1: Instalar Dependências**

```bash
pip install -r requirements.txt 
# ou, se você usa uv:
uv pip install -r requirements.txt
```

**Passo 2: Executar o Script**

```bash
python src/scripts/bitcoin.py
```

O script irá criar a tabela no banco de dados (se não existir) e começará a coletar e salvar os dados a cada 5 minutos.

## Dashboard com Streamlit

O dashboard exibe os dados coletados e armazenados no banco de dados.

### Como Executar o Dashboard

**Passo 1: Certifique-se de que o `.env` está configurado**

O Streamlit usará o mesmo arquivo `.env` para se conectar ao banco de dados.

**Passo 2: Iniciar a Aplicação Streamlit**

```bash
streamlit run src/app.py
```

Acesse `http://localhost:8501` no seu navegador para ver o dashboard.

## Estrutura do Projeto

```
.
├── flows/
│   └── bitcoin_flow.yml      # Definição do Flow para o Kestra
├── src/
│   ├── scripts/
│   │   └── bitcoin.py        # Script para coleta manual de dados
│   └── app.py                # Aplicação Streamlit para o dashboard
├── .env.example              # Exemplo de arquivo de variáveis de ambiente
├── docker-compose.yml        # Arquivo de configuração do Docker Compose
├── pyproject.toml            # Dependências do projeto
└── README.md                 # Este arquivo
```
