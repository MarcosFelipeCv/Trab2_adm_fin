# Analisador de Investimentos e Estrutura de Capital

Projeto acadêmico para a disciplina de Administracao Financeira.

O sistema expande o Trabalho 1 e continua usando dados reais do Yahoo Finance via `yfinance`, mas agora tambem cobre temas da segunda metade do curso:

- Gestao de Investimentos;
- CAPM e risco sistemático;
- Estrutura de Capital;
- Custo medio ponderado de capital (WACC);
- Diagnostico de alavancagem e endividamento;
- Resumo consolidado da analise na propria pagina.

## Alunos

Marcos Felipe Flores Cavalieri - 2020054692

Bianca Gabriela Franco e Silva - 2020092756

## Como Rodar

### 1. Requisitos

Python instalado na máquina.

Conexao ativa com a internet, necessária para buscar dados reais no Yahoo Finance.

### 2. Instalação

Dentro da pasta principal do projeto, execute:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Execução

Inicie o servidor local:

```bash
python app.py
```

Depois acesse:

```text
http://127.0.0.1:5000
```

## Como Usar

### Analise de uma empresa

Digite um ticker, por exemplo:

```text
PETR4
```

O sistema normaliza automaticamente tickers brasileiros comuns para o sufixo `.SA`.

### Analise de carteira

Digite varios tickers separados por espaço, vírgula ou ponto e vírgula:

```text
PETR4 VALE3 ITUB4
```

Opcionalmente, informe pesos:

```text
50 30 20
```

Se os pesos ficarem em branco, o sistema assume pesos iguais.

## Premissas do Modelo

Alguns dados financeiros usados em CAPM e WACC nao sao fornecidos de forma completa pelo Yahoo Finance. Por isso, o sistema permite configurar:

- Taxa livre de risco;
- Premio de risco de mercado;
- Alíquota de imposto;
- Custo da dívida;
- Periodo histórico usado nos retornos.

Essas premissas aparecem no resumo da análise para deixar claro o que veio da API e o que foi definido pelo modelo acadêmico.

## Indicadores Gerados

### Gestao de Investimentos

- Retorno historico anualizado;
- Volatilidade anualizada;
- Beta calculado contra benchmark;
- Retorno exigido pelo CAPM;
- P/L, P/VP e dividend yield;
- Classificação academica de atratividade.

### Estrutura de Capital

- Divida bruta;
- Divida liquida;
- Divida/patrimonio;
- Divida/valor de mercado;
- Divida liquida/EBITDA;
- Cobertura de juros, quando disponivel;
- Pesos de capital proprio e divida;
- WACC estimado.

### Indicadores herdados do Trabalho 1

- Liquidez corrente;
- Liquidez seca;
- Capital de giro;
- Margens;
- ROA;
- ROE;
- Analise DuPont;
- Fluxo de caixa livre.

## Observação

Este sistema e um projeto acadÊmico e não constitui recomendacao real de investimento. Os dados sao obtidos de fontes públicas via Yahoo Finance/yfinance e podem conter atrasos, lacunas ou diferenças de classificação contábil entre empresas e mercados.
