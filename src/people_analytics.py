"""Funções reutilizáveis do projeto People Analytics.

Centraliza os caminhos do projeto, o cálculo das taxas de rotatividade,
o teste estatístico e o padrão visual dos gráficos, evitando repetição
de código nos notebooks.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.ticker import PercentFormatter
from scipy.stats import chi2_contingency

# ---------------------------------------------------------------------------
# Caminhos do projeto
# ---------------------------------------------------------------------------
RAIZ = Path(__file__).resolve().parents[1]
PASTA_DADOS_BRUTOS = RAIZ / "data" / "raw"
PASTA_DADOS_PROCESSADOS = RAIZ / "data" / "processed"
PASTA_IMAGENS = RAIZ / "imagens"
PASTA_POWERBI = RAIZ / "powerBi"

# ---------------------------------------------------------------------------
# Padrão visual
# ---------------------------------------------------------------------------
COR_DESTAQUE = "#E45756"
COR_NEUTRA = "#2E86AB"
COR_REFERENCIA = "#173F5F"
ESCALA_RISCO_5 = ["#C44E52", "#DD8452", "#E5C07B", "#7AA974", "#55A868"]

NIVEL_SIGNIFICANCIA = 0.05

# Motivos de saída por iniciativa da empresa (desligamento involuntário)
MOTIVOS_INVOLUNTARIOS = [
    "Desempenho abaixo do esperado",
    "Reestruturação organizacional",
]


def formatar_percentual(valor, casas=1):
    """Formata um número como percentual no padrão brasileiro (vírgula decimal)."""
    return f"{valor:.{casas}%}".replace(".", ",")


def formatar_p_valor(p_valor):
    """Formata o p-valor para exibição (valores muito pequenos como '< 0,001')."""
    if p_valor < 0.001:
        return "p-valor < 0,001"
    return f"p-valor = {p_valor:.3f}".replace(".", ",")


# ---------------------------------------------------------------------------
# Cálculos
# ---------------------------------------------------------------------------
def calcular_taxa(dados, coluna, ordenar_por_taxa=False):
    """Calcula total de colaboradores, desligados e taxa de rotatividade por grupo."""
    tabela = (
        dados.groupby(coluna, observed=False)
        .agg(
            total_colaboradores=("colaborador_id", "nunique"),
            total_desligados=("rotatividade_flag", "sum"),
        )
        .reset_index()
    )
    tabela["taxa_rotatividade"] = (
        tabela["total_desligados"] / tabela["total_colaboradores"]
    )

    if ordenar_por_taxa:
        tabela = tabela.sort_values("taxa_rotatividade", ascending=False)

    return tabela.reset_index(drop=True)


def testar_associacao(dados, coluna, nome_exibicao, resultados=None):
    """Teste qui-quadrado de independência entre a variável e a rotatividade.

    Exibe o resultado, adiciona-o à lista `resultados` (se informada)
    e retorna um dicionário com qui², graus de liberdade, p-valor e V de Cramér.
    """
    tabela = pd.crosstab(dados[coluna], dados["rotatividade"])
    qui2, p_valor, graus_liberdade, _ = chi2_contingency(tabela)

    n = tabela.to_numpy().sum()
    v_cramer = np.sqrt(qui2 / (n * (min(tabela.shape) - 1)))
    significativo = p_valor < NIVEL_SIGNIFICANCIA

    resultado = {
        "variavel": nome_exibicao,
        "qui_quadrado": round(qui2, 2),
        "graus_liberdade": graus_liberdade,
        "p_valor": round(p_valor, 4),
        "v_cramer": round(v_cramer, 3),
        "significativo_5pct": "Sim" if significativo else "Não",
    }
    if resultados is not None:
        resultados.append(resultado)

    conclusao = (
        "associação estatisticamente significativa"
        if significativo
        else "diferença NÃO significativa (pode ser variação aleatória)"
    )
    print(
        f"{nome_exibicao}: qui² = {qui2:.2f} | gl = {graus_liberdade} | "
        f"p-valor = {p_valor:.4f} | V de Cramér = {v_cramer:.3f}"
    )
    print(f"Resultado a 5%: {conclusao}")

    return resultado


def headcount_em(dados, data):
    """Quantidade de colaboradores ativos em uma data."""
    return int(
        (
            (dados["data_admissao"] <= data)
            & (
                dados["data_desligamento"].isna()
                | (dados["data_desligamento"] > data)
            )
        ).sum()
    )


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------
def _finalizar_grafico(fig, caminho):
    fig.tight_layout()
    if caminho is not None:
        caminho = Path(caminho)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(caminho, dpi=300, bbox_inches="tight")
    plt.show()
    if caminho is not None:
        print(f"Gráfico salvo em: {caminho.relative_to(RAIZ)}")


def _titulo(ax, titulo, subtitulo):
    """Título com a mensagem principal e subtítulo descritivo."""
    if subtitulo:
        ax.set_title(
            subtitulo, fontsize=11, color="#555555", loc="left", pad=10
        )
        ax.figure.suptitle(
            titulo, fontsize=15, fontweight="bold", x=0.01, ha="left"
        )
    else:
        ax.set_title(titulo, fontsize=15, fontweight="bold")


def grafico_taxa(
    tabela,
    coluna,
    titulo,
    rotulo_eixo,
    taxa_geral,
    caminho=None,
    cores=None,
    horizontal=False,
    subtitulo=None,
):
    """Gráfico de barras da taxa de rotatividade por grupo.

    Inclui rótulos percentuais, linha de referência com a taxa geral
    e salva a imagem em alta resolução.
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    eixo_categoria, eixo_valor = ("y", "x") if horizontal else ("x", "y")
    parametros = {
        eixo_categoria: coluna,
        eixo_valor: "taxa_rotatividade",
    }
    if cores is None:
        parametros["color"] = COR_DESTAQUE
    else:
        parametros.update(hue=coluna, palette=cores, legend=False)

    sns.barplot(data=tabela, ax=ax, **parametros)

    # Rótulos de valor em cada barra
    for barra in ax.patches:
        if horizontal:
            valor = barra.get_width()
            posicao = (valor, barra.get_y() + barra.get_height() / 2)
            deslocamento, alinhamento = (6, 0), {"ha": "left", "va": "center"}
        else:
            valor = barra.get_height()
            posicao = (barra.get_x() + barra.get_width() / 2, valor)
            deslocamento, alinhamento = (0, 6), {"ha": "center", "va": "bottom"}

        ax.annotate(
            formatar_percentual(valor),
            xy=posicao,
            xytext=deslocamento,
            textcoords="offset points",
            fontsize=10,
            fontweight="bold",
            bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.85},
            **alinhamento,
        )

    # Linha de referência com a taxa geral
    linha = ax.axvline if horizontal else ax.axhline
    linha(
        taxa_geral,
        color=COR_REFERENCIA,
        linestyle="--",
        linewidth=2,
        label=f"Taxa geral: {formatar_percentual(taxa_geral)}",
    )

    # Eixos, limites e legenda
    limite = tabela["taxa_rotatividade"].max() * 1.25
    formatador = PercentFormatter(1)
    if horizontal:
        ax.set_xlim(0, limite)
        ax.xaxis.set_major_formatter(formatador)
        ax.set_xlabel("Taxa de rotatividade", fontweight="bold")
        ax.set_ylabel(rotulo_eixo, fontweight="bold")
        ax.grid(axis="x", alpha=0.3)
    else:
        ax.set_ylim(0, limite)
        ax.yaxis.set_major_formatter(formatador)
        ax.set_xlabel(rotulo_eixo, fontweight="bold")
        ax.set_ylabel("Taxa de rotatividade", fontweight="bold")
        ax.grid(axis="y", alpha=0.3)

    _titulo(ax, titulo, subtitulo)
    # Legenda acima da área do gráfico, para não sobrepor as barras
    ax.legend(loc="lower right", bbox_to_anchor=(1, 1.0), frameon=False)
    _finalizar_grafico(fig, caminho)
