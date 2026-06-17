import sys
import os
import pandas as pd
from dotenv import load_dotenv
from src.data_processor import GrowthDataProcessor
from src.ai_analyst import GrowthAIAnalyst

load_dotenv()

def update_tracking_sheet(file_name, parceiro, decisao, resumo_resultado):
    """Atualiza o arquivo CSV consolidado simulando o comportamento do Google Sheets."""
    tracking_file = "consolidado_testes.csv"
    new_row = {
        "Nome do Teste": file_name,
        "Parceiro": parceiro,
        "Decisão Tomada": decisao,
        "Resultado Resumido": resumo_resultado
    }
    
    if os.path.exists(tracking_file):
        df_track = pd.read_csv(tracking_file)
        df_track = pd.concat([df_track, pd.DataFrame([new_row])], ignore_index=True)
    else:
        df_track = pd.DataFrame([new_row])
        
    df_track.to_csv(tracking_file, index=False)
    print(f"📊 Registro do teste salvo com sucesso em '{tracking_file}'!")

def main():
    if len(sys.argv) < 2:
        print("Uso correto: python main.py <caminho_do_dataset.csv>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    file_name = os.path.basename(file_path)
    
    print(f"🚀 Iniciando análise do arquivo: {file_name}...")
    
    # 1. Processamento determinístico de dados
    processor = GrowthDataProcessor(file_path)
    metrics_df = processor.load_and_process()
    
    # 2. Análise Cognitiva via LLM
    analyst = GrowthAIAnalyst()
    report = analyst.generate_report(metrics_df)
    
    # Exibe o relatório no terminal
    print("\n" + "="*40 + "\n📜 RELATÓRIO DA IA GENERATIVA\n" + "="*40)
    print(report)
    print("="*40 + "\n")
    
    # Salvando o relatório em um arquivo markdown individual
    report_output_path = f"relatorio_{file_name.replace('.csv', '.md')}"
    with open(report_output_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"📁 Relatório detalhado salvo em: {report_output_path}")
    
    # 3. Registro Automático dos Resultados (Simulação do Sheets)
    parceiro = metrics_df['Parceiro'].iloc[0]
    
    # Uma lógica rápida para extrair a decisão automatizada para a tabela resumo
    # (Pode ser melhorada capturando a própria resposta da IA, ou via regra lógica do melhor Net Revenue)
    melhor_grupo = metrics_df.loc[metrics_df['net_revenue'].idxmax()]['Grupos de usuários']
    maior_lucro = metrics_df['net_revenue'].max()
    
    resumo_texto = f"Melhor Net Revenue acumulado de R$ {maior_lucro:,.2f}"
    update_tracking_sheet(file_name, parceiro, f"Escalar {melhor_grupo}", resumo_texto)

if __name__ == "__main__":
    main()
