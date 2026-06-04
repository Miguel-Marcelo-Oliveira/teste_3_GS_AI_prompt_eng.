"""
src/alertas.py — Lógica de thresholds e tomada de decisão do EnviroSat.

IMPORTANTE: toda decisão de alerta é feita aqui em Python puro,
NÃO delegada à IA. A IA recebe os alertas prontos e os contextualiza
em linguagem natural com impacto terrestre. Isso garante consistência.
"""

# ── Thresholds de alerta ──────────────────────────────────────────────────────

# Sensor térmico (detecta focos de calor/incêndio)
TEMP_AVISO    = 55.0   # °C — acima disso, área pode estar em risco
TEMP_CRITICO  = 75.0   # °C — alerta vermelho: foco de incêndio confirmado

# Qualidade do sensor óptico
OPTICO_AVISO  = 60.0   # % — imagens podem estar comprometidas
OPTICO_CRITICO = 40.0  # % — sensor possivelmente danificado

# Buffer de imagens não transmitidas
BUFFER_AVISO  = 80.0   # % — atenção: downlink necessário em breve
BUFFER_CRITICO = 92.0  # % — risco iminente de perda de dados

# Precisão da geolocalização (menor = melhor)
GEO_AVISO    = 60.0    # m — precisão degradada
GEO_CRITICO  = 100.0   # m — geolocalização não confiável

# Energia disponível
ENERGIA_AVISO   = 30.0  # % — modo de economia recomendado
ENERGIA_CRITICO = 20.0  # % — modo de economia obrigatório

# ── Funções de avaliação ──────────────────────────────────────────────────────

def avaliar(telemetria: dict) -> dict:
    """
    Avalia os dados de telemetria e retorna alertas e ações automáticas.

    Args:
        telemetria: dicionário retornado por telemetria.coletar()

    Returns:
        Dicionário com lista de alertas, nível geral e ações automáticas.
    """
    d = telemetria["dados"]
    alertas = []
    acoes_automaticas = []
    nivel_geral = "NORMAL"   # NORMAL | AVISO | CRITICO

    # ── Avaliação: sensor térmico ─────────────────────────────────────────────
    temp = d["sensor_termico_celsius"]
    if temp >= TEMP_CRITICO:
        alertas.append({
            "parametro": "sensor_termico",
            "nivel": "CRITICO",
            "valor": temp,
            "mensagem": f"FOCO DE INCÊNDIO DETECTADO — Temperatura {temp}°C (limite: {TEMP_CRITICO}°C)",
            "impacto_terrestre": (
                "Possível incêndio ativo na Amazônia Legal. "
                "Brigadas do PREVFOGO e IBAMA devem ser acionadas imediatamente. "
                "Área em risco: comunidades ribeirinhas e fauna protegida."
            ),
        })
        nivel_geral = "CRITICO"
        acoes_automaticas.append("ACIONAR_ALERTA_INCENDIO: Notificação automática enviada ao INPE/IBAMA via protocolo DETER.")
    elif temp >= TEMP_AVISO:
        alertas.append({
            "parametro": "sensor_termico",
            "nivel": "AVISO",
            "valor": temp,
            "mensagem": f"TEMPERATURA ELEVADA — {temp}°C (limite de atenção: {TEMP_AVISO}°C)",
            "impacto_terrestre": (
                "Área apresenta calor anormal. Monitoramento intensificado recomendado. "
                "Pode indicar desmatamento por queimada."
            ),
        })
        if nivel_geral == "NORMAL":
            nivel_geral = "AVISO"

    # ── Avaliação: sensor óptico ──────────────────────────────────────────────
    optico = d["sensor_optico_qualidade"]
    if optico <= OPTICO_CRITICO:
        alertas.append({
            "parametro": "sensor_optico",
            "nivel": "CRITICO",
            "valor": optico,
            "mensagem": f"SENSOR ÓPTICO CRÍTICO — Qualidade em {optico}% (mínimo: {OPTICO_CRITICO}%)",
            "impacto_terrestre": (
                "Imagens de monitoramento ambiental comprometidas. "
                "Alertas de desmatamento do sistema PRODES podem falhar. "
                "Agricultores e órgãos ambientais perdem cobertura desta região."
            ),
        })
        nivel_geral = "CRITICO"
        acoes_automaticas.append("REDIRECIONAR_COBERTURA: Satélite CBERS-4A acionado para cobertura redundante da área.")
    elif optico <= OPTICO_AVISO:
        alertas.append({
            "parametro": "sensor_optico",
            "nivel": "AVISO",
            "valor": optico,
            "mensagem": f"QUALIDADE ÓPTICA REDUZIDA — {optico}% (atenção abaixo de {OPTICO_AVISO}%)",
            "impacto_terrestre": (
                "Resolução das imagens pode estar comprometida. "
                "Revisão técnica do sensor recomendada no próximo ciclo."
            ),
        })
        if nivel_geral == "NORMAL":
            nivel_geral = "AVISO"

    # ── Avaliação: buffer de imagens ──────────────────────────────────────────
    buffer = d["buffer_imagens_pct"]
    if buffer >= BUFFER_CRITICO:
        alertas.append({
            "parametro": "buffer_imagens",
            "nivel": "CRITICO",
            "valor": buffer,
            "mensagem": f"BUFFER SATURADO — {buffer}% ocupado (limite: {BUFFER_CRITICO}%)",
            "impacto_terrestre": (
                "Risco iminente de perda de imagens coletadas. "
                "Dados de desmatamento e focos de calor podem ser perdidos permanentemente. "
                "Downlink de emergência necessário."
            ),
        })
        nivel_geral = "CRITICO"
        acoes_automaticas.append(f"DOWNLINK_EMERGENCIA: Janela de transmissão prioritária solicitada à estação de Cuiabá.")
    elif buffer >= BUFFER_AVISO:
        alertas.append({
            "parametro": "buffer_imagens",
            "nivel": "AVISO",
            "valor": buffer,
            "mensagem": f"BUFFER ELEVADO — {buffer}% (atenção acima de {BUFFER_AVISO}%)",
            "impacto_terrestre": (
                "Downlink recomendado na próxima passagem sobre estação terrestre."
            ),
        })
        if nivel_geral == "NORMAL":
            nivel_geral = "AVISO"

    # ── Avaliação: geolocalização ─────────────────────────────────────────────
    geo = d["geolocalizacao_precisao_m"]
    if geo >= GEO_CRITICO:
        alertas.append({
            "parametro": "geolocalizacao",
            "nivel": "CRITICO",
            "valor": geo,
            "mensagem": f"GEOLOCALIZAÇÃO IMPRECISA — ±{geo}m (limite: {GEO_CRITICO}m)",
            "impacto_terrestre": (
                "Coordenadas de focos e áreas desmatadas não são confiáveis. "
                "Operações de campo do IBAMA podem ir para a localização errada. "
                "Calibração urgente do sistema de atitude do satélite."
            ),
        })
        nivel_geral = "CRITICO"
    elif geo >= GEO_AVISO:
        alertas.append({
            "parametro": "geolocalizacao",
            "nivel": "AVISO",
            "valor": geo,
            "mensagem": f"PRECISÃO REDUZIDA — ±{geo}m (atenção acima de {GEO_AVISO}m)",
            "impacto_terrestre": (
                "Margem de erro nas coordenadas pode afetar ações de fiscalização."
            ),
        })
        if nivel_geral == "NORMAL":
            nivel_geral = "AVISO"

    # ── Avaliação: energia ────────────────────────────────────────────────────
    energia = d["energia_disponivel_pct"]
    if energia <= ENERGIA_CRITICO:
        alertas.append({
            "parametro": "energia",
            "nivel": "CRITICO",
            "valor": energia,
            "mensagem": f"ENERGIA CRÍTICA — {energia}% disponível (mínimo: {ENERGIA_CRITICO}%)",
            "impacto_terrestre": (
                "Satélite em risco de desligamento. "
                "Toda cobertura ambiental desta órbita pode ser interrompida. "
                "Monitoramento de incêndios e desmatamento suspenso até recuperação."
            ),
        })
        nivel_geral = "CRITICO"
        acoes_automaticas.append("MODO_ECONOMIA_ATIVADO: Sensores não-críticos suspensos. Apenas sensor térmico mantido ativo.")
    elif energia <= ENERGIA_AVISO:
        alertas.append({
            "parametro": "energia",
            "nivel": "AVISO",
            "valor": energia,
            "mensagem": f"ENERGIA BAIXA — {energia}% (atenção abaixo de {ENERGIA_AVISO}%)",
            "impacto_terrestre": (
                "Ciclo de captura de imagens pode ser reduzido para conservar energia."
            ),
        })
        if nivel_geral == "NORMAL":
            nivel_geral = "AVISO"

    # ── Resultado final ───────────────────────────────────────────────────────
    if not alertas:
        alertas.append({
            "parametro": "geral",
            "nivel": "NORMAL",
            "valor": None,
            "mensagem": "Todos os sistemas operando dentro dos parâmetros normais.",
            "impacto_terrestre": (
                "Cobertura ambiental da Amazônia Legal operando normalmente. "
                "Dados de monitoramento fluindo para INPE, IBAMA e parceiros."
            ),
        })

    return {
        "nivel_geral": nivel_geral,
        "total_alertas": len([a for a in alertas if a["nivel"] != "NORMAL"]),
        "alertas": alertas,
        "acoes_automaticas": acoes_automaticas,
    }


def resumo_texto(resultado_alertas: dict) -> str:
    """Converte o resultado da avaliação em texto legível para o terminal."""
    linhas = []
    nivel = resultado_alertas["nivel_geral"]

    linhas.append(f" STATUS GERAL: {nivel}")
    linhas.append("")

    for alerta in resultado_alertas["alertas"]:
        linhas.append(f"  {alerta['mensagem']}")

    if resultado_alertas["acoes_automaticas"]:
        linhas.append("")
        linhas.append("AÇÕES AUTOMÁTICAS EXECUTADAS:")
        for acao in resultado_alertas["acoes_automaticas"]:
            linhas.append(f" → {acao}")

    return "\n".join(linhas)
