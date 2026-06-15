import re
import time

import requests
from flask import Flask, jsonify, render_template, request, session

from finance_logic import DEFAULT_ASSUMPTIONS, analisar_carteira

app = Flask(__name__)
app.secret_key = "ufmg_si_financeira_key"


def normalizar_ticker(ticker):
    ticker = ticker.strip().upper()

    # Se ja veio com sufixo ou simbolo especial, mantem.
    # Exemplos: PETR4.SA, MSFT, AAPL, EURUSD=X
    if "." in ticker or "=" in ticker or "-" in ticker or ticker.startswith("^"):
        return ticker

    # Padrao comum de acoes brasileiras: 4 letras + 1 ou 2 numeros.
    # Exemplos: PETR4, VALE3, ITUB4, BBDC4, TAEE11
    if re.match(r"^[A-Z]{4}[0-9]{1,2}$", ticker):
        return ticker + ".SA"

    # Caso contrario, mantem como ticker internacional.
    return ticker


def separar_tickers(texto):
    partes = re.split(r"[,;\s]+", texto.strip().upper())
    return [normalizar_ticker(parte) for parte in partes if parte]


def converter_percentual(valor_texto, valor_padrao):
    try:
        if valor_texto is None or str(valor_texto).strip() == "":
            return valor_padrao
        valor = float(str(valor_texto).replace(",", "."))
        return valor / 100
    except Exception:
        return valor_padrao


def converter_pesos(texto, quantidade):
    if not texto or not texto.strip():
        return None

    try:
        texto = texto.strip()
        if ";" in texto:
            partes = [parte for parte in texto.split(";") if parte.strip()]
        elif re.search(r"\s", texto):
            partes = [parte for parte in re.split(r"\s+", texto) if parte.strip()]
        elif texto.count(",") >= quantidade - 1 and quantidade > 1:
            partes = [parte for parte in texto.split(",") if parte.strip()]
        else:
            partes = [texto]

        valores = [float(parte.replace(",", ".")) for parte in partes]
        if len(valores) != quantidade or any(valor < 0 for valor in valores):
            return None
        if sum(valores) > 1.5:
            valores = [valor / 100 for valor in valores]
        return valores
    except Exception:
        return None


def montar_premissas_do_form():
    return {
        "risk_free_rate": converter_percentual(
            request.form.get("risk_free_rate"),
            DEFAULT_ASSUMPTIONS["risk_free_rate"],
        ),
        "market_premium": converter_percentual(
            request.form.get("market_premium"),
            DEFAULT_ASSUMPTIONS["market_premium"],
        ),
        "tax_rate": converter_percentual(
            request.form.get("tax_rate"),
            DEFAULT_ASSUMPTIONS["tax_rate"],
        ),
        "cost_of_debt": converter_percentual(
            request.form.get("cost_of_debt"),
            DEFAULT_ASSUMPTIONS["cost_of_debt"],
        ),
        "history_period": request.form.get("history_period") or DEFAULT_ASSUMPTIONS["history_period"],
    }


def premissas_para_form(premissas):
    return {
        "risk_free_rate": round(premissas["risk_free_rate"] * 100, 2),
        "market_premium": round(premissas["market_premium"] * 100, 2),
        "tax_rate": round(premissas["tax_rate"] * 100, 2),
        "cost_of_debt": round(premissas["cost_of_debt"] * 100, 2),
        "history_period": premissas["history_period"],
    }


@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    erro = None
    tickers_digitados = ""
    pesos_digitados = ""
    form_premissas = premissas_para_form(DEFAULT_ASSUMPTIONS)

    if request.method == "POST":
        agora = time.time()
        ultima = session.get("last_req", 0)

        if agora - ultima < 3:
            erro = "Aguarde 3 segundos entre as analises."
            return render_template(
                "index.html",
                resultado=resultado,
                erro=erro,
                form_premissas=form_premissas,
                tickers_digitados=tickers_digitados,
                pesos_digitados=pesos_digitados,
            )

        session["last_req"] = agora
        tickers_digitados = request.form.get("ticker", "").strip().upper()
        pesos_digitados = request.form.get("weights", "").strip()
        premissas = montar_premissas_do_form()
        form_premissas = premissas_para_form(premissas)

        tickers = separar_tickers(tickers_digitados)
        pesos = converter_pesos(pesos_digitados, len(tickers))

        if not tickers:
            erro = "Digite ao menos um ticker valido. Exemplo: PETR4, VALE3, AAPL ou MSFT."
        elif pesos_digitados and pesos is None:
            erro = "Os pesos devem ter a mesma quantidade de valores que os tickers. Exemplo: 50 30 20."
        else:
            resultado = analisar_carteira(tickers, pesos, premissas)

            if not resultado:
                erro = (
                    "Nao foi possivel obter dados financeiros para os tickers informados. "
                    "Verifique se sao acoes validas e se possuem dados no Yahoo Finance."
                )

    return render_template(
        "index.html",
        resultado=resultado,
        erro=erro,
        form_premissas=form_premissas,
        tickers_digitados=tickers_digitados,
        pesos_digitados=pesos_digitados,
    )


@app.route("/search_proxy")
def search_proxy():
    q = request.args.get("q", "").strip()

    if not q or len(q) < 2:
        return jsonify([])

    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search"
        headers = {"User-Agent": "Mozilla/5.0"}
        params = {"q": q}

        r = requests.get(url, headers=headers, params=params, timeout=10)
        r.raise_for_status()

        quotes = r.json().get("quotes", [])

        filtrados = []
        for item in quotes:
            symbol = item.get("symbol")
            quote_type = item.get("quoteType")

            if not symbol:
                continue

            if quote_type in ["EQUITY", "ETF"]:
                filtrados.append(item)

        return jsonify(filtrados)

    except Exception as e:
        print(f"Erro no search_proxy: {e}")
        return jsonify([])


if __name__ == "__main__":
    app.run(debug=True)
