import os
import json
import pandas as pd

def _carregar_dados():
    caminho_dados = os.path.join(os.path.dirname(__file__), "..", "dados", "dados_nivel_2.json")
    with open(caminho_dados, "r", encoding="utf-8") as f:
        raw = json.load(f)
    
    taxa_cambio = raw.get("taxa_cambio_usd_brl", 5.4)
    lista_ops = raw.get("operacoes", [])
    
    df = pd.DataFrame(lista_ops)
    
    # Tratamento e remocao de datas nulas
    df = df.dropna(subset=["data"]).copy()
    df["data"] = pd.to_datetime(df["data"]).dt.strftime("%Y-%m-%d")
    
    # Conversao cambial dinamica com a taxa do arquivo
    df["valor_brl"] = df.apply(
        lambda r: r["valor"] * taxa_cambio if str(r.get("moeda")).upper() == "USD" else r["valor"], 
        axis=1
    )
    return df

_DF_GLOBAL = _carregar_dados()

def historico_cliente(cliente_id: str) -> str:
    """Retorna um resumo agregado das operacoes do cliente (total de ops, volume acumulado e mediana)."""
    sub = _DF_GLOBAL[_DF_GLOBAL["cliente_id"] == cliente_id]
    if sub.empty:
        return json.dumps({"erro": "Cliente nao encontrado"})
    
    resumo = {
        "cliente_id": cliente_id,
        "total_operacoes": int(len(sub)),
        "volume_total_brl": float(sub["valor_brl"].sum()),
        "mediana_operacoes_brl": float(sub["valor_brl"].median()),
        "maior_operacao_brl": float(sub["valor_brl"].max())
    }
    return json.dumps(resumo, ensure_ascii=False)

def operacoes_do_dia(cliente_id: str, data: str) -> str:
    """Retorna as operacoes detalhadas de um cliente em uma data especifica (formato YYYY-MM-DD)."""
    sub = _DF_GLOBAL[(_DF_GLOBAL["cliente_id"] == cliente_id) & (_DF_GLOBAL["data"] == data)]
    if sub.empty:
        return json.dumps({"mensagem": "Nenhuma operacao encontrada nesta data"})
    
    colunas = [c for c in ["data", "valor_brl", "tipo", "canal", "contraparte"] if c in sub.columns]
    ops = sub[colunas].to_dict(orient="records")
    return json.dumps(ops, ensure_ascii=False)

def perfil_canal(cliente_id: str) -> str:
    """Retorna a distribuicao de uso por canal (pix, ted, boleto, etc) e volume transacionado."""
    sub = _DF_GLOBAL[_DF_GLOBAL["cliente_id"] == cliente_id]
    if sub.empty or "canal" not in sub.columns:
        return json.dumps({"erro": "Dados de canal indisponiveis"})
    
    dist = sub.groupby("canal")["valor_brl"].agg(["count", "sum"]).reset_index()
    dist.columns = ["canal", "quantidade", "volume_total"]
    return json.dumps(dist.to_dict(orient="records"), ensure_ascii=False)