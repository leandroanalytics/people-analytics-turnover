# Guia do Dashboard — People Analytics

Documentação técnica do arquivo [`People Analytics Dashboard.pbix`](People%20Analytics%20Dashboard.pbix): fontes de dados, tratamentos no Power Query, modelo de dados, medidas DAX e conteúdo de cada página.

## 1. Fontes de dados

Os dados vêm dos arquivos gerados pelos notebooks, na pasta `data/processed/`:

| Tabela no Power BI | Origem | Granularidade |
| --- | --- | --- |
| `fColaboradores` | `People_Analytics_Base_Analitica.csv` | 1 linha por colaborador (1.200) |
| `fMensal` | `People_Analytics_Rotatividade_Mensal.csv` | 1 linha por mês (jan/2022 a set/2026) |
| `dCalendario` | Tabela calculada em DAX | 1 linha por dia |
| `fModelo` | Tabela calculada em DAX (resultados do notebook 03) | 1 linha por fator do modelo |
| `Medidas` | Tabela vazia, usada só para organizar as medidas | — |

### Como abrir o arquivo em outro computador

O `.pbix` guarda o caminho dos CSVs no computador onde foi criado. O dashboard abre normalmente, mas para usar o botão **Atualizar** é preciso apontar para a pasta do projeto:

1. **Página Inicial → Transformar dados → Configurações da fonte de dados**;
2. Selecione cada CSV → **Alterar Fonte** → escolha o arquivo em `data/processed/`;
3. **Fechar e Aplicar**.

## 2. Tratamentos no Power Query

Os CSVs usam **ponto** como separador decimal. No Power BI configurado em português, isso faz o valor `749.0` ser lido como `7490`. Para evitar isso, a etapa **Tipo Alterado** de cada consulta termina com a localidade `"en-US"`:

```m
= Table.TransformColumnTypes(#"Cabeçalhos Promovidos", { ... }, "en-US")
```

- Em `fMensal`, as colunas `headcount_medio` e `turnover_mensal` são do tipo `type number` (decimal), não `Int64.Type`.
- Em `fColaboradores`, a coluna `salario_mensal` é `type number`.

> Uma etapa de localidade adicionada **depois** da conversão de tipo não corrige o problema: o valor já foi lido errado. A localidade precisa estar na própria etapa de conversão.

A opção **Data/hora automática** está desativada (**Arquivo → Opções → Arquivo atual → Carregamento de dados**). Quem controla as datas é a tabela `dCalendario`.

## 3. Modelo de dados

```text
dCalendario[Date]  1 ──── *  fMensal[mes]        (filtro único)

fColaboradores        (sem relacionamento: usada nos recortes por perfil)
fModelo               (sem relacionamento: resultados do modelo estatístico)
```

### Tabela calendário

```DAX
dCalendario =
ADDCOLUMNS (
    CALENDAR ( DATE ( 2022, 1, 1 ), DATE ( 2026, 9, 30 ) ),
    "Ano", YEAR ( [Date] ),
    "Mês", FORMAT ( [Date], "mmm/yy" ),
    "AnoMes", YEAR ( [Date] ) * 100 + MONTH ( [Date] )
)
```

- Marcada como **tabela de data** (coluna `Date`).
- A coluna **Mês** é classificada por **AnoMes**, para os meses aparecerem em ordem cronológica e não alfabética.

### Coluna de ordenação das faixas de tempo de empresa

Em `fColaboradores`, para as faixas aparecerem na ordem correta:

```DAX
Ordem Tempo =
SWITCH (
    TRUE (),
    fColaboradores[tempo_empresa_anos] <= 1, 1,
    fColaboradores[tempo_empresa_anos] <= 3, 2,
    fColaboradores[tempo_empresa_anos] <= 6, 3,
    fColaboradores[tempo_empresa_anos] <= 10, 4,
    5
)
```

A coluna `faixa_tempo_empresa` é classificada por `Ordem Tempo`.

> A versão `SWITCH ( fColaboradores[faixa_tempo_empresa], "Até 1 ano", 1, ... )` gera **dependência circular** ao classificar `faixa_tempo_empresa` por ela. Por isso a ordem é calculada a partir de `tempo_empresa_anos`.

## 4. Medidas DAX

### Série temporal (`fMensal`)

```DAX
Data Referência = DATE ( 2026, 9, 9 )

Desligamentos = SUM ( fMensal[desligamentos] )

Desligamentos Voluntários = SUM ( fMensal[desligamentos_voluntarios] )

Admissões = SUM ( fMensal[admissoes] )

Headcount Médio = AVERAGE ( fMensal[headcount_medio] )

Dias Observados =
VAR Inicio = MIN ( fMensal[mes] )
VAR Fim = MIN ( EOMONTH ( MAX ( fMensal[mes] ), 0 ), [Data Referência] )
RETURN DATEDIFF ( Inicio, Fim, DAY ) + 1

Turnover Anualizado =
DIVIDE ( [Desligamentos], [Headcount Médio] ) * DIVIDE ( 365, [Dias Observados] )

Turnover Voluntário Anualizado =
DIVIDE ( [Desligamentos Voluntários], [Headcount Médio] ) * DIVIDE ( 365, [Dias Observados] )

Turnover 12 Meses =
CALCULATE (
    DIVIDE ( [Desligamentos], [Headcount Médio] ),
    DATESINPERIOD ( dCalendario[Date], MAX ( fMensal[mes] ), -12, MONTH )
)

Turnover Voluntário 2026 =
CALCULATE ( [Turnover Voluntário Anualizado], dCalendario[Ano] = 2026 )

Headcount Atual =
VAR UltimoMes = CALCULATE ( MAX ( fMensal[mes] ), ALL ( fMensal ) )
RETURN
    CALCULATE (
        SUM ( fMensal[headcount_fim] ),
        fMensal[mes] = UltimoMes,
        ALL ( dCalendario )
    )
```

**Por que anualizar:** os dados de 2026 vão só até setembro. Sem a anualização, o turnover de 2026 apareceria como 9,7% (nove meses) e não seria comparável aos anos completos. Com `Dias Observados`, o valor de cada ano é ajustado para 365 dias; nos anos completos o fator é 1.

### Recortes por perfil (`fColaboradores`)

```DAX
Colaboradores = DISTINCTCOUNT ( fColaboradores[colaborador_id] )

Desligados =
CALCULATE (
    DISTINCTCOUNT ( fColaboradores[colaborador_id] ),
    fColaboradores[rotatividade] = "Sim"
)

% Voluntário =
DIVIDE (
    CALCULATE ( [Desligados], fColaboradores[tipo_desligamento] = "Voluntário" ),
    [Desligados]
)

Taxa de Rotatividade = DIVIDE ( [Desligados], [Colaboradores] )

Taxa Geral =
CALCULATE ( [Taxa de Rotatividade], REMOVEFILTERS ( fColaboradores ) )

Cor Barra =
IF ( [Taxa de Rotatividade] > [Taxa Geral], "#E45756", "#9AA5B1" )
```

`Taxa Geral` ignora os filtros de `fColaboradores` e sempre retorna a taxa da base inteira (26,9%). `Cor Barra` compara cada grupo com ela e devolve a cor usada na formatação condicional.

### Resultados do modelo (`fModelo`)

Resultados da regressão logística do notebook `03_modelo_rotatividade.ipynb` (efeito = odds ratio − 1):

```DAX
fModelo =
DATATABLE (
    "Fator", STRING, "Efeito", DOUBLE, "p_valor", DOUBLE, "Significativo", STRING,
    {
        { "Tempo de empresa (+1 ano)", -0.137, 0.000, "Sim" },
        { "Satisfação no trabalho (+1 nível)", -0.148, 0.004, "Sim" },
        { "Equilíbrio vida-trabalho (+1 nível)", -0.132, 0.009, "Sim" },
        { "Distância de casa (+1 km)", 0.009, 0.085, "Não" },
        { "Realiza horas extras", 0.308, 0.090, "Não" },
        { "Idade (+1 ano)", 0.021, 0.128, "Não" },
        { "Salário (+R$ 1.000)", -0.186, 0.186, "Não" },
        { "Nível do cargo (+1 nível)", 0.244, 0.454, "Não" },
        { "Satisfação com o ambiente (+1 nível)", -0.019, 0.724, "Não" },
        { "Avaliação de desempenho (+1 nível)", -0.018, 0.833, "Não" },
        { "Promovido nos últimos 5 anos", 0.014, 0.943, "Não" }
    }
)

Efeito na Chance = SUM ( fModelo[Efeito] )

Cor Modelo =
IF ( SELECTEDVALUE ( fModelo[Significativo] ) = "Sim", "#E45756", "#C3CAD2" )
```

A coluna `Fator` é classificada por `p_valor`, para os fatores significativos aparecerem no topo do gráfico.

> Se o modelo for reajustado no notebook, os valores desta tabela precisam ser atualizados manualmente a partir de `data/processed/People_Analytics_Modelo_Odds_Ratio.csv`.

### Valores de referência para conferência

| Medida | Valor esperado |
| --- | ---: |
| Headcount Atual | 877 |
| Turnover 12 Meses | 13,0% |
| Turnover Voluntário 2026 | 10,7% |
| % Voluntário | 73,4% |
| Taxa Geral | 26,9% |
| Turnover Anualizado 2022 → 2026 | 5,2% · 5,8% · 6,9% · 9,5% · 14,1% |
| Turnover Voluntário Anualizado 2022 → 2026 | 3,4% · 4,2% · 5,3% · 6,9% · 10,7% |

O turnover de 2026 aparece como 14,1% no dashboard e 14,0% no notebook. A diferença vem do headcount médio: o Power BI faz a média dos meses, e o notebook usa a média entre o início e o fim do ano.

## 5. Páginas

Todas as páginas têm o mesmo cabeçalho (título e **navegador de páginas**) e usam a paleta:

| Uso | Cor |
| --- | --- |
| Risco, turnover total, desligamentos, fatores significativos | `#E45756` |
| Turnover voluntário, admissões, motivos voluntários | `#2E86AB` |
| Abaixo da média, motivos involuntários, sem significância | `#9AA5B1` / `#C3CAD2` |
| Cabeçalho e linhas de referência | `#0B1F3A` / `#173F5F` |

### 1 — Visão Geral: *como está o turnover?*

| Visual | Campos |
| --- | --- |
| 4 cartões | `Headcount Atual` · `Turnover 12 Meses` · `Turnover Voluntário 2026` · `% Voluntário` |
| Linhas — *"O turnover anual mais que dobrou desde 2022"* | Eixo X: `dCalendario[Ano]` (categórico) · Eixo Y: `Turnover Anualizado`, `Turnover Voluntário Anualizado` |
| Colunas — *"Contratações despencaram em 2026"* | Eixo X: `dCalendario[Ano]` · Eixo Y: `Admissões`, `Desligamentos` |
| Barras empilhadas — *"Por que as pessoas saem?"* | Eixo Y: `motivo_desligamento` · Eixo X: `Desligados` · Legenda: `tipo_desligamento` · Filtro: exclui "Não se aplica" · Ordenação: `Desligados` decrescente |

### 2 — Quem Sai: *onde está o risco?*

| Visual | Campos |
| --- | --- |
| 5 segmentações (suspensas) | `area` · `nivel_cargo` · `horas_extras` · `faixa_salarial` · `tipo_desligamento` |
| Colunas — *"Quase metade sai no primeiro ano"* | Eixo X: `faixa_tempo_empresa` · Eixo Y: `Taxa de Rotatividade` |
| Colunas — *"Satisfação baixa concentra mais saídas"* | Eixo X: `satisfacao_trabalho` · Eixo Y: `Taxa de Rotatividade` |
| Colunas — *"Equilíbrio vida-trabalho baixo eleva a rotatividade"* | Eixo X: `equilibrio_vida_trabalho` (Não resumir) · Eixo Y: `Taxa de Rotatividade` |
| Tabela por área | `area` · `Colaboradores` · `Desligados` · `Taxa de Rotatividade` |

Nos três gráficos de colunas, a cor vem de **Colunas → Cor → fx → Valor do campo → `Cor Barra`**. Os grupos acima da taxa geral ficam vermelhos e os demais, cinza. As cores se recalculam quando os filtros mudam.

### 3 — O que explica: *o que realmente importa?*

| Visual | Campos |
| --- | --- |
| Barras — *"Tempo de casa, satisfação e equilíbrio explicam a saída"* | Eixo Y: `fModelo[Fator]` · Eixo X: `Efeito na Chance` · Cor: **fx → Valor do campo → `Cor Modelo`** · Ordenação: `Fator` crescente (segue o `p_valor`) |
| Caixas de texto | Legenda *"← reduz a chance de saída / aumenta a chance de saída →"*, as 3 conclusões do modelo, o card da AUC (0,68) e a nota com a base do modelo |

### 4 — Como ler

Página de apoio para quem não é da área de dados:

- **Sobre os dados:** tamanho da base, período e anualização de 2026;
- **Indicadores:** definição de turnover anual, taxa acumulada e significado das cores;
- **O que é "significativo":** explicação do p-valor em linguagem simples;
- **Sobre o modelo:** o que significa a AUC de 0,68, qual foi a base do modelo e como foi validado;
- **Uso responsável:** associação não é causa, e os resultados não devem ser usados para decisões individuais.

## 6. Limitações conhecidas

- Os valores da `fModelo` são fixos (copiados do notebook) e não se atualizam com os dados.
- Agosto e setembro de 2026 têm poucos registros. Por isso os gráficos usam visão anual em vez de mensal.
- A base é sintética. Os resultados ilustram o método, não uma empresa real.
