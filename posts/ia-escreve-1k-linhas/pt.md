---
title: "A IA escreve 1k linhas. Quem lê é você."
slug: ia-escreve-1k-linhas
lang: pt-BR
date: 2026-11-20
written: 2026-09
author: Moacyr Ricardo
tags: [claude code, skills, rich-html, code review, decisões]
reading_time: ~5 min
summary: "Gerar ficou barato. Ler, entender e decidir continua caro - e continua sendo trabalho humano. As skills rich-html são minha resposta pra isso."
---

# A IA escreve muito - mas quem lê é você

**TL;DR:** Tempo lendo lero-lero é tempo mal gasto: como filtrar o barulho e focar no que é importante

## O gargalo mudou de lugar

Todo mundo que testou o Opus 5 sentiu o seguinte: fala demais e explica de menos. Sair do opus 4.5 foi dificil: tanto que, até o lançamento do 5.5, eu regressei pro 4.5. O motivo era o tanto de lero lero e opnião que o opus 4.5 gerava. Assustador - e não era umae experiência isolada. Mas enquanto o 4.5 foi claramente um outliar, a IA permitiu que todos pudessem escrever textos e "melhora-los" com um prompt.

Veja: "melhorá-los" aqui com aspas propositalmente - pq acredito que isso parte do o grande problema: ficou muito fácil gerar muito texto e usar vocabulário não coloquial. E, num mundo em que falar bonito é usar palavra dificil, 

Quando a gente toca 1, 2 ou até 10 projetinhos em paralelo, o gargalo é sempre o humano. Retomar
contexto custa caro: quando a IA precisa do nosso input no projeto A, a gente já descarregou tudo
dele pra cuidar do projeto B. 

É tanta coisa que a gente vai escrevendo e recebendo de outras pessoas (e suas IAs): o volume só cresce. Um PR escrito por IA vira fácil 800+ linhas: código + testes + docs. Ninguém
lê isso do jeito que lia um PR de 80.

O problema não é falta de conhecimento. É hardware mesmo - o nosso foi feito pra lidar com um pouco de informação: agora a gente gera o dobro enquanto faz 10 coisas em paralelo. É muita coisa.

## Primeiro eu pedi relatórios

Comecei pedindo relatórios pra IA: funcionavam até eu perceber que passava muito tempo refinando
esses textos pra entender melhor onde colocar o meu 'hardware'. Então quando você gasta o hardware pra cuidar da ferramenta, ficou claro que eu não avançava pq a ferramenta não tava boa.

Então parei de refinar o texto e passei a refinar a ferramenta que gera o texto.

## Três perguntas, três skills

Cada skill responde uma pergunta que eu me fazia toda hora:

**"O que tá acontecendo aqui?" → [`/rich-html:report`](https://moacyrricardo.github.io/skills/rich-html-guide.html)**
Junta fontes diferentes: docs, issues, PRs, histórico do git, código, logs. E cruza as
informações, faz analises e entrega uma página com a conclusão no topo e a evidência a um clique de distância.
Só lê; não muda nada. E claro: da pra adicionar pedidos especificos

**"O que eu preciso decidir?" → [`/rich-html:decide`](https://moacyrricardo.github.io/skills/rich-html-guide.html)**
Junta as decisões que estão esperando por mim - concerns, threads de review, perguntas em issues,
TODOs - numa página só. Cada decisão abre no lugar com o contexto completo, eu escolho uma opção
por decisão, e a página gera um único prompt pra devolver pro agente executar tudo.

Pra além disso: what&why&how framework + comparação visual.

**"O que mudou nesse PR, e por quê?" → [`/rich-html:branch-review`](https://moacyrricardo.github.io/skills/rich-html-guide.html)**
Filtra o diff por faceta - só código, só testes, só docs/spec - e reorganiza por intenção: o porquê
de cada grupo de mudanças, não por arquivo. Dá pra separar "o que é a feature nova" do
"encanamento" em volta.

## Por que HTML, e não chat

Chat é ótimo pra conversar e péssimo pra voltar depois. As três skills seguem o mesmo contrato
(`html-doc`): um arquivo só, autocontido, que funciona no navegador ou como Artifact do Claude, com
tema claro/escuro, e com o detalhe escondido até você precisar dele.

É isso que deixa a página ser lida por outra pessoa - inclusive por quem não estava na conversa.

## Testa aí

As skills são open source: [moacyrricardo.github.io/skills](https://moacyrricardo.github.io/skills)
Pode testar e dar um feedback :)
