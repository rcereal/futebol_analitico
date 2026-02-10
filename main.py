from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from src.processor import DataProcessor
from src.analyzer import StatisticalEngine
from src.predictor import BetAdvisor

# Inicializa o console do Rich
console = Console()

def main():
    # 1. Cabeçalho e Carregamento
    console.print(Panel.fit("[bold green]⚽ Sistema de Análise Estatística - Premier League[/bold green]"))
    
    with console.status("[bold green]Carregando dados da temporada...", spinner="dots"):
        processor = DataProcessor()
        df = processor.df
        engine = StatisticalEngine(df)
        advisor = BetAdvisor(engine)
        times = processor.listar_times()
    
    console.print(f"✅ [bold blue]{len(times)} times carregados com sucesso![/bold blue]\n")

    while True:
        # 2. Exibe Lista de Times
        console.print("[bold yellow]Escolha os times para o confronto:[/bold yellow]")
        
        # Cria uma tabela visual para organizar os times
        tabela_times = Table(show_header=False, box=None)
        for _ in range(4): 
            tabela_times.add_column("Time", style="cyan")
        
        # Preenche a tabela em 4 colunas
        for i in range(0, len(times), 4):
            row = times[i:i+4]
            while len(row) < 4: row.append("")
            tabela_times.add_row(*row)
            
        console.print(tabela_times)
        console.print("-" * 50)

        # 3. Pergunta ao Usuário
        mandante = Prompt.ask("🏠 Digite o MANDANTE", choices=times)
        visitante = Prompt.ask("✈️  Digite o VISITANTE", choices=times)
        
        if mandante == visitante:
            console.print("[bold red]❌ Erro: Um time não pode jogar contra ele mesmo![/bold red]")
            continue

        # 4. Processa a Análise
        analise = advisor.get_match_suggestion(mandante, visitante)
        
        if "erro" in analise:
            console.print(f"[bold red]Erro: {analise['erro']}[/bold red]")
            continue

        # 5. Exibe Relatório Visual
        stats = analise['stats']
        
        # Tabela: Forças e Expectativas
        grid = Table(title=f"\n📊 Estatísticas: {mandante} vs {visitante}", show_lines=True)
        grid.add_column("Métrica", style="white")
        grid.add_column(f"{mandante} (Casa)", justify="center", style="green")
        grid.add_column(f"{visitante} (Fora)", justify="center", style="blue")
        
        st_home = engine.calculate_strength(mandante)
        st_away = engine.calculate_strength(visitante)
        
        grid.add_row("Força de Ataque", f"{st_home['attack_home']:.2f}", f"{st_away['attack_away']:.2f}")
        grid.add_row("Força de Defesa", f"{st_home['defense_home']:.2f}", f"{st_away['defense_away']:.2f}")
        grid.add_row("xG (Gols Esperados)", f"{stats['lambda_home']}", f"{stats['lambda_away']}")
        
        console.print(grid)

        # Tabela: Probabilidades (Poisson)
        probs = Table(title="🎲 Probabilidades (Poisson)", show_lines=True)
        probs.add_column("Resultado", style="yellow")
        probs.add_column("Chance", justify="right", style="bold magenta")
        
        probs.add_row(f"Vitória {mandante}", f"{stats['prob_home']}%")
        probs.add_row("Empate", f"{stats['prob_draw']}%")
        probs.add_row(f"Vitória {visitante}", f"{stats['prob_away']}%")
        
        console.print(probs)

        # Painel: Sugestões (Tips)
        console.print("\n[bold cyan]💡 Sugestões de Entrada (Tips):[/bold cyan]")
        
        if not analise['sugestoes']:
            console.print("[italic red]Nenhuma oportunidade de valor claro encontrada.[/italic red]")
        else:
            for tip in analise['sugestoes']:
                cor = "green" if tip['confianca'] == "Alta" else "yellow"
                
                texto = (
                    f"[bold]{tip['mercado']}:[/bold] {tip['selecao']}\n"
                    f"📊 Probabilidade: {tip['probabilidade']}\n"
                    f"💰 Odd Justa: [bold]{tip['odd_justa']}[/bold]\n"
                    f"🔒 Confiança: [{cor}]{tip['confianca']}[/{cor}]"
                )
                
                console.print(Panel(texto, expand=False, border_style=cor))

        # 6. Loop de Repetição
        print("\n")
        if not Confirm.ask("Deseja analisar outro jogo?"):
            break
        console.clear()

if __name__ == "__main__":
    main()