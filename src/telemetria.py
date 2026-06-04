"""
src/telemetria.py — Geração de dados simulados de telemetria do EnviroSat.

Simula um satélite de observação ambiental com sensor térmico e óptico,
similar ao Amazônia-1 ou Landsat, monitorando a Amazônia brasileira.

Parâmetros monitorados:
  - sensor_termico_celsius   : temperatura do sensor térmico (detecta focos de calor)
  - sensor_optico_qualidade  : qualidade do sensor óptico RGB+NIR (%)
  - buffer_imagens_pct       : ocupação do buffer de imagens não transmitidas (%)
  - geolocalizacao_precisao_m: precisão da geolocalização (metros — menor é melhor)
  - energia_disponivel_pct   : energia disponível nos painéis solares (%)
"""

import random
from datetime import datetime

# Faixas normais de operação (limites ideais do satélite)
RANGES_NORMAIS = {
    "sensor_termico_celsius":    (15.0, 55.0),
    "sensor_optico_qualidade":   (70.0, 100.0),
    "buffer_imagens_pct":        (0.0,  75.0),
    "geolocalizacao_precisao_m": (5.0,  50.0),
    "energia_disponivel_pct":    (30.0, 100.0),
}

# Estado interno para simular deriva temporal (drift)
_ciclo = 0
_tendencia_energia = 0.0  # simula consumo gradual


def coletar(forcar_cenario: str = None) -> dict:
    """
    Coleta (simula) dados de telemetria do EnviroSat.

    Args:
        forcar_cenario: None (aleatório) | "normal" | "incendio" |
                        "energia_critica" | "buffer_cheio" | "degradacao_optica"

    Returns:
        Dicionário com os parâmetros de telemetria e metadados.
    """
    global _ciclo, _tendencia_energia
    _ciclo += 1

    if forcar_cenario == "incendio":
        # Foco de calor intenso detectado na região amazônica
        dados = {
            "sensor_termico_celsius":    round(random.uniform(78.0, 95.0), 1),
            "sensor_optico_qualidade":   round(random.uniform(55.0, 75.0), 1),
            "buffer_imagens_pct":        round(random.uniform(60.0, 88.0), 1),
            "geolocalizacao_precisao_m": round(random.uniform(8.0, 25.0), 1),
            "energia_disponivel_pct":    round(random.uniform(45.0, 70.0), 1),
        }
    elif forcar_cenario == "energia_critica":
        # Satélite entrando em modo de baixa energia
        dados = {
            "sensor_termico_celsius":    round(random.uniform(20.0, 40.0), 1),
            "sensor_optico_qualidade":   round(random.uniform(40.0, 65.0), 1),
            "buffer_imagens_pct":        round(random.uniform(50.0, 75.0), 1),
            "geolocalizacao_precisao_m": round(random.uniform(30.0, 80.0), 1),
            "energia_disponivel_pct":    round(random.uniform(8.0, 19.0), 1),
        }
    elif forcar_cenario == "buffer_cheio":
        # Buffer de imagens saturado — risco de perda de dados
        dados = {
            "sensor_termico_celsius":    round(random.uniform(25.0, 50.0), 1),
            "sensor_optico_qualidade":   round(random.uniform(75.0, 95.0), 1),
            "buffer_imagens_pct":        round(random.uniform(92.0, 99.9), 1),
            "geolocalizacao_precisao_m": round(random.uniform(10.0, 35.0), 1),
            "energia_disponivel_pct":    round(random.uniform(55.0, 80.0), 1),
        }
    elif forcar_cenario == "degradacao_optica":
        # Sensor óptico degradado (possível impacto de micrometeoro)
        dados = {
            "sensor_termico_celsius":    round(random.uniform(20.0, 45.0), 1),
            "sensor_optico_qualidade":   round(random.uniform(15.0, 38.0), 1),
            "buffer_imagens_pct":        round(random.uniform(20.0, 50.0), 1),
            "geolocalizacao_precisao_m": round(random.uniform(80.0, 150.0), 1),
            "energia_disponivel_pct":    round(random.uniform(40.0, 75.0), 1),
        }
    elif forcar_cenario == "normal":
        # Operação normal dentro dos parâmetros ideais
        dados = {
            "sensor_termico_celsius":    round(random.uniform(22.0, 45.0), 1),
            "sensor_optico_qualidade":   round(random.uniform(85.0, 99.0), 1),
            "buffer_imagens_pct":        round(random.uniform(10.0, 60.0), 1),
            "geolocalizacao_precisao_m": round(random.uniform(8.0, 30.0), 1),
            "energia_disponivel_pct":    round(random.uniform(60.0, 95.0), 1),
        }
    else:
        # Geração aleatória com leve deriva temporal (mais realista)
        _tendencia_energia = max(-20, min(20, _tendencia_energia + random.uniform(-3, 2)))
        dados = {
            "sensor_termico_celsius":    round(random.uniform(15.0, 95.0), 1),
            "sensor_optico_qualidade":   round(random.uniform(25.0, 100.0), 1),
            "buffer_imagens_pct":        round(random.uniform(5.0, 100.0), 1),
            "geolocalizacao_precisao_m": round(random.uniform(5.0, 150.0), 1),
            "energia_disponivel_pct":    max(5.0, min(100.0,
                round(random.uniform(25.0, 95.0) + _tendencia_energia, 1)
            )),
        }

    return {
        "ciclo": _ciclo,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "satelite": "EnviroSat-BR1",
        "orbita": "LEO 615km",
        "area_monitorada": "Amazônia Legal — Setor Norte",
        "dados": dados,
    }


def formatar_para_display(telemetria: dict) -> str:
    """Formata a telemetria para exibição amigável no terminal."""
    d = telemetria["dados"]
    linhas = [
        f"Satélite : {telemetria['satelite']} | Órbita: {telemetria['orbita']}",
        f"Área     : {telemetria['area_monitorada']}",
        f"Timestamp: {telemetria['timestamp']} (ciclo #{telemetria['ciclo']})",
        "",
        f"Sensor Térmico     : {d['sensor_termico_celsius']}°C",
        f"Sensor Óptico      : {d['sensor_optico_qualidade']}% qualidade",
        f"Buffer Imagens     : {d['buffer_imagens_pct']}% ocupado",
        f"Geolocalização     : ±{d['geolocalizacao_precisao_m']}m precisão",
        f"Energia Disponível : {d['energia_disponivel_pct']}%",
    ]
    return "\n".join(linhas)
