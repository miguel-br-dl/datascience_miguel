# datascience_miguel
Meu repositório para datascience

## Data Science com Netflix

Ontem eu descobri que é possível recuperar da Netflix tudo o que nós assistimos. Neste link aqui: https://www.netflix.com/viewingactivity

* Acessei o link acima;
* Peguei o HTML deste resultado, clicando em "ver mais" até chegar no fim (no meu caso 2015);
* Processando o HTML (vide jupyter notebook) peguei os ID dos filmes. 
* Capturei (usando crawling) os gêneros de cada item assistido.
* Retirei as duplicidades e, neste caso, considerei todos os episódios como se fosse 1 item apenas.
* Aí levantei um gráfico do que assistimos aqui em casa desde 2015. (vide jupyter notebook)

Está aí o resultado:

![Grafico](https://github.com/miguel-br-dl/datascience_miguel/blob/master/filmes.png?raw=true)
