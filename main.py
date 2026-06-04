"""
Mission Control AI — EnviroSat
Ponto de entrada do sistema.

Disciplina: Prompt Engineering and Artificial Intelligence
FIAP · Ciência da Computação · Global Solution 2026
"""

from src.ui import run_cli
from src.engine import MissionEngine

if __name__ == "__main__":
    engine = MissionEngine()
    run_cli(engine)
