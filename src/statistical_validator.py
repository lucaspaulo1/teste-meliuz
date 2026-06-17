import pandas as pd
from scipy import stats

class GrowthStatisticalValidator:
    @staticmethod
    def validate_test(df_diario: pd.DataFrame) -> dict:
        """
        Analisa os dados diários para verificar se a diferença de Net Revenue
        entre as duas melhores variantes é estatisticamente significante.
        """
        # Garante que temos as métricas calculadas por linha (dia)
        df_diario['net_revenue_diario'] = df_diario['comissão'] - df_diario['cashback']
        
        # Agrupa temporariamente para descobrir as somas totais acumuladas
        totais = df_diario.groupby('Grupos de usuários')['net_revenue_diario'].sum().sort_values(ascending=False)
        
        if len(totais) < 2:
            return {
                "vencedor_preliminar": totais.index[0],
                "significativo": False,
                "p_value": 1.0,
                "decisao_tomada": f"Escalar {totais.index[0]}",
                "resultado_resumido": "Amostra única ou sem grupos suficientes para teste."
            }
            
        grupo_1st = totais.index[0]
        grupo_2nd = totais.index[1]
        
        # Coleta a série diária de lucros para cada um dos dois grupos
        dados_1st = df_diario[df_diario['Grupos de usuários'] == grupo_1st]['net_revenue_diario']
        dados_2nd = df_diario[df_diario['Grupos de usuários'] == grupo_2nd]['net_revenue_diario']
        
        # Executa o Teste T de Student para amostras independentes (Welch's T-Test)
        t_stat, p_val = stats.ttest_ind(dados_1st, dados_2nd, equal_var=False)
        
        # Significância estatística padrão (95% de confiança)
        significativo = p_val < 0.05
        
        if significativo:
            decisao = f"Escalar {grupo_1st}"
            resultado_resumido = f"{grupo_1st} venceu {grupo_2nd} (p-valor: {p_val:.4f})"
        else:
            decisao = f"Empate Técnico - Manter {grupo_1st} por menor risco"
            resultado_resumido = f"Sem diferença significante entre {grupo_1st} e {grupo_2nd} (p-valor: {p_val:.4f})"
            
        return {
            "vencedor_preliminar": grupo_1st,
            "significativo": significativo,
            "p_value": p_val,
            "decisao_tomada": decisao,
            "resultado_resumido": resultado_resumido
        }
