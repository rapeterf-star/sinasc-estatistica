# Resumo do trabalho — SINASC Porto Alegre

## Em linhas gerais

Vamos analisar os registros de nascimentos de Porto Alegre para verificar o que uma amostra aleatória de 384 nascimentos consegue revelar sobre a população. O trabalho será apresentado em três painéis interativos publicados em um app Streamlit, em um vídeo curto no YouTube como "Não listado" e em um texto de apresentação no Moodle.

## Base de dados

Usaremos o **SINASC — Eventos Vitais: Nascimentos**, da Prefeitura de Porto Alegre:

https://dadosabertos.poa.br/dataset/sinasc

A base contém 197.801 registros de 2011 a 2021. Após retirar registros com peso abaixo de 500 g, a população analisada terá 197.639 nascimentos.

## Atividades principais

1. Preparar e limpar os dados; dimensionar a amostra com a [calculadora de tamanho de amostra da SurveyMonkey](https://pt.surveymonkey.com/learn/research-and-analysis/sample-size-calculator/) (95% de confiança, erro de 5 pontos percentuais e proporção de 50%) e sortear 384 nascimentos de forma reprodutível.
2. Criar um painel descritivo da população e outro da amostra, comparando medidas como peso ao nascer e proporção de cesáreas.
3. Usar a amostra para realizar quatro testes estatísticos: dois sobre proporções e dois sobre médias. Apresentar intervalos de confiança, valores-p, decisões e condições de aplicação.
4. Comparar os resultados da amostra com os valores conhecidos na população e explicar o que os resultados significam, incluindo as limitações da análise.
5. Publicar os painéis em um aplicativo Streamlit, apresentar o trabalho em um vídeo de até quatro minutos no YouTube como "Não listado" e entregar no Moodle um texto curto com o contexto, o método e os principais resultados, junto com os links e a fonte dos dados.

## O que pretendemos mostrar

O trabalho atende à avaliação ao demonstrar como descrever dados, dimensionar e selecionar uma amostra, calcular intervalos de confiança e testar hipóteses. Também vamos interpretar as conclusões no contexto dos nascimentos em Porto Alegre e discutir a diferença entre associação e causalidade.
