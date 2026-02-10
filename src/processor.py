import pandas as pd
import numpy as np

class DataProcessor:
    def __init__(self, raw_data_path="data/premier_league_2324.csv"):
        self.raw_data_path = raw_data_path
        self.df = None
        self.load_and_clean() # Carrega automaticamente ao iniciar

    def load_and_clean(self):
        """(2.1) Carrega CSV, converte datas e renomeia colunas."""
        try:
            self.df = pd.read_csv(self.raw_data_path)
            self.df['Date'] = pd.to_datetime(self.df['Date'], dayfirst=True)
            
            # Mapeamento para nomes em Português
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
            self.df = self.df.rename(columns=col_map)[col_map.values()]
            return self.df
            
        except FileNotFoundError:
            print(f"❌ Erro: Arquivo {self.raw_data_path} não encontrado.")
            return None

    def get_team_stats(self, team, games=5, location='all'):
        """
        (2.2, 2.3, 2.4) Calcula médias e estatísticas de um time.
        
        :param team: Nome do time (ex: 'Liverpool')
        :param games: Número de jogos recentes para analisar (Forma)
        :param location: 'all' (Geral), 'home' (Mandante), 'away' (Visitante)
        """
        if self.df is None: return None

        # 1. Filtrar jogos do time
        if location == 'home':
            matches = self.df[self.df['mandante'] == team].copy()
        elif location == 'away':
            matches = self.df[self.df['visitante'] == team].copy()
        else: # 'all'
            matches = self.df[(self.df['mandante'] == team) | (self.df['visitante'] == team)].copy()

        # Ordenar por data (mais recente por último) e pegar os últimos X jogos
        matches = matches.sort_values('data').tail(games)

        if matches.empty:
            return None

        # 2. Normalizar Estatísticas (Transformar em "Pró" e "Contra")
        stats = {
            'jogos': len(matches),
            'gols_pro': 0, 'gols_contra': 0,
            'chutes_no_alvo': 0,
            'cantos': 0,
            'cartoes': 0
        }

        # Iterar sobre os jogos para somar as métricas corretas
        for _, row in matches.iterrows():
            if row['mandante'] == team:
                stats['gols_pro'] += row['gols_mandante']
                stats['gols_contra'] += row['gols_visitante']
                stats['chutes_no_alvo'] += row['chutes_alvo_mandante']
                stats['cantos'] += row['cantos_mandante']
                stats['cartoes'] += row['amarelos_mandante'] + row['vermelhos_mandante']
            else: # Visitante
                stats['gols_pro'] += row['gols_visitante']
                stats['gols_contra'] += row['gols_mandante']
                stats['chutes_no_alvo'] += row['chutes_alvo_visitante']
                stats['cantos'] += row['cantos_visitante']
                stats['cartoes'] += row['amarelos_visitante'] + row['vermelhos_visitante']

        # 3. Calcular Médias Finais
        return {
            'time': team,
            'filtro': f"Últimos {games} jogos ({location})",
            'media_gols_feitos': round(stats['gols_pro'] / games, 2),
            'media_gols_sofridos': round(stats['gols_contra'] / games, 2),
            'media_chutes_alvo': round(stats['chutes_no_alvo'] / games, 2),
            'media_cantos': round(stats['cantos'] / games, 2),
            'media_cartoes': round(stats['cartoes'] / games, 2)
        }
    
    def listar_times(self):
        """Retorna uma lista com todos os times disponíveis no CSV."""
        if self.df is None: return []
        # Pega todos os nomes únicos da coluna 'mandante' e ordena alfabeticamente
        return sorted(self.df['mandante'].unique())

# --- Bloco de Teste ---
if __name__ == "__main__":
    proc = DataProcessor()
    
    # 1. Mostra todos os times encontrados
    print("\n📋 Times disponíveis na base de dados:")
    times = proc.listar_times()
    print(times)
    
    # 2. Teste dinâmico: Pega o primeiro time da lista e calcula a média
    primeiro_time = times[0] # Provavelmente 'Arsenal' ou 'Bournemouth'
    print(f"\n🔍 Estatísticas do {primeiro_time} (Últimos 5 jogos):")
    print(proc.get_team_stats(primeiro_time, games=5))