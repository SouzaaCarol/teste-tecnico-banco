import os
import time
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tools import _DF_GLOBAL, historico_cliente, operacoes_do_dia, perfil_canal

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- PARTE A: REGRAS EM ESCALA E TOP 10 ---
def obter_top_10_clientes():
    df = _DF_GLOBAL.copy()

    def check_smurfing(group):
        soma = group["valor_brl"].sum()
        qtd = len(group)
        max_val = group["valor_brl"].max()
        return (qtd >= 3) and (soma > 50000) and (max_val < 20000)

    smurfing_flags = df.groupby(["cliente_id", "data"], group_keys=False).apply(check_smurfing)
    if isinstance(smurfing_flags.index, pd.MultiIndex):
        smurfing_clients = smurfing_flags[smurfing_flags].index.get_level_values("cliente_id").unique()
    else:
        smurfing_clients = []

    medianas = df.groupby("cliente_id")["valor_brl"].median()
    contagens = df.groupby("cliente_id")["valor_brl"].count()

    def check_outlier(row):
        c_id = row["cliente_id"]
        if contagens.get(c_id, 0) >= 4:
            return row["valor_brl"] > 5 * medianas.get(c_id, 0)
        return False

    df["flag_outlier"] = df.apply(check_outlier, axis=1)
    outlier_clients = df[df["flag_outlier"]]["cliente_id"].unique()

    resumo = df.groupby("cliente_id").agg(volume_total=("valor_brl", "sum")).reset_index()
    resumo["flag_smurfing"] = resumo["cliente_id"].isin(smurfing_clients)
    resumo["flag_outlier"] = resumo["cliente_id"].isin(outlier_clients)
    resumo["total_flags"] = resumo["flag_smurfing"].astype(int) + resumo["flag_outlier"].astype(int)

    top_10 = resumo.sort_values(by=["total_flags", "volume_total"], ascending=[False, False]).head(10)
    return top_10

# --- PARTE B & C: AGENTE ---
def executar_agente_cliente(cliente_id: str):
    prompt = f"""
    Voce e um Analista Senior de PLD. Investigue o cliente '{cliente_id}'.
    Decida quais ferramentas utilizar (historico_cliente, operacoes_do_dia, perfil_canal) para avaliar o perfil de risco.
    
    Responda ESTRITAMENTE em formato JSON com este schema:
    {{
      "cliente_id": "{cliente_id}",
      "nivel_risco": "BAIXO" | "MEDIO" | "ALTO",
      "tipologia_suspeita": "string",
      "ferramentas_consultadas": ["lista de tools chamadas"],
      "justificativa": "resumo do parecer tecnico"
    }}
    """
    
    config = types.GenerateContentConfig(
        tools=[historico_cliente, operacoes_do_dia, perfil_canal],
        temperature=0.1
    )
    
    t0 = time.time()
    try:
        chat = client.chats.create(
            model="gemini-3.6-flash",
            config=config
        )
        response = chat.send_message(prompt)
        tempo = time.time() - t0
        
        usage = response.usage_metadata
        tokens_in = usage.prompt_token_count if usage else 0
        tokens_out = usage.candidates_token_count if usage else 0
        
        raw = response.text.replace("```json", "").replace("```", "").strip() if response.text else "{}"
        parecer = json.loads(raw)
    except Exception as e:
        tempo = time.time() - t0
        parecer = {"cliente_id": cliente_id, "nivel_risco": "ALTO", "justificativa": f"Erro na análise: {str(e)}"}
        tokens_in, tokens_out = 0, 0
        
    return parecer, {
        "cliente_id": cliente_id,
        "tempo_segundos": round(tempo, 2),
        "tokens_entrada": tokens_in,
        "tokens_saida": tokens_out,
        "tokens_total": tokens_in + tokens_out
    }

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "..", "outputs")
    os.makedirs(out_dir, exist_ok=True)
    
    print("[+] Selecionando Top 10 Clientes Sinalizados...")
    top_10 = obter_top_10_clientes()
    top_10.to_json(os.path.join(out_dir, "top_10_regras.json"), orient="records", indent=2)
    
    pareceres = []
    metricas = []
    
    print("[>] Iniciando investigacoes paralelas para o Top 10...")
    
    # Executa até 5 investigacoes em paralelo para acelerar a execucao
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(executar_agente_cliente, c_id): c_id for c_id in top_10["cliente_id"]}
        
        for future in as_completed(futures):
            c_id = futures[future]
            p, m = future.result()
            
            with open(os.path.join(out_dir, f"parecer_{c_id}.json"), "w", encoding="utf-8") as f:
                json.dump(p, f, indent=2, ensure_ascii=False)
                
            pareceres.append(p)
            metricas.append(m)
            print(f"[OK] Finalizada investigacao do cliente: {c_id}")
        
    df_m = pd.DataFrame(metricas)
    df_m.to_csv(os.path.join(out_dir, "metricas_execucao.csv"), index=False)
    
    print("\n[OK] Execucao do Agente concluida com sucesso!")
    print(f"Tempo Total Consolidado: {df_m['tempo_segundos'].max():.2f}s | Tokens Totais: {df_m['tokens_total'].sum()}")