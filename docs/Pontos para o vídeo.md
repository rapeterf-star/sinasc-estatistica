# Pontos para comentar no vídeo

## Por que usamos 50% no cálculo da amostra?

Os 50% são uma hipótese conservadora para dimensionar a amostra quando a proporção de interesse é desconhecida. Esse valor maximiza a variabilidade de uma proporção e, portanto, evita calcular uma amostra pequena demais. Não é uma previsão de que metade dos nascimentos será cesárea.

Isso é diferente da hipótese H1: nela, usamos a amostra para avaliar se a taxa de cesáreas é maior que 50%. Depois, comparamos a estimativa amostral com a proporção observada na população completa, que é aproximadamente 50,7%.

Uma proporção amostral diferente — por exemplo, 70% — não significa automaticamente que o estudo "errou". Amostras variam; o intervalo de confiança ajuda a avaliar a precisão da estimativa e a compatibilidade com o valor populacional.

## Possível incremento para avaliar ao final

Depois que todos os requisitos do enunciado estiverem concluídos, avaliar se cabe acrescentar uma análise curta dos dados com algum conteúdo adicional visto em aula, como correlação ou regressão. Isso é opcional, não altera o escopo principal e só deve ser incluído se houver tempo e se ajudar a interpretar os dados sem sugerir causalidade.

Como referência complementar da disciplina, consultar os [slides de Probabilidade e Estatística da UFRGS](https://www.ufrgs.br/probabilidade-estatistica/slides/index.html). O material lista conteúdos diretamente relacionados ao trabalho — análise exploratória e medidas descritivas, distribuições amostrais, testes de hipóteses para médias e proporções — e também coeficiente de correlação e regressão linear simples. Estes dois últimos ficam como possíveis incrementos a avaliar somente depois da conclusão do escopo obrigatório.

## Por que não usamos um heatmap de temperatura?

A base SINASC usada no trabalho não contém uma variável de temperatura; portanto, não há valores desse tipo que possam ser representados em um mapa de calor sem acrescentar outra fonte de dados e ampliar o escopo. Além disso, o exemplo de temperaturas por mês em *Fundamentals of Data Visualization*, de Claus O. Wilke (O’Reilly, 2019), ilustra a comparação de distribuições com boxplots — não é um heatmap. Para manter a análise coerente com os dados disponíveis, usamos boxplots para comparar o peso ao nascer entre grupos e gráficos de linha para mostrar tendências anuais.
