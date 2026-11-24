---
title: "Orquestração com IA"
slug: orquestracao-com-ia
lang: pt-BR
date: 2026-11-24
author: Moacyr Ricardo
tags: [claude code, herdr, orquestração, skills, spec-workflow, rich-html, produto]
reading_time: ~7 min
summary: "Orquestrar dezenas de sessões de IA é trabalho de PM: exige estudo, teste e tempo reservado. Prompts com herdr pra parte dos dados."
---

# Orquestração com IA

**TL;DR:** Orquestração com IA só funciona com estudo e teste: é preciso reservar tempo.

Eu era um aluno mala - o chato cheio de respostinha e que falava o tempo todo. Uma professora disse "quando você precisar estudar, vai cair do cavalo". Eu passava com ótimas notas e ela não viu quando o cavalo me derrubou lá pelos vinte e poucos anos: sentar na cadeira pra estudar Cálculo era dificil demais. E ainda sim passar raspando. Meus colegas - que também sofreram, é verdade - pareciam tranquilos com aquilo. Eu só queria saber logo pra sair dali... mas tive que sentar, aprender a estudar. Foi tempo e esforço.

Com IA tá acontecendo a mesma coisa: eu falo muito, abro muita sessão paralela (150 sessões abertas ao mesmo tempo) mas a nota não vinha... Umas terminadas, outras esperando uma decisão minha, outras que eu nem lembrava mais o que eram.

![Paleta Go to do herdr com 78 terminais abertos, agrupados por workspace](herdr-78-terminais.png) ![Outra tela da mesma paleta: 77 terminais, entre sessões de claude, codex e shells](herdr-77-terminais.png)

Saber onde cada uma está e quais são os próximos dois ou três passos não vem de graça. É o trabalho que meus PMs faziam e que engenheiro insiste em desvalorizar. Pega umas dicas pra você retormar um pouco do seu tempo e ir lá pedir desculpas praquele seu PM super paciente:

## O que é trabalho de PM aqui

Antes das dicas, vale separar duas coisas que a gente costuma misturar quando fala "o PM só fica organizando ticket". Tem uma parte que é dado e acompanhamento: o que está aberto, o que está parado esperando alguém, o que já terminou e ninguém fechou, o que depende do quê. E tem a outra parte, que é a difícil de verdade: decidir o que importa, negociar prioridade com quem quer tudo pra ontem, cuidar das pessoas que estão fazendo o trabalho.

A IA ajuda bastante na primeira parte: ela pergunta pra cada sessão o que está fazendo, junta, agrupa, mostra o que está esperando decisão. A segunda parte continua sendo sua, e não fica mais fácil porque tem um relatório bonito na frente. Ou seja: não, não é fácil ser PM, e as dicas abaixo não transformam ninguém em um. Elas só tiram o trabalho braçal do caminho pra sobrar cabeça pro resto.

## O herdr

Orca, herdr e t3code: cada um permite isso, do seu jeito. Vou falar do [herdr](https://herdr.dev).

Configure o herdr no seu repo e comece uma conversa: peça pro agente ver o que dá pra fazer com o herdr (`herdr --skill`) ou instale a integração dele (`herdr integration install claude`).

O ponto é que o agente passa a enxergar as outras sessões: listar, ler o que cada uma está fazendo, mandar mensagem, abrir sessão nova num repo, matar a que já acabou. Sem isso, quem faz esse meio de campo é você, pulando de aba em aba e tentando lembrar do que se tratava aquela sessão de ontem.

Depois teste esses prompts (escrevi em inglês, sem nenhum motivo especial):

### 1. Onde está tudo

> List all open sessions, ask each one what it is doing and why, and build a /rich-html:report grouping them into clusters.

Esse é o "status report" que todo PM monta toda semana, só que perguntando direto pra quem está fazendo o trabalho. Cada sessão responde o que está fazendo e por quê, e o [`/rich-html:report`](https://moacyrricardo.github.io/skills/rich-html-guide.html) junta tudo numa página com a conclusão no topo: quais grupos de trabalho existem, o que está parado esperando você, o que já terminou e dá pra fechar.

E dá pra melhorar: se você usa Linear e tem uma CLI configurada (eu uso o linearis), pede pra cruzar com as issues:

> List all open sessions, ask each one what it is doing and why, cross them with my Linear issues using the linearis CLI, and build a /rich-html:report grouping them into clusters. Flag sessions with no issue behind them and in-progress issues with no session working on them.

Aí o relatório para de ser só "o que está aberto no meu terminal" e vira "o que está aberto no meu terminal comparado com o que eu prometi pra alguém": sessão sem issue é trabalho que ninguém pediu (ou que ninguém registrou), e issue em andamento sem sessão é trabalho que ficou pra trás.

### 2. Manter as sessões saudáveis

> Find every session above 50% context, ask it to write a handoff document to /tmp, /clear it, and prompt it to continue from the handoff doc.

*(não vou explicar aqui o que é um handoff document rs)*

Sessão com contexto cheio fica lenta, cara e começa a esquecer o que combinou com você lá no começo. Fazer isso na mão em dezenas de sessões é exatamente o tipo de trabalho que ninguém faz até dar problema. Aqui a IA faz a manutenção e você só confere se o handoff faz sentido. Ah, e o que eu descrevo aqui é um pouco diferente do que o Matt Pocock construiu na skill de handoff dele (se quiser ver a dele, [tá aqui](https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff)).

### 3. Fechar o que dá pra fechar

> Capture the open work across the sessions working on {name-your-workstream}, record it with /spec-workflow:new (specs and/or concerns), and check: once everything is captured, kill those sessions.

Sessão aberta não é memória. Se o trabalho ainda não acabou mas não precisa de ninguém agora, ele vira uma spec ou uma concern no catálogo do repo (é o que o [`/spec-workflow:new`](https://moacyrricardo.github.io/skills/spec-workflow-guide.html) faz) e a sessão pode morrer em paz. Isso é o backlog: o PM não deixa a ideia morrer só porque ninguém está trabalhando nela hoje, mas também não deixa 30 abas abertas pra lembrar dela. O "check" no meio é importante - só mata depois de confirmar que tudo foi registrado.

Não usa o /spec-workflow? Sem problema: troca pela gestão do seu catálogo no Linear ou no Jira. Pede pra criar issue pro que ainda está aberto, completar o que já terminou e cancelar o que não faz mais sentido - e só depois matar as sessões.

### 4. A sessão "cérebro"

E um último, pra quem viu o [Matt Pocock falando de uma sessão "cérebro"](https://www.youtube.com/watch?v=hWe-j78vNpc) que orquestra as outras: na prática, é isso aqui:

> Check the boletim and minhabufunfa repos: the way minhabufunfa tunnels connections to allow receipts from boletim to be viewed is bad. Let's use the new auth system and plan it with /spec-workflow:new. Open Claude sessions via herdr to act on each repo. First build the contract between them and turn it into a /rich-html:decide surface in /tmp, capturing: reusing the new auth, a circuit breaker, and frontend caching.

*(O [boletim](https://boletim.iskeru.com) e o [minhabufunfa](https://minhabufunfa.iskeru.com) são dois produtos meus que conversam entre si)*

## Reserve o tempo e agradeça seu pm

Esses prompts não saem prontos e provavelmente não vão funcionar diretamente com você: então investe um pouco de tempo: teste, erre e ajuste até a coisa parar em pé do jeito que você gstaria - aaptado ao **seu** jeito de trabalhar. Você já tem ferramentas pra aprender a estudar e domar esse cavalo de IA.

E depois, de verdade, vai lá falar com seu PM e agradecer que ele ainda aturava tua carinha de mala. Ah - Belzinha, minha professora de inglês do fundamental: caí do cavalo, viu? Brigado pelo aviso - e foi mal pelo trabalho que eu dei.

## Testa aí

As skills que aparecem nos prompts são open source: [moacyrricardo.github.io/skills](https://moacyrricardo.github.io/skills). Pode testar e dar um feedback :)
