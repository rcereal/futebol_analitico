import pandas as pd
import numpy as np

class DataProcessor:
    # ATUALIZADO: Aponta para o novo arquivo csv
    def __init__(self, raw_data_path="data/premier_league_2526.csv"):
        self.raw_data_path = raw_data_path
        self.df = None
        self.load_and_clean() 

    def load_and_clean(self):
        """Carrega CSV, converte datas e renomeia colunas."""
        try:
            self.df = pd.read_csv(self.raw_data_path)
            self.df['Date'] = pd.to_datetime(self.df['Date'], dayfirst=True)
            
            col_map = {
                'Date': 'data', 'HomeTeam': 'mandante', 'AwayTeam': 'visitante',
                'FTHG': 'gols_mandante', 'FTAG': 'gols_visitante',
                'FTR': 'resultado',
                'HST': 'chutes_alvo_mandante', 'AST': 'chutes_alvo_visitante',
                'HC': 'cantos_mandante', 'AC': 'cantos_visitante',
                'HY': 'amarelos_mandante', 'AY': 'amarelos_visitante',
                'HR': 'vermelhos_mandante', 'AR': 'vermelhos_visitante'
            }
            # Filtra apenas as colunas que nos interessam
            # O set_axis/rename ignora colunas que não existem no map, evitando erros se o CSV mudar levemente
            available_cols = [c for c in col_map.keys() if c in self.df.columns]
            self.df = self.df[available_cols].rename(columns=col_map)
            
            return self.df
            
        except FileNotFoundError:
            print(f"❌ Erro: Arquivo {self.raw_data_path} não encontrado. Execute o data_loader.py primeiro.")
            return None
    
    def listar_times(self):
        """Retorna uma lista com todos os times disponíveis no CSV."""
        if self.df is None: return []
        return sorted(self.df['mandante'].unique())

    # ... (Mantenha o resto das funções get_team_stats igual estava antes) ...
    # Vou replicar a função get_team_stats aqui para garantir que você tenha o arquivo completo
    
    def get_team_stats(self, team, games=5, location='all'):
        if self.df is None: return None

        if location == 'home':
            matches = self.df[self.df['mandante'] == team].copy()
        elif location == 'away':
            matches = self.df[self.df['visitante'] == team].copy()
        else: 
            matches = self.df[(self.df['mandante'] == team) | (self.df['visitante'] == team)].copy()

        matches = matches.sort_values('data').tail(games)

        if matches.empty: return None

        stats = {
            'jogos': len(matches), 'gols_pro': 0, 'gols_contra': 0,
            'chutes_no_alvo': 0, 'cantos': 0, 'cartoes': 0
        }

        for _, row in matches.iterrows():
            if row['mandante'] == team:
                stats['gols_pro'] += row['gols_mandante']
                stats['gols_contra'] += row['gols_visitante']
                stats['chutes_no_alvo'] += row.get('chutes_alvo_mandante', 0)
                stats['cantos'] += row.get('cantos_mandante', 0)
                stats['cartoes'] += row.get('amarelos_mandante', 0) + row.get('vermelhos_mandante', 0)
            else: 
                stats['gols_pro'] += row['gols_visitante']
                stats['gols_contra'] += row['gols_mandante']
                stats['chutes_no_alvo'] += row.get('chutes_alvo_visitante', 0)
                stats['cantos'] += row.get('cantos_visitante', 0)
                stats['cartoes'] += row.get('amarelos_visitante', 0) + row.get('vermelhos_visitante', 0)

        return {
            'time': team,
            'filtro': f"Últimos {games} jogos ({location})",
            'media_gols_feitos': round(stats['gols_pro'] / games, 2),
            'media_gols_sofridos': round(stats['gols_contra'] / games, 2),
            'media_chutes_alvo': round(stats['chutes_no_alvo'] / games, 2),
            'media_cantos': round(stats['cantos'] / games, 2),
            'media_cartoes': round(stats['cartoes'] / games, 2)
        }

if __name__ == "__main__":
    proc = DataProcessor()
    print(proc.listar_times())