"""
banner_ascii.py — Gerador de banner ASCII para Mission Control AI.

Uso:
  python banner_ascii.py              # Banner padrão
  python banner_ascii.py -fonts       # Lista as 570+ fontes do PyFiglet
  python banner_ascii.py -font slant  # Testa uma fonte específica
  python banner_ascii.py -demo        # Demo com 8 fontes lado a lado
"""

import sys
import pyfiglet
from rich.console import Console
from rich.align import Align
from rich.text import Text
from rich.panel import Panel

console = Console()


def exibir_banner_padrao():
    """Exibe o banner padrão do Mission Control AI em ASCII art."""
    linha1 = pyfiglet.figlet_format("Global Solution", font="ansi_shadow")
    linha2 = pyfiglet.figlet_format("Mission Control AI", font="ansi_shadow")

    console.print(Align.center(Text(linha1, style="bold #A855F7")))
    console.print(Align.center(Text(linha2, style="bold #06B6D4")))
    console.print(Align.center(
        Text(
            "── 2026.1 · Prompt Engineering and AI · FIAP · EnviroSat ──",
            style="italic #8484A0"
        )
    ))


def listar_fontes():
    """Lista todas as fontes disponíveis no PyFiglet."""
    fontes = pyfiglet.FigletFont.getFonts()
    console.print(Panel(
        f"[bold #06B6D4]{len(fontes)} fontes disponíveis:[/]\n" +
        "  ".join(sorted(fontes)),
        title="Fontes PyFiglet",
        border_style="#A855F7"
    ))


def testar_fonte(fonte: str, texto: str = "EnviroSat"):
    """Testa uma fonte específica."""
    try:
        resultado = pyfiglet.figlet_format(texto, font=fonte)
        console.print(Text(resultado, style="bold #06B6D4"))
        console.print(f"[dim]Fonte: {fonte}[/]")
    except pyfiglet.FontNotFound:
        console.print(f"[red]Fonte '{fonte}' não encontrada. Use -fonts para listar.[/]")


def demo_fontes():
    """Demonstra 8 fontes diferentes lado a lado."""
    fontes_demo = ["ansi_shadow", "slant", "big", "banner3", "block", "doom", "isometric1", "lean"]
    texto = "EnviroSat"
    for fonte in fontes_demo:
        try:
            resultado = pyfiglet.figlet_format(texto, font=fonte)
            console.print(Panel(
                Text(resultado, style="bold #06B6D4"),
                title=f"[#A855F7]{fonte}[/]",
                border_style="dim"
            ))
        except Exception:
            pass


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        exibir_banner_padrao()
    elif "-fonts" in args:
        listar_fontes()
    elif "-demo" in args:
        demo_fontes()
    elif "-font" in args:
        idx = args.index("-font")
        fonte = args[idx + 1] if idx + 1 < len(args) else "slant"
        texto_idx = args.index("-text") if "-text" in args else -1
        texto = args[texto_idx + 1] if texto_idx != -1 and texto_idx + 1 < len(args) else "EnviroSat"
        testar_fonte(fonte, texto)
    else:
        exibir_banner_padrao()
