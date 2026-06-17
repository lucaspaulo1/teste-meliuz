import pandas as pd

class GrowthDataProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        
    def _clean_monetary_column(self, series: pd.Series) -> pd.Series:
        """Limpa strings monetárias no formato 'R$ 10.273' e converte para float."""
        return (series.astype(str)
                .str.replace('R$', '', regex=False)
                .str.replace('.', '', regex=False)
                .str.replace(',', '.', regex=False)
                .str.strip()
                .astype(float))

    def load_and_process(self) -> pd.DataFrame:
        """Carrega o dataset, limpa dados e calcula métricas agrupadas por variante."""
        self.df = pd.read_csv(self.file_path)
        
        # Limpeza das colunas financeiras
        for col in ['comissão', 'cashback', 'vendas totais']:
            self.df[col] = self._clean_monetary_column(self.df[col])
            
        # Agrupamento por variante (Grupo de usuários)
        grouped = self.df.groupby('Grupos de usuários').agg({
            'Parceiro': 'first',
            'compradores': 'sum',
            'vendas totais': 'sum',
            'comissão': 'sum',
            'cashback': 'sum'
        }).reset_index()
        
        # Engenharia de Atributos (Métricas de Growth)
        grouped['net_revenue'] = grouped['comissão'] - grouped['cashback']
        grouped['roi_cashback'] = grouped['vendas totais'] / grouped['cashback']
        grouped['ticket_medio'] = grouped['vendas totais'] / grouped['compradores']
        
        return grouped
