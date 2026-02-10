import pandas as pd
from pathlib import Path

class DataLoader:
    """
    Gerencia a coleta de dados via Football-Data.co.uk.
    Fonte robusta que fornece CSVs com estatísticas detalhadas e odds.
    """
    
    # URLs diretas para a Premier League (E0)
    # 2324 = Temporada 2023/2024
    DATA_URL = "https://www.football-data.co.uk/mmz4281/2324/E0.csv"
    
    def __init__(self):
        self.raw_data = None
        
    def load_data(self):
        """Baixa e carrega os dados da Premier League."""
        print(f"🔄 Baixando dados de: {self.DATA_URL} ...")
        
        try:
            # Pandas lê CSV diretamente da URL
            self.raw_data = pd.read_csv(self.DATA_URL)
            
            # Renomeia colunas para ficar mais intuitivo
            # FTR = Full Time Result, HS = Home Shots, HC = Home Corners
            # Veja a legenda completa em: football-data.co.uk/notes.txt
            print(f"✅ Download concluído! {len(self.raw_data)} jogos carregados.")
            return self.raw_data
            
        except Exception as e:
            print(f"❌ Erro ao baixar dados: {e}")
            return None

    def save_local(self, filename="premier_league_2324.csv"):
        """Salva uma cópia local para não baixar toda hora."""
        if self.raw_data is not None:
            filepath = Path(f"data/{filename}")
            self.raw_data.to_csv(filepath, index=False)
            print(f"💾 Arquivo salvo em: {filepath}")

# Bloco de Teste
if __name__ == "__main__":
    loader = DataLoader()
    df = loader.load_data()
    
    if df is not None:
        loader.save_local()
        
        # Mostra colunas interessantes
        cols_interesse = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'HST', 'AST', 'HC', 'AC']
        print("\n🔍 Exemplo de dados (Gols, Chutes no Alvo, Cantos):")
        print(df[cols_interesse].tail())