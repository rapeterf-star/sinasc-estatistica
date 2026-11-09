# Pontos para comentar no vídeo

## Por que usamos 50% no cálculo da amostra?

Os 50% são uma hipótese conservadora para dimensionar a amostra quando a proporção de interesse é desconhecida. Esse valor maximiza a variabilidade de uma proporção e, portanto, evita calcular uma amostra pequena demais. Não é uma previsão de que metade dos nascimentos será cesárea.

Isso é diferente da hipótese H1: nela, usamos a amostra para avaliar se a taxa de cesáreas é maior que 50%. Depois, comparamos a estimativa amostral com a proporção observada na população completa, que é aproximadamente 50,7%.

Uma proporção amostral diferente — por exemplo, 70% — não significa automaticamente que o estudo "errou". Amostras variam; o intervalo de confiança ajuda a avaliar a precisão da estimativa e a compatibilidade com o valor populacional.

## Por que a amostra é pequena diante de uma população tão grande?

O tamanho da amostra depende da **precisão desejada**, não do tamanho da população. O erro-padrão de uma proporção, √(p(1−p)/n), depende de n e não de N. Para uma margem de 5 pontos percentuais com 95% de confiança, são necessários cerca de 384 elementos, seja a população uma cidade ou um país. O N só pesa quando a população é pequena, por meio da correção para população finita.

| População (N) | Amostra (n) | Fração amostral |
| --- | --- | --- |
| 1.000 | 278 | 27,8% |
| 1.776 (estudo complementar SIM, óbitos infantis) | 316 | 17,8% |
| 10.000 | 370 | 3,7% |
| **197.639 (SINASC)** | **384** | **0,19%** |
| 10 milhões | 384 | 0,004% |

No SINASC, a correção para população finita quase não muda o resultado (383,4 → 384). No estudo complementar do SIM, com população de 1.776 óbitos infantis, ela reduz a amostra de 385 para 316. A população do SINASC é 111 vezes maior, mas a amostra é só 22% maior.

**Analogia:** para saber se uma sopa está salgada, basta provar uma colher, seja a panela pequena ou um caldeirão, desde que a sopa esteja bem misturada. O sorteio aleatório é o que "mistura a sopa"; a precisão depende do tamanho da colher, não do tamanho da panela.

**Frase pronta para o vídeo (cerca de 15 segundos), logo após citar n = 384:**
> "Pode parecer pouco: 384 nascimentos representam menos de 0,2% da população. Mas a precisão de uma amostra depende do seu tamanho, não da fração da população. É como provar uma sopa: uma colher basta, seja a panela pequena ou um caldeirão, desde que a sopa esteja bem misturada — e o sorteio aleatório é o que garante essa mistura."

## Análise complementar incluída no relatório

Depois de concluir os requisitos principais, foi incluída no relatório uma análise exploratória curta de correlação e regressão linear simples entre idade materna e peso ao nascer. Ela não altera o escopo principal e não sustenta uma interpretação causal.

Como referência complementar da disciplina, consultar os [slides de Probabilidade e Estatística da UFRGS](https://www.ufrgs.br/probabilidade-estatistica/slides/index.html). O material lista conteúdos diretamente relacionados ao trabalho — análise exploratória e medidas descritivas, distribuições amostrais, testes de hipóteses para médias e proporções — além de correlação e regressão linear simples.

No vídeo, mencionar a análise complementar em uma frase breve, sem fórmulas, coeficientes ou detalhes de interpretação. O vídeo de 4 a 5 minutos deve continuar priorizando os resultados obrigatórios.

## Por que não usamos um heatmap de temperatura?

A base SINASC usada no trabalho não contém uma variável de temperatura; portanto, não há valores desse tipo que possam ser representados em um mapa de calor sem acrescentar outra fonte de dados e ampliar o escopo. Além disso, o exemplo de temperaturas por mês em *Fundamentals of Data Visualization*, de Claus O. Wilke (O’Reilly, 2019), ilustra a comparação de distribuições com boxplots — não é um heatmap. Para manter a análise coerente com os dados disponíveis, usamos boxplots para comparar o peso ao nascer entre grupos e gráficos de linha para mostrar tendências anuais.

## Como explicar o recorte de peso abaixo de 500 g

Os 162 registros abaixo de 500 g foram excluídos pelo recorte operacional já adotado, e a análise não será refeita. A exclusão não significa que todos esses registros sejam erros: 142 têm peso positivo, e um nascido vivo de peso extremamente baixo pode ser registrado se houver sinais de vida. Assim, os resultados descrevem os 197.639 registros com peso ≥ 500 g e devem ser interpretados com essa limitação. O Q-Q plot do peso mostra afastamento da reta de referência na cauda inferior; isso evidencia que a distribuição não é perfeitamente normal, mas não é, isoladamente, motivo para apagar ou ajustar observações.

Referências para contextualização: [Secretaria Estadual da Saúde do RS — Mortalidade perinatal, p. 3](http://www1.saude.rs.gov.br/dados/1249057345460Mortalidade_Perinatal_no_RS_grassi.pdf) (definição de nascido vivo) e [artigo da Revista Indicadores Econômicos FEE](https://revistas.planejamento.rs.gov.br/index.php/indicadores/article/view/3676/3667) (contexto epidemiológico de baixo peso).
