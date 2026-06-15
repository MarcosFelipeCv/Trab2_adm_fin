import math
from pathlib import Path

import pandas as pd
import yfinance as yf


YFINANCE_CACHE_DIR = Path(__file__).resolve().parent / ".yfinance-cache"
YFINANCE_CACHE_DIR.mkdir(exist_ok=True)
yf.set_tz_cache_location(str(YFINANCE_CACHE_DIR))


DEFAULT_ASSUMPTIONS = {
    "risk_free_rate": 0.105,
    "market_premium": 0.06,
    "tax_rate": 0.34,
    "cost_of_debt": 0.12,
    "history_period": "5y",
}


def pegar_valor(df, nomes_possiveis):
    """Busca uma conta contabil usando nomes alternativos comuns no Yahoo Finance."""
    if isinstance(nomes_possiveis, str):
        nomes_possiveis = [nomes_possiveis]
    try:
        if df is None or df.empty:
            return None
        for nome in nomes_possiveis:
            if nome in df.index:
                valor = df.loc[nome].iloc[0]
                if pd.isna(valor):
                    return None
                return float(valor)
        return None
    except Exception:
        return None


def dividir(numerador, denominador):
    """Evita divisao por zero ou valores inexistentes."""
    try:
        if numerador is None or denominador is None or denominador == 0:
            return None
        if pd.isna(numerador) or pd.isna(denominador):
            return None
        return numerador / denominador
    except Exception:
        return None


def combinar_premissas(assumptions=None):
    premissas = DEFAULT_ASSUMPTIONS.copy()
    if assumptions:
        premissas.update({k: v for k, v in assumptions.items() if v is not None})
    return premissas


def formatar_percentual(valor):
    if valor is None:
        return "N/D"
    try:
        return f"{valor:.2%}"
    except Exception:
        return "N/D"


def formatar_numero(valor):
    if valor is None:
        return "N/D"
    try:
        return round(float(valor), 2)
    except Exception:
        return "N/D"


def formatar_grande_numero(valor, moeda="R$"):
    """Converte numeros grandes em formato legivel para relatorio."""
    if valor is None:
        return "N/D"
    try:
        valor = float(valor)
        abs_valor = abs(valor)
        prefixo = f"{moeda} " if moeda else ""
        if abs_valor >= 1_000_000_000_000:
            return f"{prefixo}{valor / 1_000_000_000_000:.2f} Tri"
        if abs_valor >= 1_000_000_000:
            return f"{prefixo}{valor / 1_000_000_000:.2f} Bi"
        if abs_valor >= 1_000_000:
            return f"{prefixo}{valor / 1_000_000:.2f} Mi"
        return f"{prefixo}{valor:,.2f}"
    except Exception:
        return "N/D"


def valor_exibicao(valor, tipo="numero", moeda="R$"):
    if tipo == "percentual":
        return formatar_percentual(valor)
    if tipo == "grande":
        return formatar_grande_numero(valor, moeda)
    return formatar_numero(valor)


def escolher_benchmark(tickers):
    """Usa Ibovespa para carteiras brasileiras e S&P 500 para as demais."""
    if tickers and all(ticker.upper().endswith(".SA") for ticker in tickers):
        return "^BVSP"
    return "^GSPC"


def obter_fechamentos(ticker_symbol, period="5y"):
    try:
        historico = yf.Ticker(ticker_symbol).history(period=period, auto_adjust=True)
        if historico is None or historico.empty or "Close" not in historico:
            return pd.Series(dtype=float)
        return historico["Close"].dropna()
    except Exception:
        return pd.Series(dtype=float)


def calcular_retorno_anualizado(fechamentos):
    try:
        if fechamentos is None or len(fechamentos) < 2:
            return None
        retorno_total = fechamentos.iloc[-1] / fechamentos.iloc[0] - 1
        anos = max((fechamentos.index[-1] - fechamentos.index[0]).days / 365.25, 1 / 365.25)
        return (1 + retorno_total) ** (1 / anos) - 1
    except Exception:
        return None


def calcular_volatilidade_anualizada(retornos):
    try:
        if retornos is None or len(retornos) < 2:
            return None
        return float(retornos.std() * math.sqrt(252))
    except Exception:
        return None


def calcular_beta(retornos_ativo, retornos_mercado):
    try:
        dados = pd.concat([retornos_ativo, retornos_mercado], axis=1).dropna()
        if len(dados) < 30:
            return None
        var_mercado = dados.iloc[:, 1].var()
        if var_mercado == 0:
            return None
        covariancia = dados.iloc[:, 0].cov(dados.iloc[:, 1])
        return float(covariancia / var_mercado)
    except Exception:
        return None


def classificar_investimento(retorno, retorno_exigido, volatilidade, divida_ebitda):
    pontos = 0
    motivos = []

    if retorno is not None and retorno_exigido is not None:
        if retorno >= retorno_exigido:
            pontos += 2
            motivos.append("retorno historico acima do retorno exigido pelo CAPM")
        else:
            pontos -= 1
            motivos.append("retorno historico abaixo do retorno exigido pelo CAPM")

    if volatilidade is not None:
        if volatilidade <= 0.25:
            pontos += 1
            motivos.append("volatilidade historica moderada")
        elif volatilidade >= 0.45:
            pontos -= 1
            motivos.append("volatilidade historica elevada")

    if divida_ebitda is not None:
        if divida_ebitda <= 2.5:
            pontos += 1
            motivos.append("alavancagem operacional administravel")
        elif divida_ebitda >= 4:
            pontos -= 1
            motivos.append("alavancagem operacional elevada")

    if pontos >= 3:
        return "Atrativa", motivos
    if pontos >= 1:
        return "Neutra/Moderada", motivos
    return "Risco elevado", motivos


def diagnosticar_capital(divida_liquida_patrimonio, divida_ebitda, cobertura_juros):
    alertas = []

    if divida_liquida_patrimonio is not None:
        if divida_liquida_patrimonio < 0:
            alertas.append("caixa superior a divida bruta")
        elif divida_liquida_patrimonio <= 1:
            alertas.append("divida liquida em nivel controlado frente ao patrimonio")
        else:
            alertas.append("divida liquida alta frente ao patrimonio")

    if divida_ebitda is not None:
        if divida_ebitda <= 2.5:
            alertas.append("divida liquida/EBITDA confortavel")
        elif divida_ebitda <= 4:
            alertas.append("divida liquida/EBITDA exige acompanhamento")
        else:
            alertas.append("divida liquida/EBITDA indica pressao financeira")

    if cobertura_juros is not None:
        if cobertura_juros >= 3:
            alertas.append("EBIT cobre bem as despesas financeiras")
        elif cobertura_juros >= 1:
            alertas.append("cobertura de juros apertada")
        else:
            alertas.append("EBIT nao cobre adequadamente os juros")

    if not alertas:
        return "Nao ha dados suficientes para diagnostico completo de capital."
    return "; ".join(alertas) + "."


def montar_comentario(resultado):
    retorno = resultado["valores"]["retorno_anualizado"]
    retorno_exigido = resultado["valores"]["retorno_exigido"]
    beta = resultado["valores"]["beta_calculado"] or resultado["valores"]["beta_yahoo"]
    wacc = resultado["valores"]["wacc"]
    classificacao = resultado["classificacao"]

    partes = [
        f"A empresa foi classificada como {classificacao.lower()} no modelo academico.",
    ]

    if retorno is not None and retorno_exigido is not None:
        partes.append(
            f"O retorno historico anualizado foi {formatar_percentual(retorno)}, "
            f"contra um retorno exigido pelo CAPM de {formatar_percentual(retorno_exigido)}."
        )

    if beta is not None:
        if beta > 1.2:
            partes.append("O beta acima de 1 indica risco sistematico superior ao mercado.")
        elif beta < 0.8:
            partes.append("O beta abaixo de 1 indica menor sensibilidade ao mercado.")
        else:
            partes.append("O beta proximo de 1 sugere risco sistematico parecido com o mercado.")

    if wacc is not None:
        partes.append(f"O WACC estimado foi {formatar_percentual(wacc)}, usando premissas informadas no formulario.")

    partes.append(resultado["diagnostico_capital"])
    return " ".join(partes)


def get_financial_indexes(ticker_symbol, assumptions=None, benchmark_symbol=None):
    try:
        premissas = combinar_premissas(assumptions)
        benchmark_symbol = benchmark_symbol or escolher_benchmark([ticker_symbol])

        empresa = yf.Ticker(ticker_symbol)
        dre = empresa.financials
        balanco = empresa.balance_sheet
        fluxo_caixa = empresa.cashflow
        info = empresa.info

        if (dre is None or dre.empty) and (balanco is None or balanco.empty):
            return None

        lucro_liquido = pegar_valor(dre, "Net Income")
        receita_total = pegar_valor(dre, "Total Revenue")
        lucro_bruto = pegar_valor(dre, "Gross Profit")
        ebit = pegar_valor(dre, ["EBIT", "Operating Income"])
        ebitda = pegar_valor(dre, "EBITDA")
        despesa_juros = pegar_valor(dre, ["Interest Expense", "Interest Expense Non Operating"])

        ativo_total = pegar_valor(balanco, "Total Assets")
        patrimonio_liquido = pegar_valor(balanco, "Stockholders Equity")
        ativo_circulante = pegar_valor(balanco, ["Current Assets", "Total Current Assets"])
        passivo_circulante = pegar_valor(balanco, ["Current Liabilities", "Total Current Liabilities"])
        passivo_total = pegar_valor(balanco, "Total Liabilities Net Minority Interest")
        divida_total = pegar_valor(balanco, ["Total Debt", "Long Term Debt And Capital Lease Obligation"])
        caixa = pegar_valor(balanco, ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"])
        estoques = pegar_valor(balanco, "Inventory")

        fluxo_operacional = pegar_valor(fluxo_caixa, "Operating Cash Flow")
        capex = pegar_valor(fluxo_caixa, "Capital Expenditure")
        fluxo_caixa_livre = fluxo_operacional + capex if fluxo_operacional is not None and capex is not None else None

        preco_atual = info.get("currentPrice") or info.get("regularMarketPrice")
        div_rate = info.get("dividendRate")
        valor_mercado = info.get("marketCap")
        lpa = info.get("trailingEps")
        vpa = info.get("bookValue")
        beta_yahoo = info.get("beta")
        moeda = info.get("currency", "BRL")
        simbolo_moeda = "R$" if moeda == "BRL" else moeda

        liq_corrente = dividir(ativo_circulante, passivo_circulante)
        liq_seca = dividir(ativo_circulante - estoques, passivo_circulante) if ativo_circulante is not None and estoques is not None else None
        capital_giro = ativo_circulante - passivo_circulante if ativo_circulante is not None and passivo_circulante is not None else None

        margem_bruta = dividir(lucro_bruto, receita_total)
        margem_operacional = dividir(ebit, receita_total)
        margem_liquida = dividir(lucro_liquido, receita_total)
        roa = dividir(lucro_liquido, ativo_total)
        roe = dividir(lucro_liquido, patrimonio_liquido)
        giro_ativo = dividir(receita_total, ativo_total)
        multiplicador_pl = dividir(ativo_total, patrimonio_liquido)
        roe_dupont = margem_liquida * giro_ativo * multiplicador_pl if all(v is not None for v in [margem_liquida, giro_ativo, multiplicador_pl]) else None

        endividamento_geral = dividir(passivo_total, ativo_total)
        divida_patrimonio = dividir(divida_total, patrimonio_liquido)
        divida_liquida = divida_total - caixa if divida_total is not None and caixa is not None else None
        divida_liquida_patrimonio = dividir(divida_liquida, patrimonio_liquido)
        divida_valor_mercado = dividir(divida_total, valor_mercado)
        divida_ebitda = dividir(divida_liquida, ebitda)
        cobertura_juros = dividir(ebit, abs(despesa_juros)) if despesa_juros is not None else None
        margem_fcf = dividir(fluxo_caixa_livre, receita_total)

        pl = dividir(preco_atual, lpa)
        pvp = dividir(preco_atual, vpa)
        dividend_yield = dividir(div_rate, preco_atual)
        if dividend_yield is None:
            dividend_yield = info.get("dividendYield") or info.get("trailingAnnualDividendYield")
        if dividend_yield and dividend_yield > 1.0:
            dividend_yield = dividir(dividend_yield, 100)

        fechamentos = obter_fechamentos(ticker_symbol, premissas["history_period"])
        retornos = fechamentos.pct_change().dropna()
        fechamentos_benchmark = obter_fechamentos(benchmark_symbol, premissas["history_period"])
        retornos_benchmark = fechamentos_benchmark.pct_change().dropna()

        retorno_anualizado = calcular_retorno_anualizado(fechamentos)
        volatilidade_anualizada = calcular_volatilidade_anualizada(retornos)
        beta_calculado = calcular_beta(retornos, retornos_benchmark)
        beta_para_capm = beta_calculado if beta_calculado is not None else beta_yahoo
        retorno_exigido = premissas["risk_free_rate"] + beta_para_capm * premissas["market_premium"] if beta_para_capm is not None else None

        equity_value = valor_mercado
        debt_value = divida_total
        total_capital = (equity_value or 0) + (debt_value or 0)
        peso_capital_proprio = dividir(equity_value, total_capital)
        peso_divida = dividir(debt_value, total_capital)
        custo_divida_liquido = premissas["cost_of_debt"] * (1 - premissas["tax_rate"])
        wacc = None
        if peso_capital_proprio is not None and peso_divida is not None and retorno_exigido is not None:
            wacc = peso_capital_proprio * retorno_exigido + peso_divida * custo_divida_liquido

        diagnostico_capital = diagnosticar_capital(divida_liquida_patrimonio, divida_ebitda, cobertura_juros)
        classificacao, motivos = classificar_investimento(retorno_anualizado, retorno_exigido, volatilidade_anualizada, divida_ebitda)

        valores = {
            "liq_corrente": liq_corrente,
            "liq_seca": liq_seca,
            "capital_giro": capital_giro,
            "margem_bruta": margem_bruta,
            "margem_operacional": margem_operacional,
            "margem_liquida": margem_liquida,
            "roa": roa,
            "roe": roe,
            "giro_ativo": giro_ativo,
            "multiplicador_pl": multiplicador_pl,
            "roe_dupont": roe_dupont,
            "endividamento_geral": endividamento_geral,
            "divida_patrimonio": divida_patrimonio,
            "divida_total": divida_total,
            "divida_liquida": divida_liquida,
            "divida_liquida_patrimonio": divida_liquida_patrimonio,
            "divida_valor_mercado": divida_valor_mercado,
            "divida_ebitda": divida_ebitda,
            "cobertura_juros": cobertura_juros,
            "fluxo_operacional": fluxo_operacional,
            "capex": capex,
            "fluxo_caixa_livre": fluxo_caixa_livre,
            "margem_fcf": margem_fcf,
            "preco_atual": preco_atual,
            "valor_mercado": valor_mercado,
            "lpa": lpa,
            "vpa": vpa,
            "pl": pl,
            "pvp": pvp,
            "dividend_yield": dividend_yield,
            "beta_yahoo": beta_yahoo,
            "beta_calculado": beta_calculado,
            "retorno_anualizado": retorno_anualizado,
            "volatilidade_anualizada": volatilidade_anualizada,
            "retorno_exigido": retorno_exigido,
            "peso_capital_proprio": peso_capital_proprio,
            "peso_divida": peso_divida,
            "custo_divida_liquido": custo_divida_liquido,
            "wacc": wacc,
        }

        resultado = {
            "ticker": ticker_symbol,
            "nome": info.get("longName", ticker_symbol),
            "setor": info.get("sector", "N/A"),
            "industria": info.get("industry", "N/A"),
            "moeda": moeda,
            "simbolo_moeda": simbolo_moeda,
            "benchmark": benchmark_symbol,
            "classificacao": classificacao,
            "motivos": motivos,
            "diagnostico_capital": diagnostico_capital,
            "valores": valores,
            "series_retorno": retornos,
        }
        resultado["comentario"] = montar_comentario(resultado)

        # Campos formatados preservam compatibilidade com a tela antiga.
        for chave, valor in valores.items():
            if chave in {"capital_giro", "divida_total", "divida_liquida", "fluxo_operacional", "capex", "fluxo_caixa_livre", "valor_mercado"}:
                resultado[chave] = valor_exibicao(valor, "grande", simbolo_moeda)
            elif chave in {
                "margem_bruta",
                "margem_operacional",
                "margem_liquida",
                "roa",
                "roe",
                "roe_dupont",
                "endividamento_geral",
                "divida_valor_mercado",
                "margem_fcf",
                "dividend_yield",
                "retorno_anualizado",
                "volatilidade_anualizada",
                "retorno_exigido",
                "peso_capital_proprio",
                "peso_divida",
                "custo_divida_liquido",
                "wacc",
            }:
                resultado[chave] = valor_exibicao(valor, "percentual")
            else:
                resultado[chave] = valor_exibicao(valor)

        return resultado

    except Exception as e:
        print(f"Erro ao processar {ticker_symbol}: {e}")
        return None


def analisar_carteira(tickers, pesos=None, assumptions=None):
    premissas = combinar_premissas(assumptions)
    tickers = [ticker.strip().upper() for ticker in tickers if ticker and ticker.strip()]
    if not tickers:
        return None

    benchmark = escolher_benchmark(tickers)
    if not pesos or len(pesos) != len(tickers):
        pesos = [1 / len(tickers)] * len(tickers)
    else:
        total_pesos = sum(pesos)
        pesos = [peso / total_pesos for peso in pesos] if total_pesos else [1 / len(tickers)] * len(tickers)

    empresas = []
    pesos_empresas = []
    for ticker, peso in zip(tickers, pesos):
        analise = get_financial_indexes(ticker, premissas, benchmark)
        if analise:
            empresas.append(analise)
            pesos_empresas.append(peso)

    if not empresas:
        return None

    pesos_validos = pesos_empresas
    soma_validos = sum(pesos_validos)
    pesos_validos = [peso / soma_validos for peso in pesos_validos] if soma_validos else [1 / len(empresas)] * len(empresas)

    retornos = {}
    for empresa in empresas:
        serie = empresa.get("series_retorno")
        if serie is not None and not serie.empty:
            retornos[empresa["ticker"]] = serie

    retorno_carteira = None
    volatilidade_carteira = None
    correlacao_media = None
    if retornos:
        df_retornos = pd.DataFrame(retornos).dropna()
        if not df_retornos.empty:
            pesos_por_ticker = dict(zip([empresa["ticker"] for empresa in empresas], pesos_validos))
            pesos_series = pd.Series(
                [pesos_por_ticker[coluna] for coluna in df_retornos.columns],
                index=df_retornos.columns,
                dtype=float,
            )
            pesos_series = pesos_series / pesos_series.sum()
            retorno_diario = df_retornos.dot(pesos_series)
            volatilidade_carteira = calcular_volatilidade_anualizada(retorno_diario)
            retorno_carteira = ((1 + retorno_diario).prod()) ** (252 / len(retorno_diario)) - 1
            corr = df_retornos.corr()
            if len(corr.columns) > 1:
                correlacoes = corr.where(~pd.DataFrame(
                    [[i == j for j in range(len(corr))] for i in range(len(corr))],
                    index=corr.index,
                    columns=corr.columns,
                )).stack()
                correlacao_media = float(correlacoes.mean()) if not correlacoes.empty else None

    beta_carteira = sum(
        peso * (empresa["valores"]["beta_calculado"] or empresa["valores"]["beta_yahoo"] or 0)
        for peso, empresa in zip(pesos_validos, empresas)
    )
    retorno_exigido_carteira = premissas["risk_free_rate"] + beta_carteira * premissas["market_premium"]
    wacc_medio = sum(
        peso * (empresa["valores"]["wacc"] or 0)
        for peso, empresa in zip(pesos_validos, empresas)
    )

    comentario = (
        f"A carteira usa {len(empresas)} ativo(s), benchmark {benchmark}, "
        f"beta ponderado de {formatar_numero(beta_carteira)} e retorno exigido CAPM de "
        f"{formatar_percentual(retorno_exigido_carteira)}."
    )
    if correlacao_media is not None:
        comentario += f" A correlacao media entre os ativos foi {formatar_numero(correlacao_media)}, indicador simples do ganho de diversificacao."
    if retorno_carteira is not None:
        if retorno_carteira >= retorno_exigido_carteira:
            comentario += " O retorno historico da carteira ficou acima do retorno exigido pelo CAPM."
        else:
            comentario += " O retorno historico da carteira ficou abaixo do retorno exigido pelo CAPM."

    for empresa in empresas:
        empresa.pop("series_retorno", None)

    return {
        "tickers": tickers,
        "pesos": pesos_validos,
        "benchmark": benchmark,
        "empresas": empresas,
        "premissas": premissas,
        "resumo": {
            "retorno_carteira": formatar_percentual(retorno_carteira),
            "volatilidade_carteira": formatar_percentual(volatilidade_carteira),
            "beta_carteira": formatar_numero(beta_carteira),
            "retorno_exigido_carteira": formatar_percentual(retorno_exigido_carteira),
            "wacc_medio": formatar_percentual(wacc_medio),
            "correlacao_media": formatar_numero(correlacao_media),
        },
        "comentario": comentario,
    }


def get_financial_analysis(ticker, assumptions=None):
    """Compatibilidade: invoca a analise de uma unica empresa."""
    return get_financial_indexes(ticker, assumptions)
