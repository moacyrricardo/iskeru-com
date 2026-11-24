---
title: "Orchestrating with AI"
slug: orchestrating-with-ai
lang: en
date: 2026-11-24
author: Moacyr Ricardo
tags: [claude code, herdr, orchestration, skills, spec-workflow, rich-html, product]
reading_time: ~7 min
summary: "Orchestrating dozens of AI sessions is PM work: it takes study, testing and time set aside. herdr prompts for the data part."
translated_by: Claude
---

# Orchestrating with AI

**TL;DR:** Orchestrating with AI only works with study and testing: you have to set time aside.

I was an annoying student - the pain in the neck with a smart answer for everything who talked the whole time. A teacher once said "when you actually need to study, you're going to fall off your horse". I passed with great grades and she wasn't there to see the horse throw me, somewhere in my early twenties: sitting down to study Calculus was way too hard. And even then I barely scraped by. My classmates - who also suffered, to be fair - seemed fine with it. I just wanted to get it over with and get out of there... but I had to sit down and learn how to study. It took time and effort.

The same thing is happening with AI: I talk a lot, I open a lot of parallel sessions (150 sessions open at the same time) but the grades weren't coming... Some finished, others waiting on a decision from me, others I couldn't even remember what they were about anymore.

![herdr's Go to palette with 78 terminals open, grouped by workspace](herdr-78-terminais.png) ![Another view of the same palette: 77 terminals across claude and codex sessions and shells](herdr-77-terminais.png)

Knowing where each one stands and what its next two or three steps are doesn't come for free. It's the work my PMs used to do and that engineers insist on undervaluing. Grab a few tips to win back some of your time and go apologize to that super patient PM of yours:

## What the PM work is here

Before the tips, it's worth separating two things we tend to lump together when we say "the PM just shuffles tickets around". There's a part that is data and tracking: what's open, what's stalled waiting on someone, what's finished and nobody closed, what depends on what. And there's the other part, the genuinely hard one: deciding what matters, negotiating priority with people who want everything yesterday, taking care of the people doing the work.

AI helps a lot with the first part: it asks each session what it's doing, gathers it, groups it, shows what's waiting on a decision. The second part is still yours, and it doesn't get any easier because there's a nice report in front of you. In other words: no, being a PM isn't easy, and the tips below don't turn anyone into one. They just get the grunt work out of the way so there's headspace left for the rest.

## herdr

Orca, herdr and t3code: each one lets you do this kind of orchestration, in its own way. I'll talk about [herdr](https://herdr.dev).

Set up herdr in your repo and start a conversation: ask the agent to look at what it can do with herdr (`herdr --skill`) or install its integration (`herdr integration install claude`).

The point is that the agent can now see the other sessions: list them, read what each one is doing, send them messages, open a new session in a repo, kill the ones that are done. Without that, you're the one doing the coordination, jumping from tab to tab trying to remember what yesterday's session was about.

Then try these prompts (I wrote them in English, for no particular reason):

### 1. Where everything stands

> List all open sessions, ask each one what it is doing and why, and build a /rich-html:report grouping them into clusters.

This is the "status report" every PM puts together every week, except it asks the people doing the work directly. Each session says what it's doing and why, and [`/rich-html:report`](https://moacyrricardo.github.io/skills/rich-html-guide.html) pulls it all into one page with the conclusion at the top: which workstreams exist, what's stalled waiting on you, what's finished and can be closed.

And you can take it further: if you use Linear and have a CLI set up (I use linearis), ask it to cross the sessions with your issues:

> List all open sessions, ask each one what it is doing and why, cross them with my Linear issues using the linearis CLI, and build a /rich-html:report grouping them into clusters. Flag sessions with no issue behind them and in-progress issues with no session working on them.

Then the report stops being just "what's open in my terminal" and becomes "what's open in my terminal compared with what I promised someone": a session with no issue is work nobody asked for (or nobody recorded), and an in-progress issue with no session is work that got left behind.

### 2. Keeping sessions healthy

> Find every session above 50% context, ask it to write a handoff document to /tmp, /clear it, and prompt it to continue from the handoff doc.

*(I'm not going to explain what a handoff document is here lol)*

A session with a full context gets slow, expensive, and starts forgetting what it agreed with you at the start. Doing this by hand across dozens of sessions is exactly the kind of work nobody does until something breaks. Here the AI does the maintenance and you just check that the handoff makes sense. Oh, and what I'm describing here is a bit different from what Matt Pocock built in his handoff skill (if you want to see his, [it's here](https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff)).

### 3. Closing what can be closed

> Capture the open work across the sessions working on {name-your-workstream}, record it with /spec-workflow:new (specs and/or concerns), and check: once everything is captured, kill those sessions.

An open session isn't memory. If the work isn't done but doesn't need anyone right now, it becomes a spec or a concern in the repo's catalog (that's what [`/spec-workflow:new`](https://moacyrricardo.github.io/skills/spec-workflow-guide.html) does) and the session can die in peace. That's the backlog: a PM doesn't let an idea die just because nobody is working on it today, but doesn't keep 30 tabs open to remember it either. The "check" in the middle matters - only kill them after confirming everything was recorded.

Don't use /spec-workflow? No problem: swap it for managing your catalog in Linear or Jira. Ask it to create issues for what's still open, complete what's done and cancel what no longer makes sense - and only then kill the sessions.

### 4. The "brain" session

And one last one, for those who saw [Matt Pocock talking about a "brain" session](https://www.youtube.com/watch?v=hWe-j78vNpc) that orchestrates the others: in practice, it's this:

> Check the boletim and minhabufunfa repos: the way minhabufunfa tunnels connections to allow receipts from boletim to be viewed is bad. Let's use the new auth system and plan it with /spec-workflow:new. Open Claude sessions via herdr to act on each repo. First build the contract between them and turn it into a /rich-html:decide surface in /tmp, capturing: reusing the new auth, a circuit breaker, and frontend caching.

*([boletim](https://boletim.iskeru.com) and [minhabufunfa](https://minhabufunfa.iskeru.com) are two of my products that talk to each other)*

## Set the time aside and thank your PM

These prompts don't come out ready-made and probably won't work for you as they are: so invest a bit of time: try, fail and adjust until things hold up the way you'd like - adapted to **your** way of working. You already have the tools to learn how to study and tame this AI horse.

And then, really, go talk to your PM and thank them for having put up with your smart-aleck little face. Oh - Belzinha, my elementary-school English teacher: I fell off the horse, see? Thanks for the warning - and sorry for all the trouble I gave you.

## Try it

The skills in the prompts are open source: [moacyrricardo.github.io/skills](https://moacyrricardo.github.io/skills). Try them and give me some feedback :)
