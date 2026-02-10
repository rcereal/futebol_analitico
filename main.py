from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from src.data_loader import DataLoader
from src.processor import DataProcessor
from src.analyzer import StatisticalEngine
from src.predictor import BetAdvisor
import os

console = Console()

def selecionar_campeonato():
    """Exibe menu para escolher o campeonato e baixa os dados."""
    loader = DataLoader()
    ligas = list(loader.LEAGUES.keys())
    
    console.print("[bold yellow]🌎 Campeonatos Disponíveis:[/bold yellow]")
    for i, liga in enumerate(ligas, 1):
        console.print(f"{i}. {liga}")
        
    escolha = Prompt.ask("\nEscolha o número do campeonato", choices=[str(i) for i in range(1, len(ligas)+1)])
    liga_selecionada = ligas[int(escolha)-1]
    
    # Baixa e Salva os dados da liga escolhida
    df = loader.load_data(liga_selecionada)
    caminho_arquivo = loader.save_local(liga_selecionada)
    
    return caminho_arquivo, liga_selecionada

def main():
    console.print(Panel.fit("[bold green]⚽ Sistema de Análise Estatística Multi-Ligas (25/26)[/bold green]"))
    
    while True:
        # 1. Seleção de Campeonato
        caminho_csv, nome_liga = selecionar_campeonato()
        
        if not caminho_csv:
            console.print("[bold red]Falha ao carregar campeonato. Tente outro.[/bold red]")
            continue

        # 2. Inicialização do Processador com o arquivo correto
        with console.status(f"[bold green]Processando dados da {nome_liga}...", spinner="dots"):
            # AQUI ESTÁ O SEGREDO: Passamos o caminho do arquivo específico
            processor = DataProcessor(raw_data_path=caminho_csv)
            
            if processor.df is None:
                console.print("[bold red]Erro ao processar arquivo CSV.[/bold red]")
                continue
                
            df = processor.df
            engine = StatisticalEngine(df)
            advisor = BetAdvisor(engine)
            times = processor.listar_times()
        
        console.print(f"\n✅ [bold blue]{len(times)} times da {nome_liga} carregados![/bold blue]\n")
        
        # Loop de Jogos dentro do mesmo campeonato
        while True:
            # Mostra Tabela de Times
            console.print(f"[bold yellow]Times da {nome_liga}:[/bold yellow]")
            tabela_times = Table(show_header=False, box=None)
            for _ in range(4): tabela_times.add_column("Time", style="cyan")
            
            for i in range(0, len(times), 4):
                row = times[i:i+4]
                while len(row) < 4: row.append("")
                tabela_times.add_row(*row)
            console.print(tabela_times)
            console.print("-" * 50)

            # Seleção de Times
            mandante = Prompt.ask("🏠 Digite o MANDANTE", choices=times)
            visitante = Prompt.ask("✈️  Digite o VISITANTE", choices=times)
            
            if mandante == visitante:
                console.print("[bold red]❌ Erro: Times iguais![/bold red]")
                continue

            # Análise
            analise = advisor.get_match_suggestion(mandante, visitante)
            
            if "erro" in analise:
                console.print(f"[bold red]Erro: {analise['erro']}[/bold red]")
                continue

            # Exibição (Relatório)
            stats = analise['stats']
            sec = stats['secondary_metrics']
            
            # Tabela Stats
            grid = Table(title=f"\n📊 {mandante} vs {visitante} ({nome_liga})", show_lines=True)
            grid.add_column("Métrica", style="white")
            grid.add_column(f"{mandante}", justify="center", style="green")
            grid.add_column(f"{visitante}", justify="center", style="blue")
            
            st_home = engine.calculate_strength(mandante)
            st_away = engine.calculate_strength(visitante)
            
            # Métricas de Gols
            grid.add_row("Força Ataque", f"{st_home['attack_home']:.2f}", f"{st_away['attack_away']:.2f}")
            grid.add_row("Força Defesa", f"{st_home['defense_home']:.2f}", f"{st_away['defense_away']:.2f}")
            grid.add_row("xG (Gols Esperados)", f"{stats['lambda_home']}", f"{stats['lambda_away']}")
            
            # Métricas de Escanteios (Agora com valores corrigidos)
            grid.add_row("Média Escanteios", f"{sec['exp_corners_home']}", f"{sec['exp_corners_away']}")
            
            # Métricas de Cartões (NOVO: Mostra individualmente)
            grid.add_row("Média Cartões", f"{sec['exp_cards_home']}", f"{sec['exp_cards_away']}")
            
            # Totais do Jogo (Destaque)
            grid.add_row("Projeção Jogo (Cantos)", f"{sec['exp_corners_total']}", style="bold yellow")
            grid.add_row("Projeção Jogo (Cartões)", f"{sec['exp_cards_total']}", style="bold red")
            
            console.print(grid)

            # Tabela Probabilidades
            probs = Table(show_header=True)
            probs.add_column("Resultado", style="yellow")
            probs.add_column("Chance", style="magenta")
            probs.add_row(f"Vitória {mandante}", f"{stats['prob_home']}%")
            probs.add_row("Empate", f"{stats['prob_draw']}%")
            probs.add_row(f"Vitória {visitante}", f"{stats['prob_away']}%")
            console.print(probs)

            # Tips
            console.print("\n[bold cyan]💡 Dicas de Aposta:[/bold cyan]")
            if not analise['sugestoes']:
                console.print("[italic red]Sem oportunidades claras.[/italic red]")
            else:
                for tip in analise['sugestoes']:
                    cor = "green" if tip['confianca'] == "Alta" else "yellow"
                    texto = (
                        f"[bold]{tip['mercado']}:[/bold] {tip['selecao']}\n"
                        f"📊 Prob: {tip['probabilidade']} | 💰 Odd Justa: [bold]{tip['odd_justa']}[/bold]\n"
                        f"🔒 Confiança: [{cor}]{tip['confianca']}[/{cor}]"
                    )
                    console.print(Panel(texto, expand=False, border_style=cor))

            print("\n")
            if not Confirm.ask("Analisar outro jogo DESSA liga?"):
                break # Sai do loop de jogos, volta pro loop de ligas ou encerra
            console.clear()
        
        if not Confirm.ask("Escolher outra LIGA? (N para sair)"):
            break
        console.clear()

if __name__ == "__main__":
    main()