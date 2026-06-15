# Analisador de Investimentos e Estrutura de Capital - UFMG

Projeto academico para a disciplina de Administracao Financeira (Sistemas de Informacao).

O sistema expande o Trabalho 1 e continua usando dados reais do Yahoo Finance via `yfinance`, mas agora tambem cobre temas da segunda metade do curso:

- Gestao de Investimentos;
- CAPM e risco sistematico;
- Estrutura de Capital;
- custo medio ponderado de capital (WACC);
- diagnostico de alavancagem e endividamento;
- resumo consolidado da analise na propria pagina.

## Alunos

Marcos Felipe Flores Cavalieri - 2020054692

Bianca Gabriela Franco e Silva - 2020092756

## Como Rodar

### 1. Requisitos

Python instalado na maquina.

Conexao ativa com a internet, necessaria para buscar dados reais no Yahoo Finance.

### 2. Instalacao

Dentro da pasta principal do projeto, execute:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Execucao

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

Digite varios tickers separados por espaco, virgula ou ponto e virgula:

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

- taxa livre de risco;
- premio de risco de mercado;
- aliquota de imposto;
- custo da divida;
- periodo historico usado nos retornos.

Essas premissas aparecem no resumo da analise para deixar claro o que veio da API e o que foi definido pelo modelo academico.

## Indicadores Gerados

### Gestao de Investimentos

- retorno historico anualizado;
- volatilidade anualizada;
- beta calculado contra benchmark;
- retorno exigido pelo CAPM;
- P/L, P/VP e dividend yield;
- classificacao academica de atratividade.

### Estrutura de Capital

- divida bruta;
- divida liquida;
- divida/patrimonio;
- divida/valor de mercado;
- divida liquida/EBITDA;
- cobertura de juros, quando disponivel;
- pesos de capital proprio e divida;
- WACC estimado.

### Indicadores herdados do Trabalho 1

- liquidez corrente;
- liquidez seca;
- capital de giro;
- margens;
- ROA;
- ROE;
- analise DuPont;
- fluxo de caixa livre.

## Observacao

Este sistema e um projeto academico e nao constitui recomendacao real de investimento. Os dados sao obtidos de fontes publicas via Yahoo Finance/yfinance e podem conter atrasos, lacunas ou diferencas de classificacao contabil entre empresas e mercados.
