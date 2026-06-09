# Mission Control AI — EnviroSat

> Sistema de monitoramento operacional de satélite ambiental com análise por IA generativa.
> Amazônia Legal · Detecção de incêndios · Combate ao desmatamento.

---

## Integrantes

| Nome                                   | RM     | Turma |
|----------------------------------------|--------|-------|
| Miguel Marcelo Alves Ramos de Oliveira | 569467 | 1CCPI |
| Felipe de Oliveira Doern               | 568798 | 1CCPI |

**Modalidade:** Dupla

---

## O que o projeto faz

O **Mission Control AI — EnviroSat** simula a operação de um satélite de observação ambiental em órbita baixa sobre a Amazônia Legal brasileira. O sistema:

1. **Gera telemetria simulada** de 5 parâmetros do satélite (sensor térmico, sensor óptico, buffer de imagens, geolocalização e energia).
2. **Avalia alertas em Python puro** — sem delegar decisões à IA — usando thresholds precisos e lógica de decisão estruturada.
3. **Aciona a IA (Ollama Cloud)** para interpretar o estado da missão em linguagem natural, sempre conectando a análise técnica ao impacto terrestre no Brasil.
4. **Mantém memória dos últimos 5 ciclos** para detectar tendências (ex: energia caindo gradualmente) e alertar sobre riscos futuros.

---

## Persona atendida

O sistema atende simultaneamente **três personas**:

- **Operador de centro de controle ambiental (INPE / órgão estadual):** precisa de precisão técnica e dados objetivos sobre o estado do satélite.
- **Coordenador de brigada de combate a incêndio (PREVFOGO / IBAMA):** precisa saber onde e quão grave é a situação — sem tecnicismos.
- **Analista de compliance ambiental:** precisa quantificar impactos e risco legal para relatórios.

A IA identifica o tom da pergunta e adapta a resposta à persona que está interagindo.

---

## Tecnologias utilizadas

| Tecnologia | Versão | Função |
|------------|--------|--------|
| Python | 3.10+ | Linguagem principal |
| Ollama Cloud API | — | Modelo `gpt-oss:120b` |
| ollama (lib) | 0.6.2 | Cliente Python para Ollama Cloud |
| python-dotenv | 1.2.2 | Carregamento seguro de credenciais |
| Rich | 15.0.0 | Painéis, tabelas e formatação no terminal |
| prompt-toolkit | 3.0.52 | Input editável com histórico (setas ↑↓) |
| PyFiglet | 1.0.4 | Banner ASCII no início da CLI |

---

## ▶ Como executar

```bash
# 1. Clone o repositório
git clone https://github.com/Miguel-Marcelo-Oliveira/TESTE_2_GS_IA.git
cd mission-control-ai

# 2. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate          # Linux / macOS
.venv\Scripts\activate             # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as credenciais
cp .env.example .env
# Edite o arquivo .env e insira sua chave Ollama Cloud:
# OLLAMA_API_KEY=sua_chave_aqui

# 5. Execute o sistema
python main.py
```

### Comandos disponíveis na CLI

| Comando | Descrição |
|---------|-----------|
| `/help` | Tabela de ajuda |
| `/status` | Snapshot rápido da telemetria (sem IA) |
| `/cenario <nome>` | Força cenário de teste (veja abaixo) |
| `/clear` | Limpa o terminal |
| `/about` | Informações do projeto |
| `/exit` | Encerra o sistema |
| `<qualquer texto>` | Envia pergunta para análise da IA com dados reais |

### Cenários de teste disponíveis

```bash
/cenario normal           # Operação normal
/cenario incendio         # Foco de incêndio ativo
/cenario energia_critica  # Risco de blackout
/cenario buffer_cheio     # Perda de dados iminente
/cenario degradacao_optica # Sensor óptico danificado
```

---

## Demonstração

As screenshots do sistema funcionando estão disponíveis em `assets`

---

## System Prompt

O system prompt completo está em [`prompts/system_prompt.md`](prompts/system_prompt.md).

Destaques da estratégia de prompting utilizada:

- **Role prompting** com 3 personas (operador, coordenador de brigada, analista)
- **Few-shot prompting** com 2 exemplos completos de análise (cenário de incêndio e energia crítica)
- **Estrutura de output obrigatória:** Diagnóstico → Impacto Terrestre → Recomendações → Tendência
- **Restrições explícitas:** o modelo não inventa dados, sempre conecta análise técnica ao impacto social

---

## Cenários de teste demonstrados

| # | Cenário | O que o sistema demonstra |
|---|---------|--------------------------|
| 1 | **Operação normal** | Todos os parâmetros dentro do range — IA confirma saúde da missão |
| 2 | **Foco de incêndio** | Temperatura crítica → alerta automático → IA aciona brigadas |
| 3 | **Energia crítica** | Modo economia automático → IA projeta tempo até blackout |
| 4 | **Buffer saturado** | Downlink de emergência → IA explica risco de perda de dados |
| 5 | **Degradação óptica** | Sensor comprometido → IA avalia impacto no PRODES/DETER |

---

## Proposta de valor / modelo de negócio

### 1. Qual o problema real terrestre que esta missão resolve?

O Brasil perde, em média, milhares de quilômetros quadrados de floresta amazônica por ano para incêndios e desmatamento ilegal. O principal gargalo não é a falta de satélites — é a velocidade de transformar dados orbitais brutos em decisões humanas acionáveis. Operadores de centro de controle recebem telemetria numérica que precisa de interpretação especializada; coordenadores de brigada precisam de coordenadas e nível de urgência, não de tabelas de parâmetros. O EnviroSat Mission Control AI fecha esse gap com IA generativa: transforma telemetria em linguagem natural contextualizada para cada persona, reduzindo o tempo entre detecção de foco e mobilização de brigada.

### 2. Quem paga pela solução?

Modelo híbrido:
- **Setor público (70%):** INPE, IBAMA e Ministério do Meio Ambiente como clientes primários via contratos de prestação de serviço ou concessão operacional. A AEB (Agência Espacial Brasileira) pode cofinanciar como infraestrutura crítica nacional.
- **Setor privado (30%):** Seguradoras agrícolas e fundos de ESG que precisam de dados de risco ambiental auditáveis para precificação e compliance (ex: certificação de origem, rastreabilidade de cadeias livres de desmatamento).

### 3. Métrica de impacto

Se o EnviroSat-BR1 operar 100% saudável por 1 ano:
- **~2,8 milhões de hectares** da Amazônia Legal monitorados continuamente na faixa orbital do satélite
- **Tempo de resposta a focos de incêndio reduzido de ~6h para ~45min** (detecção orbital → acionamento de brigada via análise de IA)
- **~300 alertas de desmatamento** gerados para o sistema DETER/PRODES com geolocalização de ±15m de precisão
- **Estimativa: 15.000 a 40.000 hectares de floresta preservados** pela resposta mais rápida a incêndios em estágio inicial

### 4. Modelo de negócio

**Dado-como-serviço (DaaS) + SaaS de análise:**
- A camada de telemetria bruta é dado público (seguindo modelo INPE/CBERS).
- A camada de análise por IA (interpretação contextual, alertas priorizados, relatórios automáticos por persona) é o produto comercial.
- Assinatura mensal por número de operadores e áreas monitoradas — modelo escalável para municípios, estados e parceiros internacionais (ex: fundos amazônicos globais).

---

## Limitações conhecidas

- **Dados simulados:** a telemetria é gerada aleatoriamente — não reflete dados reais de satélite em operação.
- **Sem persistência entre sessões:** a memória de ciclos é mantida apenas durante a sessão atual (reiniciar `main.py` apaga o histórico).
- **Dependência de conexão:** a análise por IA requer acesso à Ollama Cloud — sem internet, o sistema retorna mensagem de erro amigável mas não analisa.
- **Modelo não-determinístico:** respostas podem variar entre execuções com os mesmos dados. O system prompt foi ajustado para minimizar variação, mas leituras extremas ainda ocorrem ocasionalmente.
- **Interface apenas CLI:** não há dashboard web ou visualização gráfica de séries temporais (foi priorizado o motor de análise sobre a camada visual).


---

## Vídeo de demonstração
[https://youtu.be/v94nk7ov7ck](https://youtu.be/v94nk7ov7ck)

[Assistir demonstração no YouTube](https://www.youtube.com/watch?v=SEU_ID_AQUI)

> Configurado como "Não listado" no YouTube.
