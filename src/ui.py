"""
src/ui.py — Interface CLI estilo Claude Code para Mission Control AI · EnviroSat.

Bibliotecas:
  - Rich           : painéis, tabelas, markdown, spinners
  - prompt-toolkit : input editável com histórico (setas)  [com fallback para input()]
  - PyFiglet       : banner ASCII

Comandos disponíveis:
  /help     — Exibe tabela de ajuda
  /status   — Snapshot rápido da telemetria (sem chamar IA)
  /cenario  — Força um cenário de teste (incendio, energia_critica, etc.)
  /clear    — Limpa o terminal
  /about    — Informações do projeto
  /exit     — Encerra o sistema

COMPATIBILIDADE WINDOWS:
  Execute sempre via terminal real:
    - Windows: cmd.exe  →  python main.py
    - Windows: PowerShell  →  python main.py
  Rodar pelo botão "Run" do PyCharm/VSCode pode causar erro de console.
  Se ocorrer, o sistema entra em modo fallback usando input() nativo.
"""

from datetime import datetime

import pyfiglet
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

# Cenários de teste disponíveis
CENARIOS_VALIDOS = [
    "normal",
    "incendio",
    "energia_critica",
    "buffer_cheio",
    "degradacao_optica",
]


# ── Inicialização do prompt-toolkit (com fallback seguro) ─────────────────────

def _criar_session():
    """
    Tenta criar PromptSession do prompt-toolkit.
    Em ambientes sem console real (PyCharm Run, Jupyter, etc.),
    retorna None — o run_cli usa input() nativo como fallback.
    """
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import InMemoryHistory
        from prompt_toolkit.styles import Style

        estilo = Style.from_dict({"prompt": "#06B6D4 bold"})
        return PromptSession(history=InMemoryHistory(), style=estilo)
    except Exception:
        return None


# ── Banner ────────────────────────────────────────────────────────────────────

def _exibir_banner():
    """Exibe banner ASCII colorido com identidade do projeto."""
    try:
        linha1 = pyfiglet.figlet_format("Mission Control", font="ansi_shadow")
        linha2 = pyfiglet.figlet_format("EnviroSat", font="ansi_shadow")
    except Exception:
        linha1 = "MISSION CONTROL\n"
        linha2 = "ENVIROSAT\n"

    console.print(Align.center(Text(linha1, style="bold #A855F7")))
    console.print(Align.center(Text(linha2, style="bold #06B6D4")))
    console.print(Align.center(
        Text(
            "── 2026 · Prompt Engineering and AI · FIAP · Ciência da Computação ──",
            style="italic #8484A0"
        )
    ))
    console.print()

    console.print(Panel.fit(
        "[bold #06B6D4]Satélite de observação ambiental · Amazônia Legal [/]\n"
        "Monitoramento de incêndios, desmatamento e impacto terrestre por IA generativa.\n\n"
        "  [dim]Digite sua pergunta e pressione Enter · /help para ver comandos[/]\n"
        "  [dim]Modelo: gpt-oss:120b via Ollama Cloud[/]",
        title="[bold #A855F7] MISSION CONTROL AI — EnviroSat [/]",
        border_style="#06B6D4",
    ))
    console.print()


# ── Tabela de ajuda ───────────────────────────────────────────────────────────

def _exibir_ajuda():
    tabela = Table(
        title="[bold #06B6D4]Comandos disponíveis[/]",
        border_style="#A855F7",
        show_lines=True,
    )
    tabela.add_column("Comando", style="bold #06B6D4", min_width=22)
    tabela.add_column("Descrição", style="white")

    tabela.add_row("/help", "Exibe esta tabela de ajuda")
    tabela.add_row("/status", "Snapshot rápido da telemetria atual (sem IA)")
    tabela.add_row(
        "/cenario <nome>",
        "Força um cenário de teste:\n"
        "  normal | incendio | energia_critica\n"
        "  buffer_cheio | degradacao_optica",
    )
    tabela.add_row("/clear", "Limpa o terminal e reexibe o banner")
    tabela.add_row("/about", "Informações do projeto e equipe")
    tabela.add_row("/exit", "Encerra o Mission Control AI")
    tabela.add_row("[dim]<qualquer texto>[/]", "Envia pergunta para análise da IA com dados reais")

    console.print(tabela)


# ── About ─────────────────────────────────────────────────────────────────────

def _exibir_about():
    console.print(Panel(
        "[bold #06B6D4]Mission Control AI — EnviroSat[/]\n\n"
        "[bold]Disciplina:[/] Prompt Engineering and Artificial Intelligence\n"
        "[bold]Curso:[/] Ciência da Computação · FIAP\n"
        "[bold]Global Solution:[/] 2026\n"
        "[bold]Trilha:[/] EnviroSat — Observação Ambiental\n\n"
        "[bold]Satélite simulado:[/] EnviroSat-BR1 (baseado em Amazônia-1 / Landsat)\n"
        "[bold]Área monitorada:[/] Amazônia Legal — Setor Norte\n"
        "[bold]Modelo de IA:[/] gpt-oss:120b via Ollama Cloud\n\n"
        "[bold]Parâmetros monitorados:[/]\n"
        "  • Sensor térmico (focos de calor)\n"
        "  • Sensor óptico RGB+NIR (qualidade de imagem)\n"
        "  • Buffer de imagens não transmitidas\n"
        "  • Precisão de geolocalização\n"
        "  • Energia disponível (painéis solares)",
        title="[bold #A855F7] Sobre o projeto[/]",
        border_style="#06B6D4",
    ))


# ── Renderização de resposta ──────────────────────────────────────────────────

def _exibir_resposta(texto: str, titulo: str = " Mission Control AI"):
    """Renderiza resposta da IA em painel com timestamp."""
    agora = datetime.now().strftime("%H:%M:%S")
    console.print(Panel(
        texto,
        title=f"[bold #A855F7]{titulo}[/]",
        subtitle=f"[dim]{agora}[/]",
        border_style="#06B6D4",
    ))
    console.print()


def _exibir_erro(mensagem: str):
    """Renderiza mensagem de erro."""
    console.print(Panel(
        f"[bold red]{mensagem}[/]",
        title="[bold red] Erro[/]",
        border_style="red",
    ))


def _ler_entrada(session, usar_prompt_toolkit: bool) -> str:
    """
    Lê entrada do usuário.
    Usa prompt-toolkit se disponível, senão usa input() nativo.
    """
    if usar_prompt_toolkit and session is not None:
        return session.prompt("❯ ").strip()
    else:
        # Fallback: input() nativo — funciona em qualquer ambiente
        console.print("[bold #06B6D4]❯ [/]", end="")
        return input().strip()


# ── Loop principal ────────────────────────────────────────────────────────────

def run_cli(engine):
    """Loop principal da CLI — recebe o MissionEngine e gerencia a interação."""

    # Cria a sessão DENTRO da função (nunca no módulo) para evitar
    # NoConsoleScreenBufferError no Windows/PyCharm
    session = _criar_session()
    usar_prompt_toolkit = session is not None

    if not usar_prompt_toolkit:
        console.print(
            "[dim] Modo compatibilidade ativado (input nativo). "
            "Para setas de histórico, execute via cmd.exe ou PowerShell.[/]\n"
        )

    _exibir_banner()

    if not engine.is_ready():
        console.print(
            "Engine status: [yellow]AGUARDANDO IMPLEMENTAÇÃO [/]\n",
            style="yellow",
        )
    else:
        console.print(
            "Engine status: [bold green]PRONTO [/] · "
            f"Trilha: [bold #06B6D4]{engine.trilha.upper()}[/]\n"
        )

    while True:
        try:
            entrada = _ler_entrada(session, usar_prompt_toolkit)
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Encerrando Mission Control AI...[/]")
            break

        if not entrada:
            continue

        # ── Comandos especiais ────────────────────────────────────────────────

        if entrada in ("/exit", "/sair"):
            console.print("[dim]Encerrando Mission Control AI. Até logo! [/]")
            break

        if entrada in ("/help", "/ajuda"):
            _exibir_ajuda()
            continue

        if entrada in ("/about", "/sobre"):
            _exibir_about()
            continue

        if entrada in ("/clear", "/limpar"):
            console.clear()
            _exibir_banner()
            continue

        if entrada == "/status":
            with console.status("[bold #06B6D4]Coletando telemetria...[/]", spinner="dots"):
                snapshot = engine.status_snapshot()
            _exibir_resposta(snapshot, titulo=" Status da Missão")
            continue

        # /cenario <nome>
        if entrada.startswith("/cenario"):
            partes = entrada.split()
            if len(partes) < 2:
                console.print(
                    f"[yellow]Uso: /cenario <nome>\n"
                    f"Cenários válidos: {', '.join(CENARIOS_VALIDOS)}[/]"
                )
                continue
            nome_cenario = partes[1].lower()
            if nome_cenario not in CENARIOS_VALIDOS:
                _exibir_erro(
                    f"Cenário '{nome_cenario}' não reconhecido.\n"
                    f"Cenários válidos: {', '.join(CENARIOS_VALIDOS)}"
                )
                continue

            console.print(f"\n[bold #A855F7] Forçando cenário: {nome_cenario.upper()}[/]\n")
            with console.status(
                f"[bold #06B6D4]Simulando cenário '{nome_cenario}'...[/]",
                spinner="dots",
            ):
                snapshot = engine.status_snapshot(cenario=nome_cenario)
            _exibir_resposta(snapshot, titulo=f" Cenário: {nome_cenario.upper()}")
            continue

        # ── Análise completa com IA ───────────────────────────────────────────
        cenario_inline = None
        pergunta = entrada
        for nome in CENARIOS_VALIDOS:
            if entrada.lower().startswith(nome + ":"):
                cenario_inline = nome
                pergunta = entrada[len(nome) + 1:].strip()
                break

        with console.status(
            "[bold #06B6D4]Coletando telemetria e consultando IA...[/]",
            spinner="earth",
        ):
            resposta = engine.analyze(pergunta, cenario=cenario_inline)

        _exibir_resposta(resposta)