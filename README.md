# 🛡️ Desafio Técnico - Prevenção à Lavagem de Dinheiro (PLD) | Níveis 1 e 2

Este repositório contém a solução desenvolvida para o desafio técnico de **Prevenção à Lavagem de Dinheiro (PLD)** e **Antifraude**.

O objetivo do projeto é estruturar uma esteira automatizada de análise de transações financeiras, combinando **regras determinísticas de compliance (Pandas)** com a capacidade analítica e investigativa de **Agentes de IA (Google Gemini)**.

## 🎯 O Desafio de Negócio & Arquitetura da Solução

Em um ambiente bancário, a análise de PLD exige alta precisão em cálculos matemáticos para cumprir a regulação do Banco Central e do COAF, aliada à capacidade de investigar o contexto comportamental do cliente sem criar gargalos operacionais.

Para atender a esses requisitos, a solução foi dividida em duas camadas principais:

### 1. Nível 1: Camada Determinística e RAG Regulatório

* **Processamento com Pandas:** Operações de limpeza de dados, conversão cambial e aplicação de regras de negócio estritas (como a detecção de *smurfing*/fracionamento e operações atípicas acima da mediana do cliente).
* **Fundamentação por RAG:** Injeção de trechos das normativas (Circular BACEN nº 3.978/2020 e Carta Circular nº 4.001/2020) diretamente no prompt da LLM para garantir que o parecer técnico seja emitido com respaldo legal real e sem alucinações.

### 2. Nível 2: Escala com Agentes e Function Calling

* **Investigação Autônoma com** ***Tools*****:** O agente utiliza chamadas nativas de função em `nivel_2/tools.py` para consultar autonomamente apenas as informações necessárias (histórico, canais mais utilizados e perfil de risco do cliente).
* **Otimização de Lote com Paralelismo:** Para evitar gargalos de tempo no processamento do lote de 10 clientes, o fluxo foi reestruturado com `ThreadPoolExecutor`. Isso reduziu o tempo total de resposta da análise de minutos para apenas **~17 a 19 segundos**.
* **Motor de Confronto e Auditoria:** O script `nivel_2/confronto.py` cruza as marcações das regras determinísticas com as decisões finais geradas pelo Agente de IA, exportando os artefatos estruturados para conciliação em `outputs/`.

## 📂 Estrutura do Repositório

```text
.
├── ENTREGA.yaml          # Autodeclaração e status dos entregáveis do teste
├── .env.example          # Modelo de variável de ambiente (chave Gemini API)
├── docs/
│   ├── DECISOES.md       # Trade-offs, limitações reais da solução e plano do Nível 3
│   └── USO_DE_IA.md      # Governança de IA, escopo de atuação e supervisão humana
├── nivel_1/
│   └── nivel_1.ipynb     # Pipeline determinística (Pandas) e RAG regulatório
├── nivel_2/
│   ├── agente.py         # Agente LLM em lote rodando investigações em paralelo
│   ├── tools.py          # Ferramentas de consulta (histórico, canal e perfil)
│   └── confronto.py      # Motor de conciliação entre regras e parecer do agente
└── outputs/              # Relatórios de conciliação e métricas gerados (CSV/JSON)
```

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.10+
* **Engenharia e Tratamento de Dados:** Pandas
* **Modelo de Linguagem:** Google Gemini (`gemini-3.6-flash`) via SDK `google-genai`
* **Concorrência:** `concurrent.futures.ThreadPoolExecutor`
* **Integração e Formatos:** JSON, CSV, YAML e `python-dotenv`

## 🚀 Como Executar o Projeto

### 1. Clonar e Ativar Ambiente

```bash
git clone https://github.com/SouzaaCarol/teste-tecnico-banco.git
cd teste-tecnico-banco
python -m venv venv
source venv/bin/activate  # Ou .\venv\Scripts\Activate.ps1 no Windows
```

### 2. Instalar Dependências e Configurar Chave

```bash
pip install pandas google-genai python-dotenv jupyter
```

Crie o arquivo `.env` na raiz contendo:

```env
GEMINI_API_KEY=sua_chave_aqui
```

### 3. Rodar os Níveis

* **Nível 1:** Abra e execute o notebook em `nivel_1/nivel_1.ipynb`.
* **Nível 2 (Agente):** Execute `python nivel_2/agente.py` para gerar a análise do lote.
* **Nível 2 (Confronto):** Execute `python nivel_2/confronto.py` para consolidar o relatório de conciliação.

## 👩‍💻 Autora

**Ana Carolina Martins Souza**

Projeto desenvolvido como solução do desafio técnico para a área de **PLD, Antifraude, Dados e Inteligência Artificial**.
