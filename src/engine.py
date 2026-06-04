"""
src/engine.py — Motor de análise da Mission Control AI · EnviroSat.

Combina:
  - Coleta de telemetria (src/telemetria.py)
  - Avaliação de alertas em Python puro (src/alertas.py)
  - Chamada à IA via Ollama Cloud com injeção dinâmica de dados
  - Memória dos últimos ciclos (diferencial: consciência temporal)
"""

import os
from pathlib import Path
from collections import deque
from datetime import datetime

from ollama import Client
from dotenv import load_dotenv

from src import telemetria as tel
from src import alertas as alrt

load_dotenv()

# ── Identificação da trilha ───────────────────────────────────────────────────
TRILHA = "envirosat"  # "agrosat" | "envirosat" | "connectsat" | "mobilitysat"

# ── Cliente Ollama Cloud ──────────────────────────────────────────────────────
# .strip() remove espaços, \n e aspas acidentais do .env
_api_key = os.environ.get("OLLAMA_API_KEY", "").strip().strip('"').strip("'")

client = Client(
    host="https://ollama.com",
    headers={"Authorization": "Bearer " + _api_key},
)

if _api_key:
    print(f"API KEY carregada: OK")
else:
    print("API KEY carregada: FALTANDO → crie o arquivo .env com OLLAMA_API_KEY=sua_chave")


# ── Função única de integração com a IA ──────────────────────────────────────

def llm(prompt: str, system: str = None, max_tokens: int = 900,
        temperature: float = 0.3) -> str:
    """
    Envia prompt ao gpt-oss:120b via Ollama Cloud e retorna texto.
    É o único ponto de contato do projeto com o modelo de linguagem.
    """
    mensagens = []
    if system:
        mensagens.append({"role": "system", "content": system})
    mensagens.append({"role": "user", "content": prompt})

    try:
        resposta = client.chat(
            model="gpt-oss:120b",
            messages=mensagens,
            options={"num_predict": max_tokens, "temperature": temperature},
            stream=False,
        )
        return resposta["message"]["content"].strip()
    except Exception as e:
        erro_str = str(e)

        if "401" in erro_str or "unauthorized" in erro_str.lower():
            return (
                "Erro 401 — Chave API inválida ou expirada.\n\n"
                "SOLUÇÃO PASSO A PASSO:\n"
                "  1. Acesse https://ollama.com e faça login\n"
                "  2. Vá em Settings → API Keys\n"
                "  3. Gere uma nova chave\n"
                "  4. Abra o arquivo .env na raiz do projeto\n"
                "  5. Substitua: OLLAMA_API_KEY=sua_nova_chave_aqui\n"
                "     (sem aspas, sem espaços antes ou depois)\n"
                "  6. Reinicie o main.py\n\n"
                "DIAGNÓSTICO: execute  python testar_api.py  para mais detalhes."
            )
        elif "404" in erro_str:
            return (
                "⚠️  Erro 404 — Modelo não encontrado.\n\n"
                "O modelo gpt-oss:120b pode não estar disponível na sua conta.\n"
                "Execute  python testar_api.py  para diagnóstico completo."
            )
        elif "timeout" in erro_str.lower() or "connection" in erro_str.lower():
            return (
                "⚠️  Sem conexão com Ollama Cloud.\n\n"
                "Verifique sua conexão com a internet e tente novamente.\n"
                "Execute  python testar_api.py  para diagnóstico completo."
            )
        else:
            return (
                f"Erro ao consultar a IA: {e}\n\n"
                "Execute  python testar_api.py  para diagnóstico completo."
            )


def _carregar_system_prompt() -> str:
    """Lê o system prompt do arquivo prompts/system_prompt.md."""
    caminho = Path("prompts/system_prompt.md")
    if caminho.exists():
        return caminho.read_text(encoding="utf-8")
    # fallback genérico caso o arquivo não exista
    return (
        "Você é um sistema de análise de telemetria de satélite ambiental. "
        "Analise os dados fornecidos e explique o impacto terrestre de cada anomalia."
    )


# ── Classe principal ──────────────────────────────────────────────────────────

class MissionEngine:
    """
    Motor de análise do Mission Control AI.

    Responsável por:
      1. Coletar telemetria simulada
      2. Avaliar alertas via lógica Python
      3. Montar prompt com contexto histórico + dados atuais
      4. Chamar a IA e retornar análise contextualizada
    """

    # Quantos ciclos manter na memória (diferencial: consciência temporal)
    MEMORIA_CICLOS = 5

    def __init__(self):
        self.trilha = TRILHA
        self.system_prompt = _carregar_system_prompt()
        self.historico: deque = deque(maxlen=self.MEMORIA_CICLOS)
        self._ultimo_snapshot: dict = None
        self._pronto = True  # análise implementada

    def is_ready(self) -> bool:
        """Retorna True se o engine está implementado e pronto."""
        return self._pronto

    # ── Status snapshot ───────────────────────────────────────────────────────

    def status_snapshot(self, cenario: str = None) -> str:
        """
        Coleta telemetria, avalia alertas e retorna resumo textual
        sem chamar a IA (resposta rápida para o comando /status).
        """
        dados = tel.coletar(forcar_cenario=cenario)
        resultado = alrt.avaliar(dados)
        self._ultimo_snapshot = {"telemetria": dados, "alertas": resultado}
        self.historico.append(self._ultimo_snapshot)

        linhas = [
            tel.formatar_para_display(dados),
            "",
            "─" * 50,
            alrt.resumo_texto(resultado),
        ]
        return "\n".join(linhas)

    # ── Análise completa com IA ───────────────────────────────────────────────

    def analyze(self, pergunta_usuario: str, cenario: str = None) -> str:
        """
        Fluxo completo:
          1. Coleta telemetria (ou usa último snapshot se recente)
          2. Avalia alertas em Python
          3. Monta prompt com histórico + dados atuais + pergunta
          4. Chama llm() com o system prompt contextual
          5. Retorna resposta da IA
        """
        # 1. Coletar dados frescos
        dados = tel.coletar(forcar_cenario=cenario)
        resultado_alertas = alrt.avaliar(dados)

        # Salvar na memória de ciclos
        snapshot = {"telemetria": dados, "alertas": resultado_alertas}
        self.historico.append(snapshot)
        self._ultimo_snapshot = snapshot

        # 2. Montar contexto histórico (diferencial: memória de ciclos)
        historico_txt = self._formatar_historico()

        # 3. Montar prompt dinâmico com todos os dados injetados
        prompt = self._montar_prompt(
            dados=dados,
            resultado_alertas=resultado_alertas,
            pergunta=pergunta_usuario,
            historico=historico_txt,
        )

        # 4. Chamar a IA
        resposta = llm(prompt, system=self.system_prompt, temperature=0.3)

        return resposta

    # ── Helpers internos ──────────────────────────────────────────────────────

    def _formatar_historico(self) -> str:
        """
        Formata os últimos N ciclos da memória para inserir no prompt.
        Permite que a IA perceba tendências (ex: energia caindo gradualmente).
        """
        if len(self.historico) <= 1:
            return "Nenhum ciclo anterior registrado nesta sessão."

        linhas = [f"Últimos {len(self.historico) - 1} ciclo(s) anteriores:"]
        # Ignora o último (atual) — só histórico
        ciclos_passados = list(self.historico)[:-1]
        for snp in ciclos_passados:
            t = snp["telemetria"]
            d = t["dados"]
            nivel = snp["alertas"]["nivel_geral"]
            linhas.append(
                f"  [{t['timestamp']}] Ciclo #{t['ciclo']} | STATUS: {nivel} | "
                f"Temp: {d['sensor_termico_celsius']}°C | "
                f"Energia: {d['energia_disponivel_pct']}% | "
                f"Buffer: {d['buffer_imagens_pct']}% | "
                f"Óptico: {d['sensor_optico_qualidade']}%"
            )
        return "\n".join(linhas)

    def _montar_prompt(self, dados: dict, resultado_alertas: dict,
                       pergunta: str, historico: str) -> str:
        """
        Constrói o prompt dinâmico com todos os dados injetados.
        Segue o padrão: CONTEXTO → HISTÓRICO → DADOS ATUAIS →
                        ALERTAS → AÇÕES → PERGUNTA
        """
        d = dados["dados"]
        alertas_txt = "\n".join(
            f"  [{a['nivel']}] {a['parametro'].upper()}: {a['mensagem']}\n"
            f"           Impacto terrestre: {a['impacto_terrestre']}"
            for a in resultado_alertas["alertas"]
        )

        acoes_txt = (
            "\n".join(f"  → {a}" for a in resultado_alertas["acoes_automaticas"])
            if resultado_alertas["acoes_automaticas"]
            else "  Nenhuma ação automática disparada."
        )

        prompt = f"""
=== TELEMETRIA ATUAL — EnviroSat-BR1 ===
Timestamp : {dados['timestamp']}
Ciclo     : #{dados['ciclo']}
Satélite  : {dados['satelite']} | Órbita: {dados['orbita']}
Área      : {dados['area_monitorada']}

PARÂMETROS MONITORADOS:
  • Sensor Térmico         : {d['sensor_termico_celsius']}°C
  • Sensor Óptico (qualid) : {d['sensor_optico_qualidade']}%
  • Buffer de Imagens      : {d['buffer_imagens_pct']}%
  • Geolocalização (prec)  : ±{d['geolocalizacao_precisao_m']}m
  • Energia Disponível     : {d['energia_disponivel_pct']}%

STATUS GERAL: {resultado_alertas['nivel_geral']}
Total de alertas ativos: {resultado_alertas['total_alertas']}

ALERTAS DETECTADOS (avaliação Python):
{alertas_txt}

AÇÕES AUTOMÁTICAS JÁ EXECUTADAS:
{acoes_txt}

=== HISTÓRICO DESTA SESSÃO ===
{historico}

=== PERGUNTA DO OPERADOR ===
{pergunta}

Responda de forma clara e estruturada, conectando sempre a análise técnica
ao impacto terrestre no Brasil (agricultores, brigadas, INPE, IBAMA, comunidades).
""".strip()

        return prompt