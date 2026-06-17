import os
import pandas as pd
from google import genai

class GrowthAIAnalyst:
    def __init__(self):
        # O novo SDK busca a variável GEMINI_API_KEY automaticamente no ambiente,
        # mas passamos aqui explicitamente para garantir.
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        
        # Atualizado para o modelo mais recente e performático
        self.model_name = 'gemini-2.5-flash'

    def generate_report(self, processed_df: pd.DataFrame) -> str:
        """Envia o resumo estatístico para a LLM gerar o relatório de negócio."""
        
        parceiro = processed_df['Parceiro'].iloc[0]
        
        # Transforma o DataFrame do Pandas em uma string Markdown para injetar no prompt
        data_summary = processed_df.to_markdown(index=False)
        
        prompt = f"""
        Você é um Analista de Growth Sênior AI-Native no Méliuz, especialista em testes A/B de cashback.
        Sua tarefa é analisar os resultados consolidados do {parceiro} e gerar um relatório executivo claro para o gestor.
        
        Dados Consolidados do Teste:
        {data_summary}
        
        Métricas no DataFrame:
        - net_revenue: Lucro Líquido do Méliuz (Comissão - Cashback)
        - roi_cashback: Eficiência do cashback em gerar GMV (Vendas / Cashback)
        - ticket_medio: Gasto médio por comprador único
        
        Instruções para o Relatório (Gere em formato Markdown):
        1. Resumo Executivo: Visão geral da performance do parceiro.
        2. Análise Crítica das Variantes: Compare os Grupos de Usuários. Cuidado com falsos vencedores! (Variantes que faturam muito em 'vendas totais' mas destroem a margem por pagar cashback excessivo, gerando 'net_revenue' baixo ou zero).
        3. Decisão Acionável: Responda de forma direta: "Qual variante de cashback devemos escalar para 100% do tráfego?" Baseie-se no Lucro Líquido e na sustentabilidade do ROI.
        """
        
        # Nova sintaxe do SDK atualizado da Google
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        return response.text
