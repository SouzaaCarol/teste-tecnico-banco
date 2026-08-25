# 🤖 Registro de Uso de Inteligência Artificial

Este documento descreve como a Inteligência Artificial foi utilizada como apoio técnico e como parte da solução nos exercícios realizados.

---

# Nível 1

## 1. IA como apoio ao desenvolvimento

Utilizei o **Google Gemini** como apoio para:

- Interpretar os requisitos;
- Auxiliar no desenvolvimento em Python/Pandas;
- Pesquisar sobre a API;
- Estruturar prompts e respostas em JSON;
- Identificar e corrigir erros.

## 2. Uso da IA na solução

O Gemini foi utilizado para gerar o **parecer descritivo de PLD** a partir dos resultados calculados pelo Pandas.

Os cálculos e regras de risco permaneceram no código para garantir resultados determinísticos.

## 3. Engenharia de Prompt

Testei um prompt aberto e um prompt estruturado com instruções e formato JSON.

Optei pelo prompt estruturado por gerar respostas mais objetivas, padronizadas e fáceis de utilizar no código.

## 4. RAG

Utilizei RAG para fornecer ao Gemini referências das normas de PLD utilizadas no exercício, reduzindo o risco de geração de informações regulatórias incorretas.

---

# Exercício 2 — Nível 2

## 1. IA como apoio técnico

Utilizei a IA para pesquisar a documentação da `google-genai`, resolver dúvidas de implementação e auxiliar na otimização do processamento.

## 2. Processamento paralelo

Utilizei `ThreadPoolExecutor` para processar os clientes em paralelo.

A mudança reduziu o tempo do lote de 10 clientes para aproximadamente **17 a 19 segundos**.

## 3. Function Calling

O Gemini foi configurado para utilizar **Function Calling (*tools*)**, permitindo consultar informações do cliente conforme a necessidade durante a investigação.

> **Observação:** A IA foi utilizada como ferramenta de apoio, pesquisa e desenvolvimento. As regras de negócio e decisões técnicas foram revisadas durante a implementação.