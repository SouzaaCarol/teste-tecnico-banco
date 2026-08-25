import os
import json
import pandas as pd
from dotenv import load_dotenv
from google import genai
from tools import _DF_GLOBAL

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def carregar_top_10_regras(out_dir):
    caminho = os.path.join(out_dir, "top_10_regras.json")
    if os.path.exists(caminho):
        return pd.read_json(caminho)
    return pd.DataFrame()

def carregar_pareceres_agente(out_dir):
    pareceres = []
    if os.path.exists(out_dir):
        for arq in os.listdir(out_dir):
            if arq.startswith("parecer_") and arq.endswith(".json"):
                caminho = os.path.join(out_dir, arq)
                with open(caminho, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        pareceres.append(data)
                    except Exception:
                        pass
    return pd.DataFrame(pareceres)

def gerar_analise_comparativa_llm(df_confronto):
    resumo_texto = df_confronto.to_string(index=False)
    
    prompt = f"""
    Voce e um Auditor/Especialista Senior em Prevenção à Lavagem de Dinheiro (PLD).
    Analise a tabela abaixo, que compara o resultado das REGRAS DETERMINISTICAS (Smurfing/Outlier) com a AVALIACAO DO AGENTE IA (Nivel de Risco e Parecer):

    {resumo_texto}

    Elabore um relatorio de confronto sucinto e direto destacando:
    1. Divergências Relevantes: Casos em que as regras sinalizaram alto risco, mas a IA classificou como baixo/médio (ou vice-versa).
    2. Redução de Falsos Positivos: Como o agente IA agregou valor analítico além dos limites rígidos das regras.
    3. Conclusão e Recomendação Técnica para a equipe de compliance.

    Responda em texto corrido e bem estruturado.
    """

    # Tenta com o modelo gemini-2.5-flash para evitar o limite de cota do 3.6-flash
    for model_name in ["gemini-2.5-flash", "gemini-1.5-flash"]:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            continue
            
    return "Não foi possível gerar a síntese via LLM devido a restrições de cota, mas os arquivos de confronto foram gerados com sucesso."

def executar_confronto():
    base_dir = os.path.dirname(__file__)
    out_dir = os.path.join(base_dir, "..", "outputs")
    
    print("[+] Carregando dados do Top 10 Regras e Pareceres do Agente...")
    df_regras = carregar_top_10_regras(out_dir)
    df_agente = carregar_pareceres_agente(out_dir)
    
    if df_regras.empty or df_agente.empty:
        print("[!] Erro: Nao foi possivel encontrar os arquivos de entrada em 'outputs/'. Certifique-se de ter rodado o 'agente.py' primeiro.")
        return

    # Unir dados das Regras com dados do Agente
    df_merged = pd.merge(df_regras, df_agente, on="cliente_id", how="inner")
    
    # Selecionar e formatar colunas para o relatório
    colunas_exibicao = [
        "cliente_id", "volume_total", "flag_smurfing", "flag_outlier", 
        "total_flags", "nivel_risco", "tipologia_suspeita", "justificativa"
    ]
    cols_existentes = [c for c in colunas_exibicao if c in df_merged.columns]
    df_resultado = df_merged[cols_existentes].copy()
    
    print(f"[>] Processando confronto para {len(df_resultado)} clientes...")
    
    # Gerar parecer executivo global via LLM
    print("[>] Solicitando analise comparativa de PLD...")
    analise_executiva = gerar_analise_comparativa_llm(df_resultado)
    
    # Exportar resultados
    caminho_csv = os.path.join(out_dir, "relatorio_confronto.csv")
    caminho_json = os.path.join(out_dir, "relatorio_confronto.json")
    
    df_resultado.to_csv(caminho_csv, index=False, encoding="utf-8-sig")
    
    resultado_completo = {
        "resumo_clientes": df_resultado.to_dict(orient="records"),
        "parecer_auditoria_executiva": analise_executiva
    }
    
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(resultado_completo, f, indent=2, ensure_ascii=False)
        
    print("\n[OK] Confronto concluido com sucesso!")
    print(f"[+] Arquivo CSV salvo em: {caminho_csv}")
    print(f"[+] Arquivo JSON consolidado salvo em: {caminho_json}")
    print("\n=== PARACER EXECUTIVO DE AUDITORIA ===")
    print(analise_executiva)

if __name__ == "__main__":
    executar_confronto()