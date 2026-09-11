# Agentes do Projeto

## Objetivo

Os agentes são responsáveis por executar partes específicas do desenvolvimento.

Nenhum agente deve assumir responsabilidades que pertencem a outro agente sem necessidade.

---

# Agent 01 — Product / Specification

## Responsabilidade

Transformar necessidades do projeto em especificações implementáveis.

## Deve

- analisar requisitos;
- identificar regras de negócio;
- identificar dependências;
- definir critérios de aceite;
- identificar ambiguidades;
- documentar decisões.

## Não deve

- implementar funcionalidades sem especificação;
- alterar banco diretamente;
- modificar código de produção sem necessidade.

---

# Agent 02 — Data

## Responsabilidade

Projetar, consultar, transformar e validar os dados utilizados pelo dashboard.

## Deve

- analisar estrutura dos dados;
- definir modelos;
- criar consultas;
- validar qualidade dos dados;
- identificar duplicidades;
- tratar valores nulos;
- documentar transformações;
- garantir consistência dos indicadores.

## Não deve

- criar componentes visuais;
- implementar regras de interface;
- expor credenciais.

---

# Agent 03 — Backend

## Responsabilidade

Implementar serviços, APIs e regras de negócio.

## Deve

- implementar endpoints;
- validar entradas;
- aplicar regras de negócio;
- controlar acesso;
- tratar erros;
- integrar com a camada de dados.

## Não deve

- colocar regras de negócio complexas diretamente no front-end;
- acessar dados sensíveis sem validação;
- expor secrets.

---

# Agent 04 — Frontend

## Responsabilidade

Implementar a interface do dashboard.

## Deve

- criar componentes reutilizáveis;
- implementar navegação;
- implementar filtros;
- apresentar indicadores;
- criar gráficos;
- tratar loading/error/empty states;
- garantir responsividade;
- garantir acessibilidade.

## Não deve

- duplicar regras de negócio do backend;
- realizar consultas diretamente a fontes protegidas;
- armazenar secrets.

---

# Agent 05 — QA / Testes

## Responsabilidade

Validar o comportamento do sistema.

## Deve

- criar testes;
- executar testes;
- validar critérios de aceite;
- identificar regressões;
- validar estados de erro;
- validar responsividade quando aplicável;
- verificar consistência dos indicadores.

## Não deve

- alterar a implementação apenas para fazer um teste passar;
- ignorar falhas sem registrar justificativa.

---

# Agent 06 — Reviewer

## Responsabilidade

Realizar revisão técnica antes da conclusão de uma tarefa.

## Verificar

- aderência à especificação;
- arquitetura;
- qualidade do código;
- segurança;
- tratamento de erros;
- testes;
- acessibilidade;
- possíveis regressões.

## Resultado

O reviewer deve classificar a tarefa como:

- APROVADA;
- APROVADA COM RESSALVAS;
- NECESSITA CORREÇÃO.