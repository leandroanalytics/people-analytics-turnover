# Guia do Dashboard — People Analytics

Roteiro para montar o dashboard no Power BI a partir dos arquivos gerados pelos notebooks.

## 1. Arquivos de origem

Todos estão em `data/processed/`:

| Arquivo | Conteúdo | Uso no dashboard |
| --- | --- | --- |
| `People_Analytics_Base_Analitica.csv` | 1 linha por colaborador, com faixas, fatores e tipo de desligamento | Tabela fato `fColaboradores` |
| `People_Analytics_Rotatividade_Mensal.csv` | Headcount, admissões e desligamentos por mês | Tabela fato `fMensal` |
| `People_Analytics_Rotatividade_Anual.csv` | Turnover anual (total e voluntário) | Conferência dos valores |
| `People_Analytics_Modelo_Odds_Ratio.csv` | Resultado da regressão logística | Tabela `fModelo` |

> **Atenção ao importar:** os CSVs usam ponto como separador decimal. No Power Query, em *Transformar → Tipo de dados → Usando localidade*, escolha **Inglês (Estados Unidos)** para as colunas numéricas. Sem isso, `0.0149` pode virar `149`.

## 2. Modelo de dados

- Crie a tabela calendário `dCalendario`:

```DAX
dCalendario =
ADDCOLUMNS (
    CALENDAR ( DATE ( 2022, 1, 1 ), DATE ( 2026, 12, 31 ) ),
    "Ano", YEAR ( [Date] ),
    "Mês", FORMAT ( [Date], "mmm/yy" ),
    "AnoMes", YEAR ( [Date] ) * 100 + MONTH ( [Date] )
)
```

- Marque como tabela de datas e relacione `dCalendario[Date]` → `fMensal[mes]` (1:N).
- `fColaboradores` e `fModelo` ficam sem relacionamento com o calendário.

## 3. Medidas DAX

### Base de colaboradores (`fColaboradores`)

```DAX
Colaboradores = DISTINCTCOUNT ( fColaboradores[colaborador_id] )

Desligados =
CALCULATE ( [Colaboradores], fColaboradores[rotatividade] = "Sim" )

Ativos =
CALCULATE ( [Colaboradores], fColaboradores[rotatividade] = "Não" )

Taxa de Rotatividade = DIVIDE ( [Desligados], [Colaboradores] )

Desligados Voluntários =
CALCULATE ( [Colaboradores], fColaboradores[tipo_desligamento] = "Voluntário" )

% Voluntário = DIVIDE ( [Desligados Voluntários], [Desligados] )

Taxa Geral (referência) =
CALCULATE ( [Taxa de Rotatividade], REMOVEFILTERS ( fColaboradores ) )

Diferença vs Geral (p.p.) = ( [Taxa de Rotatividade] - [Taxa Geral (referência)] ) * 100
```

### Série mensal (`fMensal`)

```DAX
Desligamentos Mês = SUM ( fMensal[desligamentos] )

Admissões Mês = SUM ( fMensal[admissoes] )

Headcount Médio = AVERAGE ( fMensal[headcount_medio] )

Turnover Período = DIVIDE ( [Desligamentos Mês], [Headcount Médio] )

Turnover Voluntário Período =
DIVIDE ( SUM ( fMensal[desligamentos_voluntarios] ), [Headcount Médio] )

Turnover 12 Meses =
CALCULATE (
    [Turnover Período],
    DATESINPERIOD ( dCalendario[Date], MAX ( fMensal[mes] ), -12, MONTH )
)

Headcount Atual =
VAR UltimoMes = MAX ( fMensal[mes] )
RETURN CALCULATE ( SUM ( fMensal[headcount_fim] ), fMensal[mes] = UltimoMes )
```

> `Turnover Período` filtrado por um ano completo reproduz o turnover anual do notebook (desligamentos ÷ headcount médio).

## 4. Páginas sugeridas

### Página 1 — Visão Executiva
- **Cartões:** Headcount Atual · Turnover 12 Meses · Turnover Voluntário Período · % Voluntário
- **Gráfico de linhas:** Turnover Período por Ano (total e voluntário), com o título *"O turnover anual mais que dobrou desde 2022"*
- **Colunas agrupadas:** Admissões Mês × Desligamentos Mês por mês
- **Barras horizontais:** Desligados por `motivo_desligamento`

### Página 2 — Quem Sai
- **Barras:** Taxa de Rotatividade por `faixa_tempo_empresa`, com a linha constante da Taxa Geral (*Analytics → Linha constante*)
- **Barras:** Taxa de Rotatividade por `satisfacao_trabalho` e por `equilibrio_vida_trabalho`
- **Matriz:** `area` × `tipo_desligamento` com Desligados
- **Segmentações:** área, nível do cargo, horas extras, faixa salarial

### Página 3 — O que Explica a Saída
- **Gráfico de barras** com `fModelo[efeito_na_chance]` por variável, colorido por `significativo_5pct` (formatação condicional)
- **Caixa de texto** com a leitura: tempo de casa, satisfação e equilíbrio são os únicos fatores significativos; o efeito da promoção desaparece quando se controla o tempo de empresa.
- **Nota de uso responsável:** resultados agregados, nunca para decisões individuais.

## 5. Padrão visual

| Elemento | Cor |
| --- | --- |
| Destaque / risco | `#E45756` |
| Neutro / voluntário | `#2E86AB` |
| Linha de referência | `#173F5F` |
| Sem significância | `#9AA5B1` |

Use **títulos que dizem a conclusão** (por exemplo, *"Quase metade sai no primeiro ano"*), e não apenas o nome da métrica.

## 6. Publicação no GitHub

Depois de montar o dashboard:

1. Salve o arquivo como `powerBi/People_Analytics_Dashboard.pbix`;
2. Exporte um print de cada página para `imagens/dashboard_pagina_1.png`, `dashboard_pagina_2.png` etc.;
3. Adicione os prints ao README, na seção **Dashboard**.
