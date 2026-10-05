# People Analytics — Análise de Rotatividade de Colaboradores

Projeto de análise de dados desenvolvido para investigar os principais fatores associados à rotatividade de colaboradores e transformar os resultados em recomendações para retenção, desenvolvimento e gestão de pessoas.

A solução contempla preparação dos dados, análise exploratória com Python, visualizações, indicadores executivos e geração de arquivos para utilização no Power BI.

## Problema de Negócio

A rotatividade pode gerar custos com recrutamento, seleção, treinamento e perda de conhecimento. Para apoiar decisões de People Analytics, este projeto busca responder:

* Qual é a taxa geral de rotatividade?
* Quais áreas apresentam maior proporção de desligamentos?
* Horas extras estão associadas à maior rotatividade?
* Como satisfação e equilíbrio entre vida e trabalho se relacionam com os desligamentos?
* Em qual período da jornada do colaborador ocorre maior risco de saída?
* Remuneração e promoção estão associadas à permanência?
* O acúmulo de fatores aumenta a taxa de rotatividade?

## Base de Dados

A base sintética foi criada exclusivamente para fins educacionais e de portfólio.

### Estrutura inicial

* 1.212 registros brutos
* 23 variáveis
* 12 registros duplicados
* 43 valores ausentes intencionais

### Estrutura após o tratamento

* 1.200 registros únicos
* Nenhuma duplicidade
* Valores ausentes tratados
* Tempo de empresa recalculado a partir das datas de admissão e desligamento
* Tipos de dados padronizados
* Regras de qualidade validadas

A base não contém dados pessoais reais.

## Tecnologias Utilizadas

* Python
* Pandas
* NumPy
* Matplotlib
* Seaborn
* SciPy (testes estatísticos)
* OpenPyXL
* Jupyter Notebook
* Power BI
* Git e GitHub

## Estrutura do Projeto

```text
python-eda
├── data
│   ├── People_Analytics_Analise_de_Rotatividade_de_Colaboradores.xlsx
│   ├── People_Analytics_Base_Tratada.csv
│   ├── People_Analytics_Base_Tratada.xlsx
│   ├── People_Analytics_Base_Analitica.csv
│   └── People_Analytics_Resumo_KPIs.csv
├── imagens
│   ├── distribuicao_rotatividade.png
│   ├── motivos_desligamento.png
│   ├── rotatividade_por_area.png
│   ├── rotatividade_por_horas_extras.png
│   ├── rotatividade_por_satisfacao_trabalho.png
│   ├── rotatividade_por_tempo_empresa.png
│   ├── rotatividade_por_faixa_salarial.png
│   ├── rotatividade_por_promocao.png
│   ├── rotatividade_por_equilibrio_vida_trabalho.png
│   └── rotatividade_por_acumulo_de_fatores.png
├── notebooks
│   ├── 01_etl.ipynb
│   └── 02_eda.ipynb
├── powerBi
│   └── People_Analytics_Resumo_Executivo.xlsx
├── .gitignore
├── README.md
└── requirements.txt
```

## Metodologia

### 1. Preparação e tratamento

* Importação da base em Excel
* Diagnóstico da estrutura
* Identificação de duplicidades
* Identificação de valores ausentes
* Preservação da base bruta
* Remoção de 12 duplicidades
* Tratamento de 43 valores ausentes
* Padronização dos tipos de dados
* Recálculo do tempo de empresa (o campo original contava o tempo dos desligados até a data atual, e não até a saída)
* Validação de regras de qualidade
* Exportação da base tratada

### 2. Análise exploratória

* Cálculo dos KPIs gerais
* Rotatividade por área
* Relação com horas extras
* Satisfação no trabalho
* Tempo de empresa
* Faixa salarial
* Histórico de promoção
* Equilíbrio entre vida e trabalho
* Motivos de desligamento
* Acúmulo de fatores associados
* Teste qui-quadrado de independência e V de Cramér em cada recorte

## Principais Indicadores

| Indicador                  |   Resultado |
| -------------------------- | ----------: |
| Total de colaboradores     |       1.200 |
| Colaboradores ativos       |         877 |
| Colaboradores desligados   |         323 |
| Taxa acumulada de rotatividade |  26,92% |
| Idade média                |   41,1 anos |
| Tempo médio de empresa     |    5,9 anos |
| Salário médio              | R$ 9.086,42 |

> A taxa de rotatividade corresponde a desligados ÷ total de registros. Como os desligamentos estão distribuídos entre 2022 e 2026, trata-se de uma taxa **acumulada do período**, e não de um turnover anual.

## Principais Resultados

Cada recorte foi avaliado com o **teste qui-quadrado de independência** (nível de significância de 5%), para separar diferenças reais de variações que podem ocorrer por acaso.

| Fator | Resultado | p-valor | Significativo? |
| --- | --- | ---: | :---: |
| Tempo de empresa | 46,9% no 1º ano vs. 13,6% acima de 10 anos | < 0,001 | Sim |
| Acúmulo de fatores | 10,8% sem fatores vs. 39,6% com 3 ou mais | < 0,001 | Sim* |
| Satisfação no trabalho | 32,9%–34,2% nos níveis 1–2 vs. 21,6% no nível 5 | 0,002 | Sim |
| Equilíbrio vida-trabalho | 33,5% no nível 1 vs. 21,6% no nível 4 | 0,031 | Sim |
| Promoção nos últimos 5 anos | 28,5% sem promoção vs. 22,1% com promoção | 0,035 | Sim |
| Horas extras | 29,2% com vs. 25,6% sem | 0,20 | Não |
| Área | 33,5% em Atendimento vs. 20,9% em Tecnologia | 0,27 | Não |
| Faixa salarial | 30,0% no 1º quartil vs. 23,7% no 4º quartil | 0,38 | Não |

\* Resultado parcialmente circular: os fatores foram escolhidos a partir desta mesma base (ver abaixo).

### Tempo de empresa

O primeiro ano é o período mais crítico: quase metade dos colaboradores com até 1 ano de casa foi desligada. O risco cai de forma consistente com o tempo de empresa. É o fator com a associação mais forte da análise.

![Taxa de rotatividade por tempo de empresa](imagens/rotatividade_por_tempo_empresa.png)

### Satisfação no trabalho

Os níveis 1 e 2 de satisfação apresentam taxas acima de 32%. A partir do nível 3, a taxa cai para menos de 24%.

![Taxa de rotatividade por satisfação](imagens/rotatividade_por_satisfacao_trabalho.png)

### Equilíbrio entre vida e trabalho

O nível mais baixo de equilíbrio apresentou taxa de 33,5%. Nos níveis 3 a 5, os indicadores ficaram abaixo da taxa geral.

![Taxa de rotatividade por equilíbrio entre vida e trabalho](imagens/rotatividade_por_equilibrio_vida_trabalho.png)

### Promoção

Colaboradores sem promoção nos últimos cinco anos apresentaram taxa de 28,5%, contra 22,1% entre os promovidos. A associação é fraca e pode ser influenciada pelo tempo de empresa (quem tem pouco tempo de casa teve menos oportunidade de ser promovido).

![Taxa de rotatividade por histórico de promoção](imagens/rotatividade_por_promocao.png)

### Motivos de desligamento

Os motivos estão distribuídos de forma equilibrada. Cerca de 27% das saídas foram de iniciativa da empresa (desempenho abaixo do esperado e reestruturação) e 73% de iniciativa do colaborador.

![Motivos de desligamento](imagens/motivos_desligamento.png)

### Área, horas extras e faixa salarial

Esses recortes mostram diferenças visuais (por exemplo, Atendimento com 33,5% e Tecnologia com 20,9%), mas **nenhuma delas é estatisticamente significativa**. Com cerca de 170 colaboradores por área, diferenças dessa magnitude podem ocorrer por acaso, por isso não devem orientar decisões isoladamente.

<details>
<summary>Ver gráficos</summary>

![Taxa de rotatividade por área](imagens/rotatividade_por_area.png)

![Taxa de rotatividade por horas extras](imagens/rotatividade_por_horas_extras.png)

![Taxa de rotatividade por faixa salarial](imagens/rotatividade_por_faixa_salarial.png)

</details>

### Acúmulo de fatores

A taxa aumenta conforme os fatores se acumulam: 10,8% (nenhum), 20,8% (1), 29,2% (2) e 39,6% (3 ou mais).

Esse resultado é **parcialmente circular**: os cinco fatores foram escolhidos porque já apresentavam taxas maiores nesta mesma base. Ele ilustra o efeito combinado, mas não é uma validação independente.

![Rotatividade por acúmulo de fatores](imagens/rotatividade_por_acumulo_de_fatores.png)

## Decisões Orientadas pelos Dados

| Evidência | Força | Decisão recomendada |
| --- | --- | --- |
| 46,9% de rotatividade no primeiro ano | Forte | Reestruturar onboarding e acompanhamento inicial |
| Satisfação baixa associada a desligamentos | Moderada | Desenvolver ações de clima e liderança |
| Equilíbrio baixo associado a desligamentos | Fraca | Ampliar iniciativas de flexibilidade e bem-estar |
| Não promovidos apresentam maior rotatividade | Fraca | Estruturar carreira e mobilidade interna |
| 73% das saídas são voluntárias | Descritiva | Monitorar a rotatividade voluntária separadamente |
| Área, salário e horas extras | Não significativa | Não priorizar; monitorar a série histórica |

## Recomendações

1. Reestruturar o onboarding com metas de 30, 60 e 90 dias.
2. Realizar conversas de permanência aos 3, 6 e 12 meses.
3. Desenvolver planos de ação para satisfação e clima.
4. Criar critérios transparentes de promoção e ampliar a mobilidade interna.
5. Separar rotatividade voluntária e involuntária nos indicadores.
6. Coletar dados mais detalhados: quantidade de horas extras e salário comparado ao mercado.
7. Construir um dashboard mensal de People Analytics.
8. Comparar os indicadores antes e depois das iniciativas.

## Limitações e Uso Responsável

A base utilizada é sintética e os resultados representam associações presentes nos dados, não relações comprovadas de causa e efeito.

Os testes qui-quadrado avaliam cada fator isoladamente e não controlam a influência de uma variável sobre outra (por exemplo, tempo de empresa sobre promoção). Um próximo passo natural seria um modelo multivariado, como uma regressão logística, validado em dados separados.

O indicador de fatores acumulados possui caráter exploratório. Ele deve ser utilizado para análises agregadas e planejamento organizacional, nunca para classificar, punir ou tomar decisões individuais sobre colaboradores.


## Como Executar o Projeto

Clone o repositório:

```bash
# Clona o repositório
git clone https://github.com/leandroanalytics/python-eda.git

# Acessa a pasta do projeto
cd python-eda
```

Crie o ambiente virtual:

```bash
# Cria o ambiente virtual
python -m venv .venv
```

Ative o ambiente no Windows:

```powershell
# Ativa o ambiente virtual no Windows
.venv\Scripts\activate
```

No Linux ou macOS:

```bash
# Ativa o ambiente virtual no Linux ou macOS
source .venv/bin/activate
```

Instale as dependências:

```bash
# Instala as bibliotecas necessárias
pip install -r requirements.txt
```

Execute os notebooks na seguinte ordem:

1. `notebooks/01_etl.ipynb`
2. `notebooks/02_eda.ipynb`

## Autor

Leandro Gomes
Profissional em transição para Dados e Business Intelligence, com experiência em gestão de negócios, indicadores, rentabilidade e apoio à tomada de decisão.

[GitHub — leandroanalytics](https://github.com/leandroanalytics)
