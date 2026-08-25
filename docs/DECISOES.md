# 📝 Registro de Decisões Técnicas

Este documento reúne as principais decisões tomadas durante o desenvolvimento dos exercícios do desafio de Prevenção à Lavagem de Dinheiro (PLD).

---

# Nível 1

## 1. Limpeza e Tratamento dos Dados

* **Datas Nulas:** Optei por remover linhas sem data informada (`dropna`), pois as regras que analisam movimentações no mesmo dia dependem de uma marcação temporal correta.
* **Conversão de Moeda:** As transações em `USD` foram convertidas para `BRL` utilizando a taxa definida no arquivo de configuração, mantendo os cálculos dos limites em uma única moeda.
* **Padronização de Tipos:** As datas foram convertidas para `datetime` utilizando Pandas, facilitando a ordenação e os agrupamentos por dia.

## 2. Pandas vs. IA Generativa

**Decisão:** Os cálculos foram realizados no Python/Pandas e a IA foi utilizada apenas para gerar o parecer.

**Por quê:** Regras como soma de transações, quantidade de operações e identificação de valores atípicos precisam ser determinísticas e fáceis de verificar.

O Gemini recebe os resultados já processados e utiliza essas informações para gerar o parecer descritivo, indicando o risco e as possíveis *red flags*.

## 3. Regras Determinísticas

Foram implementadas regras simples para identificar comportamentos que merecem atenção:

* **Fracionamento (*Smurfing*):** Identifica 3 ou mais movimentações no mesmo dia que, juntas, ultrapassam R$ 50.000,00, com valores individuais menores que R$ 20.000,00.
* **Valor Atípico:** Identifica transações que ultrapassam 5 vezes a mediana histórica do cliente, considerando clientes com pelo menos 4 transações no histórico.

A escolha por regras determinísticas permite que os critérios sejam reproduzidos e verificados sem depender da interpretação da IA.

## 4. Uso de RAG

**Decisão:** Utilizei RAG para fornecer referências regulatórias ao Gemini durante a geração do parecer.

A base contém referências à **Circular BACEN nº 3.978/2020** e à **Carta Circular nº 4.001/2020**.

Quando uma regra é identificada, o sistema busca a referência correspondente e envia essa informação para a IA junto com os dados da análise.

**Por quê:** A ideia foi reduzir o risco de a IA criar ou citar incorretamente uma norma, fornecendo a fonte diretamente no contexto da geração do parecer.

---

# Níveis 2 e 3

## 1. Processamento paralelo vs. sequencial

**Decisão:** Utilizei `ThreadPoolExecutor` para processar os clientes em paralelo.

**Por quê:** O processamento sequencial demorava muito e poderia ultrapassar o tempo disponível para execução. Com as chamadas paralelas, o lote de 10 clientes passou a ser processado em aproximadamente **17 a 19 segundos**.

**Trade-off:** A execução fica mais rápida, mas adiciona complexidade relacionada à concorrência e ao acesso simultâneo a recursos.

**Com mais tempo:** Melhoraria o tratamento de erros e estudaria uma abordagem assíncrona com controle de tentativas (*retry*) e limites de chamadas.

## 2. Cálculos no Python vs. IA

**Decisão:** Mantive os cálculos e regras no Python/Pandas, deixando a IA responsável pela geração do parecer.

**Por quê:** Essa abordagem mantém os resultados determinísticos e mais fáceis de verificar, evitando depender da IA para cálculos numéricos.

## 3. Tools vs. envio de todos os dados

**Decisão:** No Nível 2, utilizei *tools* para que a IA pudesse consultar os dados do cliente conforme a necessidade.

**Por quê:** Achei mais organizado e eficiente do que enviar todo o conjunto de dados para o modelo de uma vez. A IA consulta apenas as informações necessárias para aquela investigação.

**Trade-off:** A solução fica um pouco mais complexa, pois é necessário criar e controlar as funções disponíveis para a IA.

## 4. Escolha da Trilha A no Nível 3

**Decisão:** Escolhi a **Trilha A — Fluxo multiagente**, com os papéis de **Triador, Investigador e Redator**.

**Por quê:** Achei essa abordagem interessante porque permite dividir a investigação em etapas e automatizar melhor o processo.

A ideia seria:

`Triador → Investigador → Redator → Finalização`

O Triador decidiria se o caso precisa continuar, o Investigador utilizaria as *tools* do Nível 2 e o Redator produziria o parecer final.

**Limitação:** Não consegui implementar o Nível 3 devido ao tempo disponível para realizar o desafio, principalmente por conciliar o desenvolvimento com meu trabalho presencial. Por isso, a Trilha A ficou como a arquitetura planejada para uma próxima etapa.

**Com mais tempo:** Implementaria o fluxo com um estado compartilhado entre os agentes e uma condição de parada, validando cada etapa com casos de teste.

## 5. Limitações de Escalabilidade

A solução atual mantém os dados em memória e utiliza arquivos locais. Isso é suficiente para o volume utilizado no desafio, mas poderia gerar problemas com uma quantidade muito maior de clientes.

**Com mais tempo:** Utilizaria um banco de dados para consultar os dados sob demanda e melhoraria o controle de acesso aos arquivos durante o processamento paralelo.

---

## Considerações Finais

As decisões buscaram equilibrar **simplicidade, tempo de execução e confiabilidade**, considerando o escopo e o tempo disponível para cada exercício.

No Nível 1, o foco foi garantir regras determinísticas e um parecer com referências regulatórias. No segundo exercício, o foco foi explorar o uso de **IA com ferramentas e processamento paralelo**, deixando como próximo passo a implementação do fluxo multiagente da **Trilha A**.