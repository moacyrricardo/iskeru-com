---
title: "AI writes 1k lines. You're the one who reads them."
slug: ai-writes-1k-lines
lang: en
date: 2026-11-20
written: 2026-09
author: Moacyr Ricardo
tags: [claude code, skills, rich-html, code review, decisions]
reading_time: ~5 min
summary: "Generating got cheap. Reading, understanding and deciding are still expensive - and still human work. The rich-html skills are my answer to that."
translated_by: Claude
---

# AI writes a lot - but you're the one who reads it

**TL;DR:** Time spent reading fluff is time badly spent: how to filter the noise and focus on what matters

## The bottleneck moved

Everyone who tried Opus 5 felt the same thing: it talks too much and explains too little. Leaving Opus 4.5 was hard: so much so that, until 5.5 came out, I went back to 4.5. The reason was how much fluff and opinion Opus 4.5 generated. Scary - and it wasn't an isolated experience. But while 4.5 was clearly an outlier, AI let everyone write texts and "improve" them with a prompt.

Look: "improve" is in quotes on purpose - because I believe that's part of the big problem: it got very easy to generate a lot of text and use non-colloquial vocabulary. And, in a world where speaking well means using difficult words,

When we run 1, 2 or even 10 little projects in parallel, the bottleneck is always the human. Picking context back up is expensive: when the AI needs our input on project A, we've already unloaded all of it to take care of project B.

There's so much we keep writing and receiving from other people (and their AIs): the volume only grows. A PR written by AI easily becomes 800+ lines: code + tests + docs. Nobody
reads that the way they read an 80-line PR.

The problem isn't lack of knowledge. It's hardware - ours was built to handle a little information: now we generate twice as much while doing 10 things in parallel. It's a lot.

## First I asked for reports

I started asking the AI for reports: they worked until I noticed I was spending a lot of time refining
those texts to understand better where to put my 'hardware'. So when you spend the hardware taking care of the tool, it became clear I wasn't moving forward because the tool wasn't good.

So I stopped refining the text and started refining the tool that generates the text.

## Three questions, three skills

Each skill answers a question I kept asking myself:

**"What's going on here?" → [`/rich-html:report`](https://moacyrricardo.github.io/skills/rich-html-guide.html)**
Brings different sources together: docs, issues, PRs, git history, code, logs. It cross-checks the
information, analyzes it and delivers a page with the conclusion at the top and the evidence one click away.
It only reads; it changes nothing. And of course: you can add specific requests

**"What do I need to decide?" → [`/rich-html:decide`](https://moacyrricardo.github.io/skills/rich-html-guide.html)**
Gathers the decisions waiting on me - concerns, review threads, questions in issues,
TODOs - in a single page. Each decision opens in place with its full context, I pick one option
per decision, and the page generates a single prompt to hand back to the agent to execute everything.

Beyond that: a what&why&how framework + visual comparison.

**"What changed in this PR, and why?" → [`/rich-html:branch-review`](https://moacyrricardo.github.io/skills/rich-html-guide.html)**
Filters the diff by facet - only code, only tests, only docs/spec - and regroups it by intent: the why
of each group of changes, not by file. You can separate "what the new feature is" from the
"plumbing" around it.

## Why HTML, and not chat

Chat is great for talking and terrible for coming back to later. The three skills follow the same contract
(`html-doc`): a single, self-contained file that works in the browser or as a Claude Artifact, with
light/dark theme, and with the detail hidden until you need it.

That's what lets the page be read by someone else - including someone who wasn't in the conversation.

## Try it

The skills are open source: [moacyrricardo.github.io/skills](https://moacyrricardo.github.io/skills)
Feel free to try them and give feedback :)
