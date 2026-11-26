---
title: "Construindo o fo-foca: notas de reunião locais num notebook com GPU de 2 GB"
slug: construindo-fofoca
lang: pt-BR
date: 2026-11-20
author: Moacyr Ricardo
tags: [fo-foca, IA local, whisper, llm, open source, pt-BR]
reading_time: ~6 min
summary: "Testei extensão de Chrome, testei o Yogurt, e acabei medindo o que minha GPU de 2 GB aguentava de verdade. Daí surgiu o fo-foca."
cover: fofoca-logo.png
product: fofoca
---

# Construindo o fo-foca: notas de reunião locais num notebook com GPU de 2 GB

**TL;DR**: queria tomar notas automaticamente e acabei construindo um app que roda local e roda LLMs e processos locais. Sem web, sem modelo na nuvem. Brinquei de compartilhar multiplos modelos em uma GPU de 2GB e de fazer swap. Aprendi um bocado em 1 dia :) - e ainda construí o fofoca.

![fo-foca funcionando](demo.gif)

## Onde eu comecei

Eu queria uma coisa simples: sair de uma reunião com o que foi dito e o que ficou combinado, sem
mandar o áudio pra lugar nenhum: ficar gerenciando isso manualmente é um saco. Muitos colegas usam e tinham sugerido o Granola - e essa era a solução barata e fácil. Mas...

Por que não só usar o Granola? Bom, primeiro por que eu sou um desenvolvedor - pra que facilitar se eu posso perder dias fazendo do jeito complicado rs.
Apesar de acreditar que o Granola resolve <i>(provavelmente)</i> (não sei - nunca testei) - minha idéia era ficar no zero cost / opensource e aproveitar minha GPU. Com claudinho do meu lado comecei a testar o whisper, tentei extensões do chrome que expusessem a transcrição automática, etc.. Não funcionou
bem pra mim e continuei procurando e cheguei no **Yogurt**.

O Yogurt tem uma proposta muito boa: detecta sozinho o que sua máquina aguenta e escolhe o modelo.
Eu gosto de mágica - quando funciona. Pra mim, na minha máquina, o yogurt azedou. E tentar configurar ele foi imposśivel: ele tentava rodar um Gemma4B e não permitia eu dizer a ele algo diferente. Eu - dev/programador/fuçador - estava trancado pra fora. O modelo era ruim, a máquina ficava lenta. Minhas 70 sessões de claude (talvez eu precise de ajuda...) estavam sofrendo. "O deploy" virou "o plói" e nada funcionava.

Então fui ver o que a GPU aguentava de verdade.

## Medindo antes de construir

Antes do primeiro commit, rodei um estudo de viabilidade na própria MX230:

| O quê | Resultado |
|---|---|
| Whisper large-v3-turbo (q5_0) na GPU | 824 MiB de VRAM, acompanha ao vivo |
| Taxa de erro em pt-BR | **~2 %** (vs ~12 % do small) |
| Qwen3.5-2B (Q4_K_M) na GPU | 1,4–1,6 GB, ~17 tokens/s |
| Os dois juntos | não cabem em 2 GB → alterna, ~3 s por troca |

O modelo "grande" coube - mas não sobrava espaço pra mais nada: Qwen (1414 MiB) + Whisper (824 MiB) passa dos
2048 MiB — out of memory.

## A parte difícil: testar ideia rápido

O que tornou o fofoca possível foi esse ciclo de testar e medir. O Claude Code fez a parte chata
— rodar os benchmarks, GPU e CPU, modelo por modelo — e eu fiquei com a parte boa: ter ideias e ver
na hora se elas paravam em pé. Ele nem tinha fechado um teste e eu já mandava outra mensagem: testa assim; testa assado. Bom demais :)

Algumas ideias que o benchmark respondeu:

- **Trocar os modelos na GPU ou manter os dois carregados?** Trocar custa ~3 s. A cada chunk de
  30 s, trocando dava ~37 s de trabalho; com os dois carregados, ~53 s. Trocar ganhou.
- **Dividir o Qwen entre GPU e CPU?** Pior opção de todas: deixou o Whisper ~35 % mais lento.
- **E uma pegadinha:** no whisper.cpp, `-dev 1` caía pro CPU sem avisar. A primeira rodada "na
  GPU" era na verdade no CPU. Sem medir, eu nunca teria percebido.

Daí saiu o desenho: o Whisper fica na GPU transcrevendo ao vivo; o LLM entra trocado só pra
resumir; e depois da call vem um pós-processamento na transcrição inteira — separação de falantes
no CPU e notas checadas, que é onde os erros são corrigidos.

E continuar medindo continuou rendendo: cortar o áudio nas pausas naturais da fala (em vez de
esperar o chunk de 30 s fechar) baixou o atraso do texto ao vivo de 21,5 s pra 12,7 s, e medir as notas achou um servidor órfão segurando 813 MiB dos 2 GB.

*(embed: página de benchmarks interativa — specs/001-assets/benchmarks-mx230.html)*

## Como eu construí

Com a parte que eu não conhecia muito sobre (LLMs locais + GPU) encaminhada - foi só avançar no app. Usei minha skill [/prototype](https://moacyrricardo.github.io/skills/prototype-guide.html) - e usei o gemini pra gerar icones/logo.

Cada funcionalidade virou uma spec num [catálogo numerado](https://moacyrricardo.github.io/skills/spec-workflow-guide.html) (`specs/`), com uma seção que registra
onde a realidade diferiu do plano. O Claude Code implementou, em branches empilhadas, uma por spec;
eu revisei, decidi e testei na mão. Do primeiro commit (19/11, 15h48) a 12 specs prontas foi até
as 9h do dia seguinte.

## O que vem

- **Setup automático** — detectar GPU/RAM, escolher o que cabe, medir na primeira execução. Sim, a
  mesma ideia do Yogurt — mas mostrando o porquê e deixando você mudar tudo.
- **Empacotamento** — AppImage. *(Atualização 25/11: saiu — builds de teste em AppImage e .deb.)*
- **Servidor MCP** (ainda em aberto) — deixar outras ferramentas de IA lerem suas reuniões.

## Testa aí

Ainda é pré-alpha: Linux x86-64, agora com builds de teste (AppImage e .deb). Relatos de hardware ("isso aqui cabe na minha GPU") e
gravações de teste em pt-BR são muito bem-vindos.

Pra baixar e instalar: [moacyrricardo.github.io/fofoca](https://moacyrricardo.github.io/fofoca/). Se quiser testar e dar um feedback: github.com/moacyrricardo/fofoca - enjoy :)
