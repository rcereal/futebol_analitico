import numpy as np
from scipy.stats import poisson

class StatisticalEngine:
    def __init__(self, df):
        self.df = df
        self.league_avgs = self._calculate_league_averages()

    def _calculate_league_averages(self):
        return {
            'home_goals': self.df['gols_mandante'].mean(),
            'away_goals': self.df['gols_visitante'].mean(),
            # Tratamento de erro com .get() para ligas que não têm essas colunas (ex: Brasil)
            'home_corners': self.df.get('cantos_mandante', self.df['gols_mandante']*0).mean(),
            'away_corners': self.df.get('cantos_visitante', self.df['gols_visitante']*0).mean(),
        }

    def calculate_strength(self, team):
        # ... (Mantendo a lógica de ataque/defesa igual) ...
        home_games = self.df[self.df['mandante'] == team]
        if home_games.empty: return None
        
        att_home = home_games['gols_mandante'].mean() / self.league_avgs['home_goals']
        def_home = home_games['gols_visitante'].mean() / self.league_avgs['away_goals']

        away_games = self.df[self.df['visitante'] == team]
        if away_games.empty: return None

        att_away = away_games['gols_visitante'].mean() / self.league_avgs['away_goals']
        def_away = away_games['gols_mandante'].mean() / self.league_avgs['home_goals']

        return {
            'attack_home': att_home, 'defense_home': def_home,
            'attack_away': att_away, 'defense_away': def_away
        }

    def predict_corners_cards(self, home_team, away_team):
        """
        CORRIGIDO: Calcula Escanteios e Cartões cruzando Ataque x Defesa.
        """
        h_games = self.df[self.df['mandante'] == home_team]
        a_games = self.df[self.df['visitante'] == away_team]
        
        if h_games.empty or a_games.empty: 
            return {'exp_corners_home': 0, 'exp_corners_away': 0, 'exp_corners_total': 0, 
                    'exp_cards_home': 0, 'exp_cards_away': 0, 'exp_cards_total': 0}

        # --- ESCANTEIOS (CANTOS) ---
        # Média que o Mandante faz em casa
        avg_corners_h_for = h_games.get('cantos_mandante', h_games['gols_mandante']*0).mean()
        # Média que o Visitante SOFRE fora (são os cantos do mandante adversário)
        avg_corners_a_against = a_games.get('cantos_mandante', a_games['gols_mandante']*0).mean()
        
        # Expectativa Casa: Média entre o que ele faz e o que o adversário sofre
        exp_home_corners = (avg_corners_h_for + avg_corners_a_against) / 2
        
        # Média que o Visitante faz fora
        avg_corners_a_for = a_games.get('cantos_visitante', a_games['gols_visitante']*0).mean()
        # Média que o Mandante SOFRE em casa
        avg_corners_h_against = h_games.get('cantos_visitante', h_games['gols_visitante']*0).mean()
        
        exp_away_corners = (avg_corners_a_for + avg_corners_h_against) / 2
        
        total_corners = exp_home_corners + exp_away_corners

        # --- CARTÕES (NOVO: Lógica detalhada) ---
        # Cartões que o Mandante recebe em casa
        cards_h = h_games.get('amarelos_mandante', h_games['gols_mandante']*0).mean() + \
                  h_games.get('vermelhos_mandante', h_games['gols_mandante']*0).mean()
        
        # Cartões que o Visitante recebe fora
        cards_a = a_games.get('amarelos_visitante', a_games['gols_visitante']*0).mean() + \
                  a_games.get('vermelhos_visitante', a_games['gols_visitante']*0).mean()

        total_cards = cards_h + cards_a

        return {
            'exp_corners_home': round(exp_home_corners, 2),
            'exp_corners_away': round(exp_away_corners, 2),
            'exp_corners_total': round(total_corners, 2),
            'exp_cards_home': round(cards_h, 2), # Adicionado individual
            'exp_cards_away': round(cards_a, 2), # Adicionado individual
            'exp_cards_total': round(total_cards, 2)
        }

    def predict_match(self, home_team, away_team):
        # ... (Mantém igual, só garante que chama a função nova) ...
        home_stats = self.calculate_strength(home_team)
        away_stats = self.calculate_strength(away_team)
        
        if not home_stats or not away_stats: return None

        home_xg = home_stats['attack_home'] * away_stats['defense_away'] * self.league_avgs['home_goals']
        away_xg = away_stats['attack_away'] * home_stats['defense_home'] * self.league_avgs['away_goals']

        probs = np.zeros((6, 6))
        for h in range(6):
            for a in range(6):
                probs[h, a] = poisson.pmf(h, home_xg) * poisson.pmf(a, away_xg)

        prob_home_win = np.sum(np.tril(probs, -1))
        prob_draw = np.sum(np.diag(probs))
        prob_away_win = np.sum(np.triu(probs, 1))

        secondary = self.predict_corners_cards(home_team, away_team)

        return {
            'home_team': home_team, 'away_team': away_team,
            'lambda_home': round(home_xg, 2),
            'lambda_away': round(away_xg, 2),
            'prob_home': round(prob_home_win * 100, 1),
            'prob_draw': round(prob_draw * 100, 1),
            'prob_away': round(prob_away_win * 100, 1),
            'score_matrix': probs,
            'secondary_metrics': secondary 
        }