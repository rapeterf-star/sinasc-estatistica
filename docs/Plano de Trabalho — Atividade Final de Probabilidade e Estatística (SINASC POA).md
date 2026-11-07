# Plano de Trabalho — Atividade Final de Probabilidade e Estatística (SINASC POA)

Nov 4, 2026 · @Renato

## 1. Visão geral e cronograma

O trabalho usa a base SINASC de Porto Alegre (197.801 nascimentos, 2011–2021) como população. Dela sai uma amostra aleatória simples de 384 nascimentos, que serve para estimar e testar 2 proporções e 2 médias. A entrega são 3 painéis em Python + Streamlit, publicados no Streamlit Community Cloud, um vídeo de até 4 minutos no YouTube e um relatório acadêmico complementar em LaTeX/PDF. **Prazo: domingo, 15/11, 23:59.** O cronograma deixa 2 dias de folga.

**Etapa 1 — Dados e amostra (até sáb 07/11)**

- [x] Criar o projeto `sinasc-estatistica` no VS Code, com `data/`, `src/` e `app/`
- [x] Script `src/01_limpeza.py`: aplica as regras da seção 3 e salva `data/populacao.parquet`
- [x] Script `src/02_amostra.py`: calcula n, sorteia a AAS com semente fixa e salva `data/amostra.csv`
- [x] Registrar em `docs/decisoes.md` a fonte, o link, os filtros, a semente e o n

**Etapa 2 — Painéis 1 e 2 (até seg 09/11)**

- [x] Painel 1 (população) completo
- [x] Painel 2 (amostra) reaproveitando as mesmas funções, com a coluna de comparação
- [x] Revisar escolha dos gráficos, legibilidade dos rótulos e cores com base em Wilke (2019)
- [x] Investigar a interpretação de registros com peso abaixo de 500 g e definir a ressalva metodológica sem refazer as análises

**Etapa 3 — Painel 3, a inferência (até qua 11/11)**

- [x] Funções de IC e testes em `src/inferencia.py`, conferidas contra o `statsmodels`
- [x] As 4 hipóteses com IC, estatística, valor-p, decisão e comparação com a verdade populacional
- [x] Verificação das condições de aplicação de cada procedimento

**Etapa 4 — Publicação (qui 12/11)**

- [x] Preparar `data/resumo_publico.json` localmente com estatísticas agregadas, sem linhas individuais
- [x] Adaptar os três painéis para consumir somente os resumos agregados e retirar o download individual da amostra
- [x] Ignorar CSVs e Parquets com registros individuais no Git
- [x] Criar o repositório público no GitHub e publicar o código e o resumo agregado, sem microdados individuais
- [x] Publicar a aplicação no Streamlit Community Cloud
- [x] Abrir o app numa janela anônima e verificar os três painéis sem login

**Privacidade na publicação:** `data/sinasc_nascimentos.csv`, `data/populacao.parquet` e `data/amostra.csv` permanecem locais e são ignorados pelo Git. O deploy deve incluir apenas `data/resumo_publico.json`, que contém estatísticas e distribuições agrupadas; grupos com menos de 10 registros são reunidos ou omitidos.

**Ressalva sobre o corte de peso:** mantemos a população analítica e os resultados já calculados (N = 197.639; amostra n = 384), sem refazer as análises. O corte de 500 g é tratado como uma decisão operacional deste estudo, não como prova de que todo registro abaixo desse valor seja erro ou biologicamente impossível. A literatura e as orientações citadas indicam que um nascimento pode ser registrado como nascido vivo quando há sinais de vida, independentemente do peso; portanto, parte dos registros abaixo de 500 g pode ser legítima. O relatório deve dizer que as conclusões se aplicam ao recorte analisado após o corte e reconhecer que a exclusão pode deixar de fora nascidos vivos de peso extremamente baixo. Foram removidos 162 registros, dos quais 20 têm peso zero e 142 têm peso positivo.

**Etapa 5 — Vídeo (sex 13/11 a sáb 14/11)**

- [ ] Ensaiar o roteiro da seção 9 com cronômetro (meta: 3min50s, limite de 4 minutos)
- [ ] Gravar a tela com o OBS ou o Loom, editar e subir no YouTube como "Não listado"

**Etapa 6 — Entrega (dom 15/11, até 18h)**

- [ ] Publicar no Moodle um texto curto apresentando o objetivo, a base, o método e os principais resultados
- [ ] Preparar um relatório acadêmico complementar em LaTeX e compilar o PDF, seguindo como referência de estrutura/apresentação o trabalho AGI-ARC-1 da disciplina anterior
- [ ] Incluir no relatório a justificativa do recorte de peso ≥ 500 g, a ressalva de que registros abaixo desse valor podem corresponder a nascidos vivos, e a limitação decorrente; não substituir o texto curto exigido no Moodle
- [ ] Registrar no relatório e no texto do Moodle que o Q-Q plot do peso mostra afastamento da normalidade na cauda inferior; interpretar isso como característica/discrepância da distribuição que merece contextualização, não como motivo isolado para excluir ou ajustar registros
- [ ] Incluir no texto os links do app Streamlit (três painéis), do vídeo no YouTube como "Não listado" e da base original, com a identificação da fonte
- [ ] Conferir que o app e o vídeo abrem pelos links compartilhados e que o vídeo está como "Não listado"

## 2. Base de dados

A base é o SINASC (Sistema de Informações sobre Nascidos Vivos) de Porto Alegre, publicado no portal de dados abertos da Prefeitura ([SINASC – dadosabertos.poa.br](https://dadosabertos.poa.br/dataset/sinasc)). Quem mantém os dados é a Coordenação Geral de Vigilância Sanitária, e a atualização é semestral.

- **Contexto e objetivo:** cada nascimento vivo no município gera uma Declaração de Nascido Vivo, digitada no SINASC. A base apoia a vigilância epidemiológica e o planejamento da saúde materno-infantil.
- **Tamanho:** 197.801 registros e 22 variáveis, de jan/2011 a dez/2021 (entre 14.147 e 19.720 nascimentos por ano).
- **População analítica deste estudo:** registros de nascidos vivos em Porto Alegre no SINASC entre 2011 e 2021, após o recorte operacional de peso ≥ 500 g (N = 197.639).
- **Unidade amostral:** o nascimento, ou seja, uma linha da base (uma Declaração de Nascido Vivo).

**Variáveis selecionadas**

| Variável | Tipo | Uso no trabalho | Valor na população |
| --- | --- | --- | --- |
| `peso` (g) | Quantitativa contínua | Média (H3 e H4) | média 3.189 g, DP 574 g |
| `idade_mae` (anos, derivada) | Quantitativa contínua | Descritiva | média 28,8 anos |
| `parto` | Qualitativa nominal | Proporção de cesáreas (H1 e H2) | 50,7% cesáreo |
| `escolaridade_mae` | Qualitativa ordinal | Grupos da H2 | 31% com 12 anos ou mais |
| `nro_consultas_prenatal` | Qualitativa ordinal | Grupos da H4 | 75% com 7 ou mais |
| `duracao_gestacao` | Qualitativa ordinal (faixas) | Descritiva: prematuridade | 11,6% com menos de 37 semanas |
| `baixo_peso` (derivada) | Qualitativa binária | Descritiva | 9,5% abaixo de 2.500 g |
| `sexo` | Qualitativa nominal | Descritiva | 51,2% masculino |

O dicionário de dados em PDF permanece local e não será redistribuído no repositório público enquanto a licença não for confirmada. O Painel 1 cita a fonte pública do SINASC e seu portal de dados.

## 3. Preparação e limpeza dos dados

A limpeza remove 162 registros (0,08%) e cria 7 variáveis derivadas. Ela roda uma vez só, no script `src/01_limpeza.py`, e o resultado vira a "população" oficial do trabalho. Ler o CSV com `sep=';'`.

1. **Aplicar o recorte analítico de peso ≥ 500 g**, mantendo a definição já usada nos cálculos. Foram excluídos 162 registros, dos quais 20 têm peso zero e 142 têm peso positivo. A exclusão é uma decisão operacional do projeto; peso abaixo de 500 g não prova, por si só, erro de registro ou impossibilidade biológica. Nascidos vivos com peso extremamente baixo podem ser registrados quando há sinais de vida. Como não vamos refazer a análise, as conclusões devem ser explicitamente limitadas ao recorte de peso ≥ 500 g, e essa restrição deve aparecer no relatório e na apresentação.
2. **Derivar `idade_mae`** = (`data_nascimento` − `nascimento_mae`) em anos. As duas colunas estão no formato `mm/aaaa`; ler com `format='%m/%Y'` e tirar os espaços em branco antes. Cerca de 1,6% fica vazio porque a data da mãe não foi informada. Esses registros ficam na base e só saem das análises de idade.
3. **Derivar as variáveis binárias:**
   - `cesarea` = 1 se `parto` == 'CESAREO'. Os 18 registros IGNORADO ou vazios entram como 0 e isso vai anotado.
   - `baixo_peso` = 1 se `peso` < 2.500 g
   - `prematuro` = 1 se `duracao_gestacao` for menor que 37 semanas (as 4 faixas abaixo de "DE 37 A 41 SEM")
   - `escol_12mais` = 1 se `escolaridade_mae` == 'COM 12 ANOS OU MAIS'
   - `prenatal_7mais` = 1 se `nro_consultas_prenatal` == '7 OU MAIS CONS'
4. **Derivar `ano`** a partir de `data_nascimento`, para o filtro dos painéis. A série cobre 2011–2021; 2021 tem 14.130 registros na população analítica, portanto não deve ser confundido com o último ano coberto, 2020.
5. **Não usar** colunas muito incompletas ou fora do escopo: `raca` (98,5% vazia), `classe_robson` (88,8%), `cesaria_antes_parto` (50,3%), `cid_anomalia`, `cbo_mae` e `ocupacao`.
6. **Salvar** em `data/populacao.parquet` e registrar no Painel 1 o N antes e depois da limpeza.

## 4. Dimensionamento e seleção da amostra (AAS)

A amostra tem **n = 384 nascimentos**, sorteados por amostragem aleatória simples sem reposição com semente fixa. Esse é o resultado da calculadora da USP/Bauru com os parâmetros abaixo.

| Parâmetro | Valor | Justificativa |
| --- | --- | --- |
| Nível de confiança | 95% (Z = 1,96) | Padrão da área e dos slides; casa com α = 5% nos testes |
| Margem de erro (d) | 5 p.p. | Precisão suficiente para proporções da ordem de 10% a 50%, com custo de coleta razoável |
| Proporção (p) | 0,5 | Pior caso: maximiza p(1−p) e garante a margem para qualquer proporção estudada |
| Tamanho da população (N) | 197.639 | Base limpa (seção 3) |

Primeiro calcula-se o tamanho para população infinita (a "Regra do Zero-Um" dos slides) e depois aplica-se a correção para população finita:

```latex
n_0 = \frac{Z^2 \, p(1-p)}{d^2} = \frac{1{,}96^2 \cdot 0{,}5 \cdot 0{,}5}{0{,}05^2} = 384{,}16
```

```latex
n = \frac{n_0}{1 + \frac{n_0 - 1}{N}} = \frac{384{,}16}{1 + \frac{383{,}16}{197.639}} = 383{,}4 \;\Rightarrow\; n = 384
```

Como N é muito maior que n (fração amostral de 0,19%), a correção quase não muda o resultado. Vale dizer isso no vídeo.

**Procedimento da AAS**

1. Ordenar a população por um identificador estável, o índice da linha do CSV original, para o sorteio ser reprodutível.
2. Sortear com `amostra = pop.sample(n=384, replace=False, random_state=2026)`. Com isso, cada nascimento tem a mesma probabilidade de entrar na amostra: 384/197.639 ≈ 0,19%.
3. Salvar `data/amostra.csv` com o índice original de cada linha sorteada, para que qualquer um possa conferir.
4. Documentar no Painel 2: semente, comando, n e a data do sorteio.

**Regra de ouro:** a amostra é sorteada uma vez só. Sortear de novo até o resultado "ficar bom" invalida a inferência, e é o mesmo problema do p-hacking dos slides.

Para o teste da média, a amostra de 384 também serve: n > 30 garante, pelo TCL, a normalidade aproximada de x̄, e o IC t usa o S da própria amostra.

## 5. Painel 1 — Análise descritiva da população

O Painel 1 mostra os parâmetros verdadeiros (μ, σ, π) dos 197.639 nascimentos. Esses valores são o "gabarito" contra o qual a amostra será julgada no Painel 3. Use a notação dos slides em todos os rótulos: N, μ, σ, π para a população.

**Topo — contexto e filtros**

- Cabeçalho com a fonte, o link, o período e o N antes e depois da limpeza
- Filtro de ano na barra lateral (padrão: todos). Os parâmetros do gabarito usam sempre a base inteira, e o painel avisa isso quando o filtro estiver ativo

**Linha de indicadores (cartões, `st.metric`)**

- N = 197.639 · peso médio μ · σ do peso (ddof=0) · % cesárea π · % baixo peso · % prematuros · idade média da mãe

**Variáveis quantitativas (peso e idade da mãe)**

- Histograma com as linhas da média e da mediana
- Boxplot, que mostra os valores atípicos pela regra 1,5·IQR
- Tabela de medidas: média, mediana, moda, desvio-padrão, variância, CV, mínimo, Q1, Q3, máximo, amplitude, IQR e assimetria (o peso tem assimetria de −0,84, à esquerda)
- Gráfico Q-Q normal do peso, como nos labs ch3B

**Variáveis qualitativas**

- Barras de frequência e proporção para tipo de parto, escolaridade da mãe, consultas de pré-natal, duração da gestação e sexo. Use barras, não pizza, para facilitar a comparação
- Tabela de frequências absolutas e relativas (%) de cada variável

**Cruzamentos que preparam as hipóteses**

- % de cesárea por escolaridade da mãe (barras), o terreno da H2
- Boxplot do peso por faixa de consultas de pré-natal, o terreno da H4
- Linha da % de cesárea e do peso médio por ano, de 2011 a 2021. A cesárea cai de 53,4% para 49,4%, o que mostra que a população não é homogênea no tempo

Interpretação curta embaixo de cada bloco (1 ou 2 frases), porque o critério avalia a interpretação, e não só os gráficos.

## 6. Painel 2 — Análise descritiva da amostra

O Painel 2 repete o Painel 1 usando somente os 384 nascimentos da amostra e acrescenta a comparação lado a lado com a população. Use a notação amostral: n, x̄, S (ddof=1), P.

**Como construir sem retrabalho:** escreva os gráficos e tabelas do Painel 1 como funções que recebem um DataFrame (por exemplo, `secao_quantitativa(df, rotulos)`). O Painel 2 chama as mesmas funções com a amostra. Assim os dois painéis ficam idênticos na forma, que é exatamente o que o enunciado pede.

**Topo — o sorteio**

- Cartão com n = 384, a semente 2026, o comando do sorteio e a fração amostral de 0,19%
- Botão para baixar `amostra.csv`

**Mesmos blocos do Painel 1**, agora com a amostra: indicadores, histogramas, boxplots, Q-Q plot, barras e tabelas de frequência.

**Bloco de comparação com a população**

- Tabela com uma linha por medida: valor na população · valor na amostra · diferença absoluta · diferença relativa (%)
- Histograma do peso com população e amostra sobrepostas, em densidade, porque as escalas são muito diferentes
- Barras agrupadas das proporções (população × amostra) para cada variável qualitativa

**Interpretação que o painel deve trazer**

- As medidas de centro (média, mediana, %) devem ficar próximas às da população
- As caudas e os extremos variam mais: com 384 casos, eventos raros como peso abaixo de 1.000 g ou gestação com menos de 22 semanas podem nem aparecer
- Diferenças são esperadas e não indicam erro: são a variabilidade amostral, que o Painel 3 quantifica com os ICs

## 7. Painel 3 — Inferência estatística e comparação

O Painel 3 testa 4 hipóteses só com a amostra e depois confere cada conclusão contra a verdade populacional. A combinação foi escolhida para gerar dois resultados "sem evidência" e dois "com evidência forte", o que dá material para discutir poder do teste e significância prática. **α = 5% em todos os testes, fixado antes de olhar a amostra**, como manda o pipeline dos slides.

### As 4 hipóteses

| # | Pergunta | H₀ | H₁ | Procedimento | Verdade na população |
| --- | --- | --- | --- | --- | --- |
| H1 | A cesárea já é maioria dos partos em POA? | π = 0,50 | π > 0,50 (unilateral) | IC de Wald e teste Z de 1 proporção | π = 0,507 |
| H2 | A taxa de cesárea difere conforme a escolaridade da mãe? | π₁ = π₂ | π₁ ≠ π₂ | IC da diferença e teste Z de 2 proporções (P agrupada) | 74,2% (12 anos ou mais) × 39,9% (demais) |
| H3 | O peso médio ao nascer difere de 3.200 g? | μ = 3.200 g | μ ≠ 3.200 g | IC t e teste t de 1 amostra | μ = 3.189 g |
| H4 | O peso médio difere entre mães com 7 ou mais consultas de pré-natal e as demais? | μ₁ = μ₂ | μ₁ ≠ μ₂ | IC da diferença e teste t de Welch | 3.248 g × 3.015 g |

Resultados observados na amostra oficial de n = 384:

- **H1 e H3 não rejeitam H₀**, embora H₀ seja falsa na população (π = 50,72%, contra 50%, e μ = 3.188,95 g, contra 3.200 g). São erros tipo II: os efeitos são pequenos em relação à variabilidade da amostra.
- **H2 e H4 rejeitam H₀** (diferenças populacionais de 34,26 p.p. e 233,10 g). São rejeições corretas. A simulação ao final ilustra o poder empírico de cada teste.

### O que mostrar para cada hipótese

1. Pergunta, variável e evento de interesse, H₀, H₁ e α
2. Verificação das condições (bloco abaixo), com ✓ ou ✗
3. Estimativa pontual (P ou x̄) e IC de 95%
4. Estatística de teste (Z ou t), graus de liberdade quando houver, valor-p e decisão ("rejeita H₀" ou "não rejeita H₀")
5. Gráfico da distribuição de referência (normal ou t) com a região de rejeição sombreada e a estatística observada marcada
6. Comparação com a população: o parâmetro real, se o IC contém o parâmetro (sim ou não) e se a decisão acertou
7. Conclusão em uma frase, em linguagem do problema e não só "rejeita H₀"

### Fórmulas (as mesmas dos slides)

```latex
IC_{\pi}: \; P \pm Z_{\alpha/2}\sqrt{\frac{P(1-P)}{n}} \qquad Z = \frac{P - \pi_0}{\sqrt{\pi_0(1-\pi_0)/n}}
```

```latex
IC_{\mu}: \; \bar{x} \pm t_{\alpha/2,\,n-1}\frac{S}{\sqrt{n}} \qquad T = \frac{\bar{x} - \mu_0}{S/\sqrt{n}}
```

```latex
T_{Welch} = \frac{\bar{x}_1 - \bar{x}_2}{\sqrt{\frac{S_1^2}{n_1} + \frac{S_2^2}{n_2}}} \qquad Z_{2p} = \frac{P_1 - P_2}{\sqrt{\bar{P}(1-\bar{P})\left(\frac{1}{n_1}+\frac{1}{n_2}\right)}}
```

No código: `scipy.stats.ttest_1samp`, `scipy.stats.ttest_ind(..., equal_var=False)` e `statsmodels.stats.proportion.proportions_ztest`. **Cuidado:** no teste de 1 proporção, o `proportions_ztest` usa P no erro-padrão por padrão. Para seguir os slides, que usam π₀, passe `prop_var=0.5`. Para o IC unilateral da H1, mostre também o limite inferior unilateral (com Z = 1,645). A implementação e os intervalos foram conferidos contra o `statsmodels`.

### Condições de aplicação

- **Independência:** a AAS garante, e n = 384 é menos de 10% de N
- **Proporções:** sucessos e fracassos ≥ 10 em cada grupo (n·π₀ e n·(1−π₀) na H1; os contadores de cada grupo na H2). Na amostra oficial, os grupos da H2 têm 115 e 269 casos
- **Médias:** n > 30 em cada grupo, para o TCL valer, mais o Q-Q plot do peso na amostra. Na amostra oficial, os grupos da H4 têm 287 e 97 casos. O peso é assimétrico à esquerda, mas com esses tamanhos o TCL dá conta
- **Welch e não t agrupado:** os desvios-padrão dos grupos são diferentes, então não se supõe variâncias iguais (a árvore de decisão dos slides leva ao Welch)

### Bloco final de comparação e limitações

- **Tabela-resumo:** uma linha por hipótese, com parâmetro populacional · estimativa · IC 95% · IC contém o parâmetro? · valor-p · decisão · H₀ é verdadeira na população? · tipo de resultado (acerto, erro tipo I ou erro tipo II)
- **Gráfico de ICs:** um ponto e um intervalo por parâmetro, com uma linha vertical no valor real
- **Simulação da variabilidade amostral** (bônus que pesa na nota de interpretação): sortear 1.000 amostras de 384 e mostrar (a) que cerca de 95% dos ICs contêm μ e π, como no exercício da "turma de 65 alunos" do lab ch4B, e (b) a fração de amostras que rejeitam H₀ em cada hipótese, que é o poder empírico. A amostra oficial continua sendo só a de semente 2026
- **Limitações:** um resultado vem de uma única amostra. A população mistura 11 anos com tendência de queda da cesárea. Os dados são administrativos e podem ter erros de registro. As associações de H2 e H4 não provam causalidade (escolaridade e pré-natal andam juntos com renda e acesso à saúde)

## 8. Estrutura do app Streamlit e publicação

Um único app multipágina gera os 3 links que a entrega exige, porque cada página do Streamlit tem a sua própria URL. A publicação é gratuita no Streamlit Community Cloud, a partir de um repositório público no GitHub.

```
sinasc-estatistica/
├── Inicio.py                 # navegação multipágina do aplicativo
├── app/
│   └── inicio.py             # capa: objetivo e fonte
├── pages/
│   ├── 1_Populacao.py        # Painel 1
│   ├── 2_Amostra.py          # Painel 2
│   └── 3_Inferencia.py       # Painel 3
├── src/
│   ├── 01_limpeza.py         # gera data/populacao.parquet
│   ├── 02_amostra.py         # gera data/amostra.csv (semente 2026)
│   ├── descritiva.py         # funções de gráficos e tabelas (Painéis 1 e 2)
│   └── inferencia.py         # ICs, testes, condições, simulação
├── data/
│   ├── populacao.parquet
│   └── amostra.csv
├── docs/decisoes.md
├── tests/test_inferencia.py  # testes dos cálculos e conferência com statsmodels
└── requirements.txt          # streamlit, pandas, pyarrow, numpy, scipy, statsmodels, plotly
```

**Detalhes que evitam problemas**

- Use o Parquet no app, e não o CSV de 40 MB: ele carrega bem mais rápido e fica muito menor no repositório
- Use `@st.cache_data` na função que lê os dados e na simulação de 1.000 amostras, para o painel não recalcular a cada clique
- Use Plotly nos gráficos, porque passar o mouse e dar zoom contam como "interativo". Os filtros da barra lateral (ano e variável) completam a interatividade
- A amostra fica salva em arquivo e não é sorteada de novo ao abrir o app
- Os apps gratuitos "dormem" depois de alguns dias sem acesso. Abra os links na véspera da entrega e, durante o período de avaliação, a cada 2 ou 3 dias

**Passo a passo do deploy**

1. Criar o repositório público no GitHub e subir o projeto
2. Em share.streamlit.io: "Create app" → escolher o repositório → arquivo principal `Inicio.py`
3. Escolher uma URL curta (por exemplo, `sinasc-poa-estatistica`)
4. Testar numa janela anônima e copiar as 3 URLs das páginas para a entrega

## 9. Roteiro do vídeo (meta: 3min50s; limite: 4 minutos)

O vídeo gasta metade do tempo na inferência e na comparação, porque o enunciado pede prioridade à interpretação, e não à descrição de gráficos. Grave a tela navegando no app e fale por cima. Os valores apresentados abaixo foram calculados com a amostra oficial e a população limpa.

| Tempo | Tela | Fala (resumo) |
| --- | --- | --- |
| 0:00–0:15 | Capa do app | "Usei dados de nascimentos de Porto Alegre para avaliar o que uma amostra de 384 registros revela sobre a população." |
| 0:15–0:35 | Painel 1, topo | Fonte SINASC, período de 2011 a 2021, população de 197.639 nascimentos após a limpeza e unidade amostral: cada nascimento. |
| 0:35–0:55 | Painel 2, cartão do sorteio | "Dimensionei a amostra com 95% de confiança, erro de 5 pontos percentuais e p = 0,5, o pior caso. Sorteei 384 nascimentos sem reposição, com semente 2026." |
| 0:55–1:10 | Painéis 1 e 2, tabela de comparação | "Na população, o peso médio foi 3.189 g e a taxa de cesáreas 50,7%. Na amostra, foram 3.228 g e 52,1%; diferenças são esperadas pela variabilidade amostral." |
| 1:10–1:30 | Painel 3, H1 | "A cesárea é maioria? Na amostra, P = 52,1%, com valor-p = 0,207: não rejeito H₀. Como a proporção populacional é 50,72%, ocorreu erro tipo II." |
| 1:30–1:50 | Painel 3, H2 | "Com 12 anos ou mais de estudo, a taxa amostral de cesáreas foi 72,2%, contra 43,5%. O valor-p é menor que 0,001: rejeito H₀, corretamente." |
| 1:50–2:10 | Painel 3, H3 | "O peso médio difere de 3.200 g? O intervalo de 95% vai de 3.172,7 a 3.284,0 g e o valor-p é 0,317: não rejeito H₀; é erro tipo II." |
| 2:10–2:35 | Painel 3, H4 | "Com sete ou mais consultas pré-natais, o peso amostral foi 327 g maior. O teste de Welch dá valor-p menor que 0,001: rejeito H₀. É associação, não causalidade." |
| 2:35–3:20 | Painel 3, tabela-resumo + simulação | "Os quatro intervalos contêm os parâmetros populacionais. Houve duas rejeições corretas e dois erros tipo II. Em mil amostras, a cobertura ficou entre 94,8% e 95,6%. Efeitos pequenos foram mais difíceis de detectar." |
| 3:20–3:50 | Painel 3, limitações | "A análise usa uma amostra, dados administrativos e uma população que varia no tempo. Os resultados mostram associações, não causas. Mesmo com 0,19% da população, a amostra permitiu estimar e testar hipóteses, com a incerteza indicada pelos intervalos." |

**Dicas de gravação**

- Escreva a fala completa a partir dessa tabela, mas fale olhando para a tela, e não lendo palavra por palavra
- Ensaie com cronômetro e mantenha o vídeo abaixo de 4 minutos; a meta de 3min50s reserva uma pequena margem. Se ultrapassar, corte detalhes descritivos, sem omitir as decisões e interpretações das quatro hipóteses
- Use o zoom do navegador em 125% para os números ficarem legíveis no vídeo
- No YouTube, deixe como "Não listado" e confira se abre sem login

## 10. Checklist de entrega × critérios de avaliação

Antes de postar, confira cada critério contra o que está no app e no vídeo. Se a sua amostra levar a uma decisão diferente da prevista na seção 7 (por exemplo, rejeitar H₀ na H1), isso não é erro: ajuste a fala e a tabela-resumo, e use o caso como exemplo de variabilidade amostral.

| Critério | Peso | Onde está | Conferência |
| --- | --- | --- | --- |
| Base: escolha, descrição e contexto | 10% | Painel 1, topo; vídeo 0:20 | Fonte, link, contexto, N, variáveis, população e unidade amostral |
| Dimensionamento e AAS | 10% | Painel 2, topo; vídeo 0:55 | Parâmetros justificados, fórmula, n = 384, semente e arquivo da amostra |
| Painel da população | 10% | Painel 1 | Medidas completas, gráfico certo para cada tipo de variável, interpretação curta |
| Painel da amostra | 10% | Painel 2 | Mesmos blocos + tabela e gráficos de comparação com a população |
| ICs e testes corretos | 20% | Painel 3 | 2 proporções + 2 médias; α, estatística, valor-p e decisão; condições verificadas; resultados conferidos contra o `statsmodels` |
| Interpretação e comparação | 20% | Painel 3, bloco final; vídeo 3:35 | IC contém o parâmetro? Decisão certa ou erro tipo I/II? Simulação e limitações |
| Vídeo | 20% | YouTube | Até 4 min, objetivo, foco em interpretação, números legíveis |

**O que vai no Moodle**

- [ ] Texto curto de apresentação: objetivo do trabalho, fonte e período dos dados, limpeza, dimensionamento e sorteio da amostra, análises realizadas e principais conclusões
- [ ] Link do Painel 1 — análise descritiva da população
- [ ] Link do Painel 2 — análise descritiva da amostra
- [ ] Link do Painel 3 — inferência estatística e comparação
- [ ] Link do vídeo no YouTube (até 4 min, "Não listado")
- [ ] Link da base original e a fonte: "SINASC – Eventos Vitais: Nascimentos, Prefeitura Municipal de Porto Alegre, dadosabertos.poa.br, acesso em nov/2026"
- [ ] Links do app e do vídeo testados numa janela anônima, sem login
