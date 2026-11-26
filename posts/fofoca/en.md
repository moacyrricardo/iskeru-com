---
title: "Building fo-foca: local meeting notes on a laptop with a 2 GB GPU"
slug: building-fofoca
lang: en
date: 2026-11-20
author: Moacyr Ricardo
tags: [fo-foca, local AI, whisper, llm, open source, pt-BR]
reading_time: ~6 min
summary: "I tried a Chrome extension, I tried Yogurt, and ended up measuring what my 2 GB GPU could really handle. That's where fo-foca came from."
cover: fofoca-logo.png
product: fofoca
translated_by: Claude
---

# Building fo-foca: local meeting notes on a laptop with a 2 GB GPU

**TL;DR**: I wanted to take notes automatically and ended up building an app that runs locally and runs LLMs and local processes. No web, no cloud model. I played with sharing multiple models on a 2 GB GPU and with swapping them. I learned a lot in 1 day :) - and I still built fofoca.

![fo-foca in action](demo.gif)

## Where I started

I wanted something simple: leave a meeting with what was said and what was agreed, without
sending the audio anywhere: managing that by hand is a pain. Many colleagues use Granola and had suggested it - and that was the cheap, easy solution. But...

Why not just use Granola? Well, first because I'm a developer - why make it easy when I can lose days doing it the complicated way lol.
Although I believe Granola solves it *(probably)* (I don't know - never tried it) - my idea was to stay zero cost / open source and make use of my GPU. With my little Claude by my side I started testing Whisper, tried Chrome extensions that exposed the automatic transcription, etc.. It didn't work
well for me, so I kept looking and found **Yogurt**.

Yogurt has a very good idea: it detects on its own what your machine can handle and picks the model.
I like magic - when it works. For me, on my machine, Yogurt went sour. And trying to configure it was impossible: it tried to run a Gemma4B and wouldn't let me tell it anything different. I - dev/programmer/tinkerer - was locked out. The model was bad, the machine got slow. My 70 Claude sessions (maybe I need help...) were suffering. "O deploy" became "o plói" and nothing worked.

So I went to see what the GPU could really handle.

## Measuring before building

Before the first commit, I ran a feasibility study on the MX230 itself:

| What | Result |
|---|---|
| Whisper large-v3-turbo (q5_0) on the GPU | 824 MiB of VRAM, keeps up live |
| Error rate in pt-BR | **~2 %** (vs ~12 % for small) |
| Qwen3.5-2B (Q4_K_M) on the GPU | 1.4–1.6 GB, ~17 tokens/s |
| Both together | don't fit in 2 GB → swap, ~3 s per swap |

The "large" model fit - but there was no room left for anything else: Qwen (1414 MiB) + Whisper (824 MiB) goes past
2048 MiB — out of memory.

## The hard part: testing ideas fast

What made fofoca possible was this loop of testing and measuring. Claude Code did the tedious part
— running the benchmarks, GPU and CPU, model by model — and I got the good part: having ideas and seeing
right away whether they held up. It hadn't even finished one test and I was already sending another message: try it this way; try it that way. So good :)

Some ideas the benchmark answered:

- **Swap the models on the GPU, or keep both loaded?** A swap costs ~3 s. For each 30 s chunk,
  swapping took ~37 s of work; with both loaded, ~53 s. Swapping won.
- **Split Qwen between GPU and CPU?** The worst option of all: it made Whisper ~35 % slower.
- **And a gotcha:** in whisper.cpp, `-dev 1` silently fell back to the CPU. The first "GPU" run
  was actually on the CPU. Without measuring, I'd never have noticed.

That gave the design: Whisper stays on the GPU transcribing live; the LLM is swapped in only to
summarize; and after the call there's a post-processing pass over the whole transcript — speaker
separation on the CPU and checked notes, which is where errors get corrected.

And measuring kept paying off: cutting the audio at natural pauses in speech (instead of waiting
for the 30 s chunk to close) brought the live text delay down from 21.5 s to 12.7 s, and measuring the notes found an orphaned server holding 813 MiB of the 2 GB.

*(embed: interactive benchmark page — specs/001-assets/benchmarks-mx230.html)*

## How I built it

With the part I didn't know much about (local LLMs + GPU) sorted out - it was just a matter of moving forward with the app. I used my [/prototype](https://moacyrricardo.github.io/skills/prototype-guide.html) skill - and used Gemini to generate icons/logo.

Each feature became a spec in a [numbered catalog](https://moacyrricardo.github.io/skills/spec-workflow-guide.html) (`specs/`), with a section recording where reality
differed from the plan. Claude Code implemented them on stacked branches, one per spec;
I reviewed, decided and tested by hand. From the first commit (Nov 19, 3:48 pm) to 12 finished specs took until
9 am the next day.

## What's next

- **Automatic setup** — detect GPU/RAM, pick what fits, measure on first run. Yes, the
  same idea as Yogurt — but showing why and letting you change everything.
- **Packaging** — AppImage. *(Update, Nov 25: shipped — test builds as AppImage and .deb.)*
- **MCP server** (still open) — let other AI tools read your meetings.

## Try it

It's still pre-alpha: Linux x86-64, now with test builds (AppImage and .deb). Hardware reports ("this fits on my GPU") and
pt-BR test recordings are very welcome.

To download and install: [moacyrricardo.github.io/fofoca](https://moacyrricardo.github.io/fofoca/). If you want to try it and give feedback: github.com/moacyrricardo/fofoca - enjoy :)
