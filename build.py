#!/usr/bin/env python3
"""Zero-dependency static-site generator for iskeru.com.

Edit the CONTENT/PRODUCTS data below once; running this script regenerates
both languages (English at /, Portuguese at /pt/) as plain static HTML.

    python3 build.py

No external dependencies — standard library only.
"""

import json
import os
import re
import shutil

SITE = "https://iskeru.com"
EMAIL = "contato@iskeru.com"
LINKEDIN = "https://www.linkedin.com/in/moacyrricardo"
GITHUB = "https://github.com/moacyrricardo"
OG_IMAGE = "/assets/og-image.png"  # 1200x630 social card (asset produced separately)
NBHY = "&#8209;"  # non-breaking hyphen, for "lineu-ai"
PERSON_NAME = "Moacyr Ricardo"

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
# Static source assets copied verbatim into dist/ (web root) alongside generated
# HTML. The whole assets/ directory is copied, so the 1200x630 social card at
# assets/og-image.png (referenced by og:image / twitter:image) ships automatically
# once the design asset is dropped in — see OG_IMAGE.
STATIC = ["assets", "favicon.svg", "robots.txt"]

LANGS = ["en", "pt"]
HTML_LANG = {"en": "en", "pt": "pt-BR"}
OG_LOCALE = {"en": "en_US", "pt": "pt_BR"}
LANG_LABEL = {"en": "EN", "pt": "PT"}

# page key -> URL path per language
ROUTES = {
    "home":     {"en": "/",          "pt": "/pt/"},
    "products": {"en": "/products/", "pt": "/pt/produtos/"},
    "about":    {"en": "/about/",    "pt": "/pt/sobre/"},
    # Intent-matched service pages (spec 002): each ranks for one commercial query.
    "fractional_cto": {"en": "/fractional-cto/",    "pt": "/pt/cto-fracional/"},
    "custom_dev":     {"en": "/custom-development/", "pt": "/pt/desenvolvimento/"},
    # The 404 is a single bilingual file served at the web root via nginx
    # error_page. There is no /pt/ variant, so both languages point at the same
    # absolute path — it is reachable at any depth, never via nav or sitemap.
    "notfound": {"en": "/404.html",  "pt": "/404.html"},
}

NAV = {
    "en": {"products": "Products", "company": "Company",
           "consulting": "Profile", "contact": "Contact",
           "fractional_cto": "Fractional CTO", "custom_dev": "Custom development"},
    "pt": {"products": "Produtos", "company": "Empresa",
           "consulting": "Perfil", "contact": "Contato",
           "fractional_cto": "CTO Fracional", "custom_dev": "Desenvolvimento"},
}

BADGE = {"live": {"en": "Live", "pt": "No ar"},
         "soon": {"en": "Coming soon", "pt": "Em breve"}}

CATEGORIES = ["finance", "events", "buildings"]
CAT_NAME = {
    "finance":   {"en": "Finance", "pt": "Finanças"},
    "events":    {"en": "Events", "pt": "Eventos"},
    "buildings": {"en": "Buildings & condos", "pt": "Condomínios"},
}
CAT_TAG = {
    "finance":   {"en": "Organize, automate and understand your money",
                  "pt": "Organização, automação e finanças pessoais"},
    "events":    {"en": "Invitations & confirmation of attendance",
                  "pt": "Convites & confirmação de presença"},
    "buildings": {"en": "Building management over WhatsApp",
                  "pt": "Gestão predial pelo WhatsApp"},
}

PRODUCTS = [
    {
        "slug": "boletim", "cat": "finance", "status": "live",
        "name": "boletim", "icon": "file-text", "link": "https://boletim.iskeru.com",
        "en": {
            "tag": "Financial automation & organization",
            "short": "Reads and organizes statements, boletos and receipts — built for Brazilian banks.",
            "desc": "iskeru's financial automation engine. It reads and organizes bank and credit-card statements, boletos, notifications and receipts — with parsing aware of Brazilian bank layouts (Itaú, Bradesco, Nubank, Inter and others), recognizing TED/DOC origins, Pix keys and tax codes. It also helps split bills and connects the services you already use.",
            "features": ["Bank and credit-card statements", "Boletos, notifications and receipts",
                         "Bill splitting and allocation rules", "Integrations (ContaAzul, Splitwise, Google and more)"],
            "cta": "Visit boletim.iskeru.com",
        },
        "pt": {
            "tag": "Automação &amp; organização financeira",
            "short": "Lê e organiza extratos, boletos e recibos — feito para os bancos brasileiros.",
            "desc": "O motor de automação financeira da iskeru. Lê e organiza extratos bancários e de cartão, boletos, notificações e recibos — com parsing ciente dos layouts dos bancos brasileiros (Itaú, Bradesco, Nubank, Inter e outros), reconhecendo origens TED/DOC, chaves Pix e códigos fiscais. Também ajuda a dividir contas e conecta os serviços que você já usa.",
            "features": ["Extratos bancários e de cartão", "Boletos, notificações e recibos",
                         "Divisão de contas e regras de rateio", "Integrações (ContaAzul, Splitwise, Google e mais)"],
            "cta": "Acessar boletim.iskeru.com",
        },
    },
    {
        "slug": "minhabufunfa", "cat": "finance", "status": "live",
        "name": "minhabufunfa", "icon": "wallet", "link": "https://minhabufunfa.iskeru.com",
        "en": {
            "tag": "Personal finance",
            "short": "Track transactions, accounts and budgets for everyday personal finance.",
            "desc": "Personal finance for everyday life. Record transactions, track accounts, budgets and payments, and get a clear view of where your money goes — simple and direct.",
            "features": ["Income and expense entries", "Accounts and budgets",
                         "Payment tracking", "A consolidated view of your finances"],
            "cta": "Visit minhabufunfa.iskeru.com",
        },
        "pt": {
            "tag": "Finanças pessoais",
            "short": "Acompanhe lançamentos, contas e orçamentos no dia a dia.",
            "desc": "Controle de finanças pessoais para o dia a dia. Registre lançamentos, acompanhe contas, orçamentos e pagamentos e tenha uma visão clara de para onde vai o seu dinheiro — simples e direto.",
            "features": ["Lançamentos de receitas e despesas", "Contas e orçamentos",
                         "Acompanhamento de pagamentos", "Visão consolidada das finanças"],
            "cta": "Acessar minhabufunfa.iskeru.com",
        },
    },
    {
        "slug": "lineu-ai", "cat": "finance", "status": "soon",
        "name": "lineu" + NBHY + "ai", "icon": "sparkles",
        "en": {
            "tag": "AI financial automation",
            "short": "Turns messy statements into organized spreadsheet data — no manual entry.",
            "desc": "The bridge between messy bank data and professional financial analysis. lineu" + NBHY + "ai turns statements (PDF, CSV, OFX) and email attachments into organized, categorized data delivered straight to Google Sheets or your cloud storage — no manual data entry. Aimed at financial consultants and spreadsheet power-users, it makes boletim's automation available as a self-serve SaaS.",
            "features": ["Statements in PDF, CSV and OFX become structured data", "Automatic categorization",
                         "Delivered straight to Google Sheets / cloud", "Gmail integration to capture attachments"],
            "note": "In development — coming soon at lineu" + NBHY + "ai.iskeru.com.",
        },
        "pt": {
            "tag": "Automação financeira com IA",
            "short": "Transforma extratos bagunçados em dados organizados na planilha — sem digitação.",
            "desc": "A ponte entre extratos bancários bagunçados e a análise financeira profissional. O lineu" + NBHY + "ai transforma extratos (PDF, CSV, OFX) e anexos de e-mail em dados organizados e categorizados, entregues direto no Google Sheets ou no seu armazenamento na nuvem — sem digitação manual. Voltado a consultores financeiros e quem vive de planilhas, é o produto que torna a automação do boletim acessível como um SaaS self-service.",
            "features": ["Extratos em PDF, CSV e OFX viram dados estruturados", "Categorização automática",
                         "Entrega direta no Google Sheets / nuvem", "Integração com Gmail para captura de anexos"],
            "note": "Em desenvolvimento — em breve em lineu" + NBHY + "ai.iskeru.com.",
        },
    },
    {
        "slug": "cevem", "cat": "events", "status": "live",
        "name": "cevem", "icon": "calendar", "link": "https://cevem.iskeru.com",
        "en": {
            "tag": "Invitations & RSVP",
            "short": "Invites, RSVPs and Pix contributions for your event — in one place.",
            "desc": "Create the page for your birthday or event, send the invite and collect RSVPs in one place. Public event page, guest list, host controls and contributions via Pix — no spreadsheet, no message group.",
            "features": ["A public page per event", "Guest RSVP",
                         "Contributions via Pix", "Google login for the host"],
            "cta": "Visit cevem.iskeru.com",
        },
        "pt": {
            "tag": "Convites &amp; confirmação de presença",
            "short": "Convites, RSVP e contribuições via Pix para seu evento — num só lugar.",
            "desc": "Crie a página do seu aniversário ou evento, envie o convite e receba as confirmações de presença (RSVP) em um só lugar. Página pública do evento, lista de convidados, controle do anfitrião e contribuições via Pix — tudo sem planilha e sem grupo de mensagens.",
            "features": ["Página pública por evento", "Confirmação de presença dos convidados",
                         "Contribuições via Pix", "Login com Google para o anfitrião"],
            "cta": "Acessar cevem.iskeru.com",
        },
    },
    {
        "slug": "pacdoorman", "cat": "buildings", "status": "soon",
        "name": "pacdoorman", "icon": "package",
        "cta_href": "mailto:" + EMAIL + "?subject=pacdoorman",
        "en": {
            "tag": "Package management over WhatsApp",
            "short": "Building package management entirely over WhatsApp, powered by AI.",
            "desc": "Package management for residential buildings entirely over WhatsApp, powered by AI. The doorman photographs the package label, the AI reads it and identifies the apartment, and the resident is notified automatically — pickup is confirmed with a 6-digit code. Building managers register residents by message or bulk import. Doorman, manager and resident interact only through WhatsApp, with no app to install.",
            "features": ["Package registration by photo, read by AI", "Automatic resident notification",
                         "Pickup by 6-digit code or by name", "Resident registration by message or CSV",
                         "All over WhatsApp — no app to install"],
            "note": "In development — coming soon.",
            "cta": "I'm interested",
        },
        "pt": {
            "tag": "Gestão de encomendas pelo WhatsApp",
            "short": "Gestão de encomendas do prédio inteiramente pelo WhatsApp, com IA.",
            "desc": "Gestão de encomendas para prédios residenciais inteiramente pelo WhatsApp, com inteligência artificial. O porteiro fotografa a etiqueta da encomenda, a IA lê os dados e identifica o apartamento, e o morador é avisado automaticamente — a retirada é confirmada por um código de 6 dígitos. Síndicos cadastram moradores por mensagem ou importação em massa. Porteiro, síndico e morador interagem só pelo WhatsApp, sem app para instalar.",
            "features": ["Registro de encomendas por foto, com leitura por IA", "Notificação automática ao morador",
                         "Retirada por código de 6 dígitos ou por nome", "Cadastro de moradores por mensagem ou CSV",
                         "Tudo pelo WhatsApp — sem app para instalar"],
            "note": "Em desenvolvimento — novidades em breve.",
            "cta": "Tenho interesse",
        },
    },
]

# Development capabilities (the "what I work with" grid on the profile)
CAPABILITIES = [
    {"icon": "cpu",
     "en": ("AI services", "LLM-powered features, extraction and automation."),
     "pt": ("Serviços de IA", "Recursos, extração e automação com LLMs.")},
    {"icon": "plug",
     "en": ("Integrations", "Connecting banks, gateways and third-party APIs."),
     "pt": ("Integrações", "Conexão com bancos, gateways e APIs de terceiros.")},
    {"icon": "filter",
     "en": ("Extraction pipelines", "Turning PDFs, statements and documents into structured data."),
     "pt": ("Pipelines de extração", "Transformando PDFs, extratos e documentos em dados estruturados.")},
    {"icon": "credit-card",
     "en": ("Payment providers", "Pix, boletos and checkout flows (AbacatePay, Mercado Pago)."),
     "pt": ("Meios de pagamento", "Pix, boletos e fluxos de checkout (AbacatePay, Mercado Pago).")},
    {"icon": "shield",
     "en": ("Security & auth", "Authentication, secrets handling and audit trails."),
     "pt": ("Segurança & autenticação", "Autenticação, gestão de segredos e trilhas de auditoria.")},
    {"icon": "layers",
     "en": ("Architecture", "Scalable, well-structured backends and clean domains."),
     "pt": ("Arquitetura", "Backends escaláveis, bem estruturados e domínios limpos.")},
]

# Experience timeline
# Leadership & team-building proof — the people axis (separate from tech capabilities)
STATS = [
    {"num": "200+", "en": "engineers hired", "pt": "engenheiros contratados"},
    {"num": "400+", "en": "interviewed", "pt": "entrevistados"},
    {"num": "15+", "en": "teams supported", "pt": "times apoiados"},
]

LEADERSHIP = [
    {"icon": "user-plus",
     "en": "Helped build and scale engineering hiring at QuintoAndar.",
     "pt": "Ajudei a construir e escalar a contratação de engenharia na QuintoAndar."},
    {"icon": "trending-up",
     "en": "Hired interns and new grads who grew into directors.",
     "pt": "Contratei estagiários e recém-formados que cresceram até diretores."},
    {"icon": "trending-up",
     "en": "Mentored junior engineers who are now senior and principal.",
     "pt": "Mentorei engenheiros juniores que hoje são seniores e principais."},
    {"icon": "users",
     "en": "Coached experienced engineers into engineering leaders.",
     "pt": "Fiz coaching de engenheiros experientes que viraram líderes de engenharia."},
]

TIMELINE = [
    {"org": "Advisory & Fractional CTO", "period": {"en": "Ongoing", "pt": "Em andamento"},
     "en": ("Advisor to companies & startups",
            "Fractional CTO and advisory — technology, architecture and product decisions."),
     "pt": ("Advisor de empresas e startups",
            "CTO fracional e advisory — decisões de tecnologia, arquitetura e produto.")},
    {"org": "QuintoAndar", "period": {"en": "2013 – 2025", "pt": "2013 – 2025"},
     "en": ("Founding team · Director · Principal Engineer",
            "One of the first engineers at one of Latin America's largest proptechs; helped scale engineering to 15+ teams and 200+ services."),
     "pt": ("Time fundador · Diretor · Principal Engineer",
            "Um dos primeiros engenheiros em uma das maiores proptechs da América Latina; ajudei a escalar a engenharia para 15+ times e 200+ serviços.")},
]

# Selected public GitHub projects (curated; ordered by most recently updated)
GITHUB_PROJECTS = [
    {"name": "docusign-cli", "icon": "file-text", "lang": "Java",
     "url": "https://github.com/moacyrricardo/docusign-cli",
     "en": "Command-line client for DocuSign, in Java.",
     "pt": "Cliente de linha de comando para o DocuSign, em Java."},
    {"name": "java-pix", "icon": "credit-card", "lang": "Java",
     "url": "https://github.com/moacyrricardo/java-pix",
     "en": "Java library to build Brazil's PIX copia-e-cola and static QR codes.",
     "pt": "Biblioteca Java para gerar PIX copia-e-cola e QR Code estático."},
    {"name": "splitwise-jax-rs", "icon": "plug", "lang": "Java",
     "url": "https://github.com/moacyrricardo/splitwise-jax-rs",
     "en": "JAX-RS interfaces for the Splitwise API.",
     "pt": "Interfaces JAX-RS para a API do Splitwise."},
    {"name": "maven-slack", "icon": "code", "lang": "Java",
     "url": "https://github.com/moacyrricardo/maven-slack",
     "en": "Maven plugin for Slack integration.",
     "pt": "Plugin Maven para integração com o Slack."},
]

# Per-page copy (everything that isn't product data)
T = {
    "en": {
        "footer_note": "Digital products that simplify everyday life.",
        "skip": "Skip to content",
        # home
        "home_title": "iskeru — digital products that simplify everyday life",
        "home_desc": "iskeru builds focused digital products: cevem (invites & RSVP), boletim & minhabufunfa (finance), lineu-ai and pacdoorman (coming soon).",
        "hero_h1": "Digital products that simplify everyday life.",
        "hero_lede": "We build focused web tools — no noise, no clutter — each solving one real problem well. See what's live and what's on the way.",
        "btn_products": "See products",
        "btn_about": "About iskeru",
        "products_title": "Our products",
        "products_sub": "Independent tools, each at its own address.",
        "learn_more": "Learn more",
        "teaser_title": "Work with me",
        "teaser_sub": "Beyond the products, I take on fractional-CTO, advisory and engineering-leadership work — and I've hired and grown a lot of engineers.",
        "view_profile": "View full profile",
        "company_title": "iskeru",
        "company_p1": "iskeru is where I build and ship independent products. I believe in lean software — tools that do one thing well, easy to understand and quick to use — each with its own address, focus and pace.",
        "company_p2": "The products serve a Brazilian audience, with native support for Pix, boletos and everyday services. There's always something new in the works — lineu-ai is next.",
        "company_p3_pre": "iskeru is me — ",
        "company_p3_mid": ", Principal Engineer and ex-QuintoAndar (founding team), now building products and working as a fractional CTO and advisor.",
        "contact_title": "Contact",
        "contact_text": "Want to talk, ask a question or propose a partnership? Email ",
        # products
        "products_page_title": "Products — iskeru",
        "products_page_desc": "All iskeru products by area: Finance (boletim, minhabufunfa, lineu-ai), Events (cevem) and Buildings (pacdoorman).",
        "products_eyebrow": "Products",
        "products_h1": "Focused tools, organized by area.",
        "products_lede": "iskeru builds independent products — some live, some on the way. Browse them by area below.",
        # about
        "about_title": "Moacyr Ricardo — Principal Engineer, Fractional CTO & Advisor",
        "about_desc": "Moacyr Ricardo — Principal Engineer, Fractional CTO and advisor. Founding-team, Director & Principal Engineer at QuintoAndar. 18 years building software.",
        "about_eyebrow": "Profile",
        "about_lede": "18 years building software — from one-man-team to leading 15+ teams and 200+ services. I advise companies and startups and build my own products, with a focus on AI services.",
        "bg_title": "Background",
        "bg_p1": "I've worked in software engineering for years, building production systems end to end — from backend to the final user experience. I was on the <strong>founding team at QuintoAndar</strong>, one of Latin America's largest proptechs, where I served as <strong>Director and Principal Engineer</strong>, working at scale with product and engineering teams to solve real problems for thousands of people.",
        "bg_p2_pre": "I work as an <strong>advisor to several companies and startups</strong>, helping teams make good technology, architecture and product decisions. In parallel, at ",
        "bg_p2_post": ", I apply that experience to build my own products: cevem (invitations and RSVP), boletim (financial organization), minhabufunfa (personal finance) and, soon, lineu-ai.",
        "help_title": "How I can help",
        "help_intro": "I work with companies and startups in flexible formats — from pointed advisory to full custom projects, end to end.",
        "help_list": [
            "<strong>Fractional CTO</strong> — engineering leadership, hiring and team building, and technical direction, part-time.",
            "<strong>Advisory</strong> — ongoing support to founders and teams on technology, architecture and product.",
            "<strong>Custom development</strong> — complete solutions end to end, with a focus on <strong>AI services</strong> and integrations.",
        ],
        "help_cta": "Want to talk about a project? ",
        "find_title": "Where to find me",
        "headline": "Principal Engineer · Fractional CTO & Advisor · Founding team, ex-QuintoAndar",
        "open_chip": "Open to advisory & collaboration",
        "lead_title": "Leadership & team building",
        "lead_sub": "Scaling engineering means scaling people — I hire, grow and coach engineers, and the leaders who run their teams.",
        "cap_title": "Capabilities",
        "cap_sub": "What I build with — the areas I go deep in.",
        "exp_title": "Experience",
        "work_title": "Selected work",
        "work_sub": "Products I've designed and built at iskeru.",
        "oss_title": "Open source",
        "oss_sub": "A few public projects — building blocks behind the products.",
        "oss_all": "See all projects on GitHub",
        "view_gh": "View on GitHub",
        # fractional CTO service page
        "fcto_title": "Fractional CTO for Hire — Engineering Leadership On Demand | iskeru",
        "fcto_desc": "Fractional CTO for hire: part-time engineering leadership, hiring and technical direction from a founding-team Principal Engineer. Advisory too.",
        "fcto_eyebrow": "Fractional CTO",
        "fcto_h1": "Fractional CTO for hire",
        "fcto_lede": "Part-time engineering leadership for startups and companies that need senior technical direction without a full-time hire. I set architecture, build and grow teams, and keep delivery on track.",
        "fcto_what_title": "What a fractional CTO does for you",
        "fcto_what_p": "As your fractional CTO I own the technical direction: architecture and roadmap decisions, hiring and team building, code and delivery quality, and the hard build-vs-buy and AI calls — engineering leadership on demand, scaled to what you actually need.",
        "fcto_proof_title": "Leadership proof, not just a title",
        "fcto_proof_p": "I was on the founding team at QuintoAndar, one of Latin America's largest proptechs, as Director and Principal Engineer — helping scale engineering to 15+ teams and 200+ services, and hiring and growing the people who run them.",
        "fcto_cta": "Talk about a fractional CTO engagement",
        "fcto_faq": [
            {"q": "How much does a fractional CTO cost?",
             "a": "A fractional CTO is paid for part-time involvement — typically a monthly retainer scoped to a set number of days per month — so you get senior engineering leadership at a fraction of a full-time CTO salary. Scope and rate are agreed up front based on the days you need; email contato@iskeru.com for a quote."},
            {"q": "What is the difference between a fractional CTO and an advisor?",
             "a": "An advisor gives periodic guidance; a fractional CTO is accountable for execution. As your fractional CTO I make and own technical decisions, lead hiring, and drive delivery — part-time but hands-on — rather than only reviewing from the outside."},
            {"q": "When should a startup hire a fractional CTO?",
             "a": "When you need senior technical direction — architecture, hiring, delivery — but cannot yet justify or fill a full-time CTO role. It is ideal for early-stage startups, non-technical founders, and teams between technical leaders."},
            {"q": "What does a fractional CTO engagement include?",
             "a": "Typically: technical strategy and architecture, the engineering hiring plan and interviews, delivery oversight, and decisions on tooling, AI and build-vs-buy. The exact scope is tailored to your stage and reviewed as you grow."},
        ],
        # custom development service page
        "cdev_title": "Custom Software & Project Development (AI-focused) | iskeru",
        "cdev_desc": "Custom software and project development, end to end — AI services, integrations and extraction pipelines built by a Principal Engineer. Get a quote.",
        "cdev_eyebrow": "Custom development",
        "cdev_h1": "Custom project development",
        "cdev_lede": "End-to-end custom software development for companies and startups — from a scoped project to a long-running build — with a focus on AI services, integrations and turning messy data into structured systems.",
        "cdev_what_title": "Custom software development, end to end",
        "cdev_what_p": "I take projects from idea to production: backend, integrations and the final user experience. The focus is AI services — LLM-powered features, extraction pipelines that turn PDFs and statements into structured data — plus payment flows (Pix, boletos) and third-party API integrations.",
        "cdev_proof_title": "Built and shipped, not just specced",
        "cdev_proof_p": "I build my own products at iskeru — boletim, minhabufunfa, cevem and lineu-ai — on top of 18 years shipping production systems and founding-team experience at QuintoAndar. Custom projects get the same end-to-end engineering.",
        "cdev_cta": "Scope a custom development project",
        "cdev_faq": [
            {"q": "How do you scope a custom software project?",
             "a": "We start with a short discovery to pin down the problem, the must-have outcomes and the constraints, then I propose a phased plan with a clear first milestone. Scoping is deliberately small at first so we validate direction before committing to a full build."},
            {"q": "Do you build AI and LLM-powered features?",
             "a": "Yes — AI services are the core focus: LLM-powered features, document and statement extraction pipelines, and automation. I have shipped these in production (for example reading bank statements and boletos into structured data) rather than only prototyping them."},
            {"q": "Can you work with my existing team and codebase?",
             "a": "Yes. I can deliver a project end to end on my own or embed with your team — reviewing the codebase, setting up architecture and integrations, and leaving it maintainable. This pairs naturally with fractional-CTO engagements."},
            {"q": "What does a custom development project cost?",
             "a": "It depends on scope. Small, well-defined projects are quoted as a fixed phase; larger or evolving builds run on a time basis with milestones. After the discovery call you get a written scope and estimate — email contato@iskeru.com to start."},
        ],
        # 404
        "nf_title": "Page not found — iskeru",
        "nf_desc": "The page you were looking for doesn't exist. Head back to the iskeru home page or browse the products.",
        "nf_eyebrow": "404",
        "nf_h1": "This page doesn't exist.",
        "nf_lede": "The address you followed may be broken or the page may have moved. Try the home page or the products below.",
        "nf_home": "Go to home",
        "nf_products": "See products",
    },
    "pt": {
        "footer_note": "Produtos digitais que simplificam o dia a dia.",
        "skip": "Pular para o conteúdo",
        "home_title": "iskeru — produtos digitais que simplificam o dia a dia",
        "home_desc": "A iskeru cria produtos digitais focados: cevem (convites e RSVP), boletim e minhabufunfa (finanças), lineu-ai e pacdoorman (em breve).",
        "hero_h1": "Produtos digitais que simplificam o dia a dia.",
        "hero_lede": "Construímos ferramentas web focadas, sem ruído e sem complicação — cada uma resolvendo bem um problema real. Conheça o que já está no ar e o que está por vir.",
        "btn_products": "Ver produtos",
        "btn_about": "Sobre a iskeru",
        "products_title": "Nossos produtos",
        "products_sub": "Soluções independentes, cada uma no seu próprio endereço.",
        "learn_more": "Saiba mais",
        "teaser_title": "Trabalhe comigo",
        "teaser_sub": "Além dos produtos, atuo como CTO fracional, advisor e em liderança de engenharia — e já contratei e desenvolvi muitos engenheiros.",
        "view_profile": "Ver perfil completo",
        "company_title": "A iskeru",
        "company_p1": "A iskeru é onde eu construo e lanço produtos digitais independentes. Acredito em software enxuto — ferramentas que fazem uma coisa bem feita, fáceis de entender e rápidas de usar — cada uma com seu próprio endereço, foco e ritmo.",
        "company_p2": "Os produtos atendem o público brasileiro, com suporte nativo a Pix, boletos e aos serviços do dia a dia. Tem sempre algo novo a caminho — o lineu-ai é o próximo.",
        "company_p3_pre": "A iskeru sou eu — ",
        "company_p3_mid": ", Principal Engineer e ex-QuintoAndar (time fundador), hoje criando produtos e atuando como CTO fracional e advisor.",
        "contact_title": "Contato",
        "contact_text": "Quer falar com a gente, tirar uma dúvida ou propor uma parceria? Escreva para ",
        "products_page_title": "Produtos — iskeru",
        "products_page_desc": "Todos os produtos da iskeru por área: Finanças (boletim, minhabufunfa, lineu-ai), Eventos (cevem) e Condomínios (pacdoorman).",
        "products_eyebrow": "Produtos",
        "products_h1": "Ferramentas focadas, organizadas por área.",
        "products_lede": "A iskeru constrói produtos independentes — alguns já no ar, outros a caminho. Conheça-os por área abaixo.",
        "about_title": "Moacyr Ricardo — Principal Engineer, CTO Fracional e Advisor",
        "about_desc": "Moacyr Ricardo — Principal Engineer, CTO Fracional e advisor. Time fundador, Diretor e Principal Engineer na QuintoAndar. 18 anos construindo software.",
        "about_eyebrow": "Perfil",
        "about_lede": "18 anos construindo software — de one-man-team a liderar 15+ times e 200+ serviços. Assessoro empresas e startups e crio meus próprios produtos, com foco em serviços de IA.",
        "bg_title": "Trajetória",
        "bg_p1": "Atuo com engenharia de software há anos, construindo sistemas de produção de ponta a ponta — do backend à experiência final do usuário. Fiz parte do <strong>time fundador da QuintoAndar</strong>, uma das maiores proptechs da América Latina, onde atuei como <strong>Diretor e Principal Engineer</strong>, trabalhando em escala com times de produto e engenharia para resolver problemas reais de milhares de pessoas.",
        "bg_p2_pre": "Atuo como <strong>advisor de várias empresas e startups</strong>, ajudando times a tomar boas decisões de tecnologia, arquitetura e produto. Em paralelo, na ",
        "bg_p2_post": ", aplico essa experiência para criar produtos próprios: o cevem (convites e RSVP), o boletim (organização financeira), o minhabufunfa (finanças pessoais) e, em breve, o lineu-ai.",
        "help_title": "Como posso ajudar",
        "help_intro": "Trabalho com empresas e startups em formatos flexíveis — de advisory pontual a projetos sob medida de ponta a ponta.",
        "help_list": [
            "<strong>CTO Fracional</strong> — liderança de engenharia, contratação e formação de times, e direção técnica, em meio período.",
            "<strong>Advisory</strong> — apoio contínuo a fundadores e times em tecnologia, arquitetura e produto.",
            "<strong>Desenvolvimento sob medida</strong> — soluções completas de ponta a ponta, com foco em <strong>serviços de IA</strong> e integrações.",
        ],
        "help_cta": "Quer conversar sobre um projeto? ",
        "find_title": "Onde me encontrar",
        "headline": "Principal Engineer · CTO Fracional & Advisor · Time fundador, ex-QuintoAndar",
        "open_chip": "Aberto a advisory e colaborações",
        "lead_title": "Liderança & formação de times",
        "lead_sub": "Escalar engenharia é escalar pessoas — eu contrato, desenvolvo e faço coaching de engenheiros e dos líderes que tocam os times.",
        "cap_title": "Capacidades",
        "cap_sub": "Com o que eu construo — as áreas em que vou fundo.",
        "exp_title": "Experiência",
        "work_title": "Trabalhos selecionados",
        "work_sub": "Produtos que desenhei e construí na iskeru.",
        "oss_title": "Código aberto",
        "oss_sub": "Alguns projetos públicos — peças por trás dos produtos.",
        "oss_all": "Ver todos os projetos no GitHub",
        "view_gh": "Ver no GitHub",
        # fractional CTO service page
        "fcto_title": "CTO Fracional — Liderança de Engenharia Sob Demanda | iskeru",
        "fcto_desc": "CTO Fracional: liderança de engenharia, contratação e direção técnica em meio período, com um Principal Engineer de time fundador. Advisory também.",
        "fcto_eyebrow": "CTO Fracional",
        "fcto_h1": "CTO Fracional",
        "fcto_lede": "Liderança de engenharia em meio período para startups e empresas que precisam de direção técnica sênior sem uma contratação full-time. Defino arquitetura, formo e desenvolvo times e mantenho a entrega no rumo.",
        "fcto_what_title": "O que um CTO fracional faz por você",
        "fcto_what_p": "Como seu CTO fracional eu assumo a direção técnica: decisões de arquitetura e roadmap, contratação e formação de time, qualidade de código e de entrega, e as decisões difíceis de build-vs-buy e de IA — liderança de engenharia sob demanda, no tamanho que você realmente precisa.",
        "fcto_proof_title": "Liderança comprovada, não só um título",
        "fcto_proof_p": "Fiz parte do time fundador da QuintoAndar, uma das maiores proptechs da América Latina, como Diretor e Principal Engineer — ajudando a escalar a engenharia para 15+ times e 200+ serviços, e contratando e desenvolvendo as pessoas que tocam esses times.",
        "fcto_cta": "Conversar sobre um trabalho de CTO fracional",
        "fcto_faq": [
            {"q": "Quanto custa um CTO fracional?",
             "a": "Um CTO fracional é remunerado pela atuação em meio período — em geral um valor mensal dimensionado por uma quantidade de dias por mês — então você tem liderança de engenharia sênior por uma fração do salário de um CTO full-time. Escopo e valor são combinados antes, conforme os dias necessários; escreva para contato@iskeru.com para um orçamento."},
            {"q": "Qual a diferença entre um CTO fracional e um advisor?",
             "a": "Um advisor dá orientação pontual; um CTO fracional é responsável pela execução. Como seu CTO fracional eu tomo e assumo as decisões técnicas, lidero a contratação e conduzo a entrega — em meio período, mas mão na massa — e não apenas reviso de fora."},
            {"q": "Quando uma startup deve contratar um CTO fracional?",
             "a": "Quando precisa de direção técnica sênior — arquitetura, contratação, entrega — mas ainda não justifica ou não consegue preencher um CTO full-time. É ideal para startups em estágio inicial, fundadores não técnicos e times entre líderes técnicos."},
            {"q": "O que está incluído em um trabalho de CTO fracional?",
             "a": "Em geral: estratégia técnica e arquitetura, plano de contratação de engenharia e entrevistas, acompanhamento de entrega e decisões sobre ferramentas, IA e build-vs-buy. O escopo exato é ajustado ao seu estágio e revisado conforme você cresce."},
        ],
        # custom development service page
        "cdev_title": "Desenvolvimento de Software e Projetos Sob Medida (foco em IA) | iskeru",
        "cdev_desc": "Desenvolvimento de software e projetos sob medida, ponta a ponta — serviços de IA, integrações e pipelines de extração, por um Principal Engineer.",
        "cdev_eyebrow": "Desenvolvimento",
        "cdev_h1": "Desenvolvimento de projetos sob medida",
        "cdev_lede": "Desenvolvimento de software sob medida, de ponta a ponta, para empresas e startups — de um projeto pontual a um build de longo prazo — com foco em serviços de IA, integrações e em transformar dados bagunçados em sistemas estruturados.",
        "cdev_what_title": "Desenvolvimento de software sob medida, ponta a ponta",
        "cdev_what_p": "Levo projetos da ideia à produção: backend, integrações e a experiência final do usuário. O foco são serviços de IA — recursos com LLMs, pipelines de extração que transformam PDFs e extratos em dados estruturados — além de fluxos de pagamento (Pix, boletos) e integrações com APIs de terceiros.",
        "cdev_proof_title": "Construído e lançado, não só especificado",
        "cdev_proof_p": "Construo meus próprios produtos na iskeru — boletim, minhabufunfa, cevem e lineu-ai — sobre 18 anos lançando sistemas de produção e a experiência de time fundador na QuintoAndar. Projetos sob medida recebem a mesma engenharia de ponta a ponta.",
        "cdev_cta": "Especificar um projeto de desenvolvimento sob medida",
        "cdev_faq": [
            {"q": "Como você define o escopo de um projeto sob medida?",
             "a": "Começamos com uma descoberta curta para delimitar o problema, os resultados essenciais e as restrições; então proponho um plano em fases com um primeiro marco claro. O escopo inicial é propositalmente pequeno, para validar a direção antes de comprometer um build completo."},
            {"q": "Você desenvolve recursos com IA e LLMs?",
             "a": "Sim — serviços de IA são o foco principal: recursos com LLMs, pipelines de extração de documentos e extratos, e automação. Já coloquei isso em produção (por exemplo, lendo extratos bancários e boletos em dados estruturados), e não apenas em protótipo."},
            {"q": "Você trabalha com meu time e código existentes?",
             "a": "Sim. Posso entregar um projeto de ponta a ponta sozinho ou me integrar ao seu time — revisando o código, definindo arquitetura e integrações e deixando tudo sustentável. Isso combina naturalmente com trabalhos de CTO fracional."},
            {"q": "Quanto custa um projeto de desenvolvimento sob medida?",
             "a": "Depende do escopo. Projetos pequenos e bem definidos são orçados como uma fase de valor fechado; builds maiores ou em evolução rodam por tempo com marcos. Após a conversa de descoberta você recebe um escopo e estimativa por escrito — escreva para contato@iskeru.com para começar."},
        ],
        # 404
        "nf_title": "Página não encontrada — iskeru",
        "nf_desc": "A página que você procurava não existe. Volte para a página inicial da iskeru ou conheça os produtos.",
        "nf_eyebrow": "404",
        "nf_h1": "Esta página não existe.",
        "nf_lede": "O endereço que você acessou pode estar quebrado ou a página pode ter mudado de lugar. Tente a página inicial ou os produtos abaixo.",
        "nf_home": "Ir para o início",
        "nf_products": "Ver produtos",
    },
}


# ----------------------------------------------------------------------------
# Icons (inline SVG, Lucide-style line icons + brand fills; MIT-licensed art)
# ----------------------------------------------------------------------------

CAT_ICON = {"finance": "banknote", "events": "calendar", "buildings": "building"}
HELP_ICONS = ["users", "compass", "code"]

ICONS = {
    "check": ("line", '<polyline points="20 6 9 17 4 12"/>'),
    "arrow-right": ("line", '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>'),
    "menu": ("line", '<line x1="4" y1="6" x2="20" y2="6"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="18" x2="20" y2="18"/>'),
    "file-text": ("line", '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>'),
    "wallet": ("line", '<path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4Z"/>'),
    "sparkles": ("line", '<path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>'),
    "calendar": ("line", '<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>'),
    "package": ("line", '<path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="M3.3 7 12 12l8.7-5"/><path d="M12 22V12"/>'),
    "banknote": ("line", '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01"/><path d="M18 12h.01"/>'),
    "building": ("line", '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/>'),
    "compass": ("line", '<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>'),
    "search": ("line", '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>'),
    "code": ("line", '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>'),
    "mail": ("line", '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 5L2 7"/>'),
    "cpu": ("line", '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 2v2"/><path d="M15 2v2"/><path d="M9 20v2"/><path d="M15 20v2"/><path d="M2 9h2"/><path d="M2 15h2"/><path d="M20 9h2"/><path d="M20 15h2"/>'),
    "plug": ("line", '<path d="M12 22v-5"/><path d="M9 8V2"/><path d="M15 8V2"/><path d="M18 8v5a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4V8Z"/>'),
    "filter": ("line", '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>'),
    "credit-card": ("line", '<rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/>'),
    "shield": ("line", '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'),
    "layers": ("line", '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>'),
    "users": ("line", '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>'),
    "user-plus": ("line", '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/>'),
    "trending-up": ("line", '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>'),
    "github": ("fill", '<path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>'),
    "linkedin": ("fill", '<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>'),
}


def icon(name, cls="icon"):
    kind, body = ICONS[name]
    if kind == "fill":
        return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="currentColor" '
                f'aria-hidden="true">{body}</svg>')
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{body}</svg>')


# ----------------------------------------------------------------------------
# Structured data (JSON-LD)
# ----------------------------------------------------------------------------
# Each page emits a site-wide Person plus, on the service pages, a Service node
# (provider -> the Person) and a FAQPage. Everything is serialized with
# json.dumps so quoting/escaping is correct by construction — never hand-built.

KNOWS_ABOUT = {
    "en": ["Software architecture", "Artificial intelligence", "LLM integrations",
           "Engineering leadership", "Fintech", "Payment systems", "Pix"],
    "pt": ["Arquitetura de software", "Inteligência artificial", "Integrações com LLMs",
           "Liderança de engenharia", "Fintech", "Sistemas de pagamento", "Pix"],
}

PERSON_ID = SITE + "/about/#person"


def person_ld(lang):
    """The site-wide Person node. Referenced by @id from Service providers."""
    job_title = ("Principal Engineer, Fractional CTO & Advisor" if lang == "en"
                 else "Principal Engineer, CTO Fracional e Advisor")
    return {
        "@type": "Person",
        "@id": PERSON_ID,
        "name": PERSON_NAME,
        "url": SITE + ROUTES["about"][lang],
        "jobTitle": job_title,
        "image": SITE + "/assets/moacyr.jpg",
        "sameAs": [LINKEDIN, GITHUB],
        "knowsAbout": KNOWS_ABOUT[lang],
        "worksFor": {"@type": "Organization", "name": "iskeru", "url": SITE},
    }


def service_ld(name, service_type, desc, url):
    """A ProfessionalService offered by the Person, for a service page."""
    return {
        "@type": "ProfessionalService",
        "name": name,
        "serviceType": service_type,
        "description": desc,
        "url": url,
        "provider": {"@id": PERSON_ID},
        "areaServed": [
            {"@type": "Country", "name": "Brazil"},
            {"@type": "AdministrativeArea", "name": "Remote / Worldwide"},
        ],
    }


def faq_ld(faqs):
    """A FAQPage node from a list of {q, a} dicts (eligible for FAQ rich results)."""
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f["q"],
             "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
            for f in faqs
        ],
    }


def ld_script(nodes):
    """Render one ld+json <script> wrapping the given nodes in an @graph.

    Drops any None entries so callers can pass optional nodes inline. Returns ""
    when there is nothing to emit. json.dumps handles all escaping."""
    graph = [n for n in nodes if n]
    if not graph:
        return ""
    doc = {"@context": "https://schema.org", "@graph": graph}
    payload = json.dumps(doc, ensure_ascii=False, indent=2)
    return f'  <script type="application/ld+json">\n{payload}\n  </script>\n'


# ----------------------------------------------------------------------------
# Rendering helpers
# ----------------------------------------------------------------------------

def head(lang, key, title, desc, ld=""):
    canonical = SITE + ROUTES[key][lang]
    en_url = SITE + ROUTES[key]["en"]
    pt_url = SITE + ROUTES[key]["pt"]
    og_image = SITE + OG_IMAGE
    return f"""<!DOCTYPE html>
<html lang="{HTML_LANG[lang]}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <link rel="canonical" href="{canonical}" />
  <link rel="alternate" hreflang="en" href="{en_url}" />
  <link rel="alternate" hreflang="pt-BR" href="{pt_url}" />
  <link rel="alternate" hreflang="x-default" href="{en_url}" />

  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="iskeru" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:locale" content="{OG_LOCALE[lang]}" />
  <meta property="og:image" content="{og_image}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="{og_image}" />

  <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/assets/styles.css" />
{ld}</head>
<body>
  <a class="skip-link" href="#main">{T[lang]['skip']}</a>
"""


def header(lang, key):
    home = ROUTES["home"][lang]
    nav = NAV[lang]
    switch = []
    for l in LANGS:
        cls = ' class="active"' if l == lang else ""
        switch.append(f'<a href="{ROUTES[key][l]}"{cls}>{LANG_LABEL[l]}</a>')
    switch_html = '<span class="lang-switch">' + "\n          ".join(switch) + "</span>"
    return f"""  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="{home}" aria-label="iskeru">
        <span class="brand-mark" aria-hidden="true"></span>
        <span class="brand-name">iskeru</span>
      </a>
      <button class="nav-toggle" aria-label="Menu" aria-expanded="false" aria-controls="site-nav">
        {icon('menu', 'icon')}
      </button>
      <nav id="site-nav" class="site-nav" aria-label="{nav['products']}">
        <a href="{ROUTES['products'][lang]}">{nav['products']}</a>
        <a href="{ROUTES['fractional_cto'][lang]}">{nav['fractional_cto']}</a>
        <a href="{ROUTES['custom_dev'][lang]}">{nav['custom_dev']}</a>
        <a href="{ROUTES['about'][lang]}">{nav['consulting']}</a>
        <a href="{home}#contact">{nav['contact']}</a>
        {switch_html}
      </nav>
    </div>
  </header>
"""


def footer(lang):
    nav = NAV[lang]
    home = ROUTES["home"][lang]
    return f"""  <footer class="site-footer">
    <div class="container footer-inner">
      <div>
        <span class="brand-name">iskeru</span>
        <p class="footer-note">{T[lang]['footer_note']}</p>
      </div>
      <nav class="footer-nav" aria-label="{nav['products']}">
        <a href="{ROUTES['products'][lang]}">{nav['products']}</a>
        <a href="{ROUTES['fractional_cto'][lang]}">{nav['fractional_cto']}</a>
        <a href="{ROUTES['custom_dev'][lang]}">{nav['custom_dev']}</a>
        <a href="{ROUTES['about'][lang]}">{nav['consulting']}</a>
        <a href="{home}#contact">{nav['contact']}</a>
      </nav>
      <p class="footer-copy">&copy; <span id="year">2026</span> iskeru</p>
    </div>
  </footer>

  <script>
    var y = document.getElementById('year');
    if (y) y.textContent = new Date().getFullYear();
    var tg = document.querySelector('.nav-toggle');
    var nv = document.getElementById('site-nav');
    if (tg && nv) {{
      tg.addEventListener('click', function () {{
        var open = nv.classList.toggle('open');
        tg.setAttribute('aria-expanded', open);
      }});
    }}
  </script>
</body>
</html>
"""


def page(lang, key, title, desc, body, ld=""):
    return head(lang, key, title, desc, ld) + header(lang, key) + body + footer(lang)


def badge(status, lang):
    cls = "badge-live" if status == "live" else "badge-soon"
    return f'<span class="badge {cls}">{BADGE[status][lang]}</span>'


def product_article(p, lang):
    c = p[lang]
    soon = p["status"] == "soon"
    cls = "product product-soon" if soon else "product"
    features = "\n".join(
        f'            <li>{icon("check", "feat-ic")}<span>{f}</span></li>' for f in c["features"])
    if soon:
        tail = f'          <p class="product-status">{c["note"]}</p>\n'
        if "cta" in c and "cta_href" in p:
            tail += (f'          <a class="btn btn-ghost" href="{p["cta_href"]}">'
                     f'{icon("mail")}<span>{c["cta"]}</span></a>\n')
    else:
        tail = (f'          <a class="btn btn-primary" href="{p["link"]}">'
                f'<span>{c["cta"]}</span>{icon("arrow-right")}</a>\n')
    return f"""        <article id="{p['slug']}" class="{cls}">
          <div class="product-head">
            <span class="ic-chip">{icon(p['icon'])}</span>
            <h2>{p['name']}</h2>
            {badge(p['status'], lang)}
          </div>
          <p class="product-tag">{c['tag']}</p>
          <p>{c['desc']}</p>
          <ul class="feature-list">
{features}
          </ul>
{tail}        </article>
"""


def home_card(p, lang):
    c = p[lang]
    href = ROUTES["products"][lang] + "#" + p["slug"]
    return f"""          <article class="card">
            <div class="card-head">
              <span class="ic-chip">{icon(p['icon'])}</span>
              <h3>{p['name']}</h3>
              {badge(p['status'], lang)}
            </div>
            <p class="card-tag">{c['tag']}</p>
            <p>{c['short']}</p>
            <a class="card-link" href="{href}"><span>{T[lang]['learn_more']}</span>{icon('arrow-right')}</a>
          </article>
"""


# ----------------------------------------------------------------------------
# Page bodies
# ----------------------------------------------------------------------------

def render_home(lang):
    t = T[lang]
    cards = "\n".join(home_card(p, lang) for p in PRODUCTS)
    stats = "\n".join(stat_item(s, lang) for s in STATS)
    pills = "".join(f'<span class="pill">{c[lang][0]}</span>' for c in CAPABILITIES)
    name_link = f'<a href="{ROUTES["about"][lang]}">Moacyr Ricardo</a>'
    body = f"""  <main id="main">
    <section class="hero">
      <div class="container">
        <p class="eyebrow">iskeru</p>
        <h1>{t['hero_h1']}</h1>
        <p class="lede">{t['hero_lede']}</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="{ROUTES['products'][lang]}">{t['btn_products']}</a>
          <a class="btn btn-ghost" href="#company">{t['btn_about']}</a>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <h2 class="section-title">{t['products_title']}</h2>
        <p class="section-sub">{t['products_sub']}</p>
        <div class="cards">
{cards}
        </div>
      </div>
    </section>

    <section id="company" class="section section-alt">
      <div class="container narrow">
        <h2 class="section-title">{t['company_title']}</h2>
        <p>{t['company_p1']}</p>
        <p>{t['company_p2']}</p>
        <p>{t['company_p3_pre']}{name_link}{t['company_p3_mid']}</p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <h2 class="section-title">{t['teaser_title']}</h2>
        <p class="section-sub">{t['teaser_sub']}</p>
        <div class="stats">
{stats}
        </div>
        <div class="pills">{pills}</div>
        <div class="hero-actions">
          <a class="btn btn-primary" href="{ROUTES['fractional_cto'][lang]}"><span>{NAV[lang]['fractional_cto']}</span>{icon('arrow-right')}</a>
          <a class="btn btn-primary" href="{ROUTES['custom_dev'][lang]}"><span>{NAV[lang]['custom_dev']}</span>{icon('arrow-right')}</a>
          <a class="btn btn-ghost" href="{ROUTES['about'][lang]}"><span>{t['view_profile']}</span>{icon('arrow-right')}</a>
        </div>
      </div>
    </section>

    <section id="contact" class="section">
      <div class="container narrow">
        <h2 class="section-title">{t['contact_title']}</h2>
        <p>{t['contact_text']}<a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
      </div>
    </section>
  </main>
"""
    return page(lang, "home", t["home_title"], t["home_desc"], body,
                ld=ld_script([person_ld(lang)]))


def render_products(lang):
    t = T[lang]
    sections = []
    for cat in CATEGORIES:
        arts = "\n".join(product_article(p, lang) for p in PRODUCTS if p["cat"] == cat)
        sections.append(f"""      <section id="{cat}" class="section">
        <div class="container">
          <h2 class="section-title cat-title">{icon(CAT_ICON[cat], 'cat-ic')}<span>{CAT_NAME[cat][lang]}</span></h2>
          <p class="section-sub">{CAT_TAG[cat][lang]}</p>
{arts}        </div>
      </section>""")
    body = f"""  <main id="main">
    <section class="hero">
      <div class="container">
        <p class="eyebrow">{t['products_eyebrow']}</p>
        <h1>{t['products_h1']}</h1>
        <p class="lede">{t['products_lede']}</p>
      </div>
    </section>

{chr(10).join(sections)}
  </main>
"""
    return page(lang, "products", t["products_page_title"], t["products_page_desc"], body,
                ld=ld_script([person_ld(lang)]))


def cap_card(c, lang):
    title, desc = c[lang]
    return f"""          <article class="card cap">
            <span class="ic-chip">{icon(c['icon'])}</span>
            <h3>{title}</h3>
            <p>{desc}</p>
          </article>
"""


def timeline_item(x, lang):
    role, desc = x[lang]
    return f"""        <li class="tl-item">
          <span class="tl-dot" aria-hidden="true"></span>
          <div class="tl-body">
            <div class="tl-head">
              <h3>{x['org']}</h3>
              <span class="tl-period">{x['period'][lang]}</span>
            </div>
            <p class="tl-role">{role}</p>
            <p>{desc}</p>
          </div>
        </li>"""


def oss_card(g, lang):
    return f"""          <article class="card">
            <div class="card-head">
              <span class="ic-chip">{icon(g['icon'])}</span>
              <h3>{g['name']}</h3>
              <span class="badge badge-count">{g['lang']}</span>
            </div>
            <p>{g[lang]}</p>
            <a class="card-link" href="{g['url']}" target="_blank" rel="noopener"><span>{T[lang]['view_gh']}</span>{icon('arrow-right')}</a>
          </article>
"""


def stat_item(s, lang):
    return (f'          <div class="stat"><span class="stat-num">{s["num"]}</span>'
            f'<span class="stat-label">{s[lang]}</span></div>')


def lead_item(x, lang):
    return f'          <li>{icon(x["icon"], "feat-ic")}<span>{x[lang]}</span></li>'


def render_about(lang):
    t = T[lang]
    stats = "\n".join(stat_item(s, lang) for s in STATS)
    leads = "\n".join(lead_item(x, lang) for x in LEADERSHIP)
    caps = "\n".join(cap_card(c, lang) for c in CAPABILITIES)
    timeline = "\n".join(timeline_item(x, lang) for x in TIMELINE)
    work = "\n".join(home_card(p, lang) for p in PRODUCTS)
    oss = "\n".join(oss_card(g, lang) for g in GITHUB_PROJECTS)
    help_items = "\n".join(
        f'          <li>{icon(HELP_ICONS[i], "feat-ic")}<span>{x}</span></li>'
        for i, x in enumerate(t["help_list"]))
    body = f"""  <main id="main">
    <section class="hero">
      <div class="container">
        <div class="profile-hero">
          <img class="avatar" src="/assets/moacyr.jpg" width="120" height="120" alt="Moacyr Ricardo" />
          <div class="profile-intro">
            <p class="eyebrow">{t['about_eyebrow']}</p>
            <h1>Moacyr Ricardo</h1>
            <p class="headline">{t['headline']}</p>
            <p class="lede">{t['about_lede']}</p>
            <div class="hero-actions">
              <a class="btn btn-primary" href="{LINKEDIN}" rel="me noopener" target="_blank">{icon('linkedin')}<span>LinkedIn</span></a>
              <a class="btn btn-ghost" href="{GITHUB}" rel="me noopener" target="_blank">{icon('github')}<span>GitHub</span></a>
            </div>
            <p class="status-chip">{t['open_chip']}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="section section-alt">
      <div class="container">
        <h2 class="section-title">{t['lead_title']}</h2>
        <p class="section-sub">{t['lead_sub']}</p>
        <div class="stats">
{stats}
        </div>
        <ul class="feature-list lead-list">
{leads}
        </ul>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <h2 class="section-title">{t['cap_title']}</h2>
        <p class="section-sub">{t['cap_sub']}</p>
        <div class="cards">
{caps}
        </div>
      </div>
    </section>

    <section class="section section-alt">
      <div class="container narrow">
        <h2 class="section-title">{t['exp_title']}</h2>
        <ul class="timeline">
{timeline}
        </ul>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <h2 class="section-title">{t['work_title']}</h2>
        <p class="section-sub">{t['work_sub']}</p>
        <div class="cards">
{work}
        </div>
      </div>
    </section>

    <section class="section section-alt">
      <div class="container">
        <h2 class="section-title cat-title">{icon('github', 'cat-ic')}<span>{t['oss_title']}</span></h2>
        <p class="section-sub">{t['oss_sub']}</p>
        <div class="cards">
{oss}
        </div>
        <p class="oss-all"><a class="card-link" href="{GITHUB}" target="_blank" rel="noopener"><span>{t['oss_all']}</span>{icon('arrow-right')}</a></p>
      </div>
    </section>

    <section class="section">
      <div class="container narrow">
        <h2 class="section-title">{t['help_title']}</h2>
        <p>{t['help_intro']}</p>
        <ul class="links-list">
{help_items}
        </ul>
        <p>{t['help_cta']}<a href="mailto:{EMAIL}">{EMAIL}</a>.</p>

        <h2 class="section-title" style="margin-top:48px;">{t['find_title']}</h2>
        <ul class="links-list links-list-icons">
          <li>{icon('linkedin', 'feat-ic')}<span><a href="{LINKEDIN}" rel="me noopener" target="_blank">LinkedIn</a> — linkedin.com/in/moacyrricardo</span></li>
          <li>{icon('github', 'feat-ic')}<span><a href="{GITHUB}" rel="me noopener" target="_blank">GitHub</a> — github.com/moacyrricardo</span></li>
          <li>{icon('mail', 'feat-ic')}<span><a href="mailto:{EMAIL}">{EMAIL}</a></span></li>
        </ul>
      </div>
    </section>
  </main>
"""
    return page(lang, "about", t["about_title"], t["about_desc"], body,
                ld=ld_script([person_ld(lang)]))


def faq_section(title, faqs):
    """Render an FAQ section from a list of {q, a} dicts using native <details>
    disclosure (no JS needed). The same data drives the FAQPage JSON-LD."""
    items = "\n".join(
        f"""          <details class="faq-item">
            <summary>{f['q']}</summary>
            <p>{f['a']}</p>
          </details>""" for f in faqs)
    return f"""    <section class="section section-alt">
      <div class="container narrow">
        <h2 class="section-title">{title}</h2>
        <div class="faq">
{items}
        </div>
      </div>
    </section>"""


def service_hero(eyebrow, h1, lede, cta_label):
    return f"""    <section class="hero">
      <div class="container narrow">
        <p class="eyebrow">{eyebrow}</p>
        <h1>{h1}</h1>
        <p class="lede">{lede}</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="mailto:{EMAIL}">{icon('mail')}<span>{cta_label}</span></a>
        </div>
      </div>
    </section>"""


def service_prose(title, body_html):
    return f"""    <section class="section">
      <div class="container narrow">
        <h2 class="section-title">{title}</h2>
        <p>{body_html}</p>
      </div>
    </section>"""


FAQ_TITLE = {"en": "Frequently asked questions", "pt": "Perguntas frequentes"}


def render_fractional_cto(lang):
    t = T[lang]
    stats = "\n".join(stat_item(s, lang) for s in STATS)
    body = f"""  <main id="main">
{service_hero(t['fcto_eyebrow'], t['fcto_h1'], t['fcto_lede'], t['fcto_cta'])}

{service_prose(t['fcto_what_title'], t['fcto_what_p'])}

    <section class="section section-alt">
      <div class="container narrow">
        <h2 class="section-title">{t['fcto_proof_title']}</h2>
        <p>{t['fcto_proof_p']}</p>
        <div class="stats">
{stats}
        </div>
      </div>
    </section>

{faq_section(FAQ_TITLE[lang], t['fcto_faq'])}
  </main>
"""
    url = SITE + ROUTES["fractional_cto"][lang]
    svc = service_ld(t['fcto_h1'], t['fcto_eyebrow'], t['fcto_desc'], url)
    ld = ld_script([person_ld(lang), svc, faq_ld(t['fcto_faq'])])
    return page(lang, "fractional_cto", t["fcto_title"], t["fcto_desc"], body, ld=ld)


def render_custom_dev(lang):
    t = T[lang]
    caps = "\n".join(cap_card(c, lang) for c in CAPABILITIES)
    body = f"""  <main id="main">
{service_hero(t['cdev_eyebrow'], t['cdev_h1'], t['cdev_lede'], t['cdev_cta'])}

{service_prose(t['cdev_what_title'], t['cdev_what_p'])}

    <section class="section section-alt">
      <div class="container">
        <h2 class="section-title">{t['cap_title']}</h2>
        <p class="section-sub">{t['cap_sub']}</p>
        <div class="cards">
{caps}
        </div>
      </div>
    </section>

{service_prose(t['cdev_proof_title'], t['cdev_proof_p'])}

{faq_section(FAQ_TITLE[lang], t['cdev_faq'])}
  </main>
"""
    url = SITE + ROUTES["custom_dev"][lang]
    svc = service_ld(t['cdev_h1'], t['cdev_eyebrow'], t['cdev_desc'], url)
    ld = ld_script([person_ld(lang), svc, faq_ld(t['cdev_faq'])])
    return page(lang, "custom_dev", t["cdev_title"], t["cdev_desc"], body, ld=ld)


def notfound_block(lang):
    """One language's slice of the bilingual 404 body. All links are absolute
    (ROUTES values are already absolute) since a 404 is served at any depth."""
    t = T[lang]
    return f"""    <section class="hero" lang="{HTML_LANG[lang]}">
      <div class="container narrow">
        <p class="eyebrow">{t['nf_eyebrow']}</p>
        <h1>{t['nf_h1']}</h1>
        <p class="lede">{t['nf_lede']}</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="{ROUTES['home'][lang]}">{t['nf_home']}</a>
          <a class="btn btn-ghost" href="{ROUTES['products'][lang]}">{t['nf_products']}</a>
        </div>
      </div>
    </section>"""


def render_notfound():
    """A single bilingual 404: EN and PT sections stacked in one file, rendered
    through the shared PAGE template (head/header switcher/footer). Served by
    nginx error_page at the web root, never linked from nav or the sitemap."""
    t = T["en"]
    blocks = "\n\n".join(notfound_block(lang) for lang in LANGS)
    body = f"""  <main id="main">
{blocks}
  </main>
"""
    return page("en", "notfound", t["nf_title"], t["nf_desc"], body,
                ld=ld_script([person_ld("en")]))


# ----------------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------------

RENDERERS = {"home": render_home, "products": render_products, "about": render_about,
             "fractional_cto": render_fractional_cto, "custom_dev": render_custom_dev}


def out_path(route):
    """'/' -> dist/index.html ; '/pt/produtos/' -> dist/pt/produtos/index.html"""
    rel = route.strip("/")
    return os.path.join(DIST, rel, "index.html") if rel else os.path.join(DIST, "index.html")


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print("wrote", os.path.relpath(path, ROOT))


def copy_static():
    for item in STATIC:
        src = os.path.join(ROOT, item)
        dst = os.path.join(DIST, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        elif os.path.isfile(src):
            shutil.copy2(src, dst)
        print("copied", item)


def render_sitemap():
    urls = []
    for key in ROUTES:
        if key == "notfound":
            continue  # the 404 is error-only — never advertised in the sitemap
        for lang in LANGS:
            loc = SITE + ROUTES[key][lang]
            # Home top; products + the commercial service pages high (0.9); rest 0.7.
            high = {"products", "fractional_cto", "custom_dev"}
            prio = "1.0" if key == "home" else ("0.9" if key in high else "0.7")
            alts = "".join(
                f'\n    <xhtml:link rel="alternate" hreflang="{HTML_LANG[l]}" href="{SITE + ROUTES[key][l]}" />'
                for l in LANGS)
            alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE + ROUTES[key]["en"]}" />'
            urls.append(
                f'  <url>\n    <loc>{loc}</loc>{alts}\n    <changefreq>monthly</changefreq>'
                f'\n    <priority>{prio}</priority>\n  </url>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(urls) + "\n</urlset>\n")


def clean():
    """Wipe and recreate dist/ so every build is reproducible (no stragglers)."""
    shutil.rmtree(DIST, ignore_errors=True)
    os.makedirs(DIST)


_LD_RE = re.compile(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', re.DOTALL)
_DESC_RE = re.compile(r'<meta name="description" content="(.*?)" />')
META_DESC_MAX = 155  # SEO best practice: descriptions over ~155 chars get truncated


def seo_selfcheck():
    """Fail the build if any emitted page has invalid JSON-LD or an over-long
    meta description. This is the in-build verification the spec calls for: every
    ld+json block must json.loads cleanly and every description must stay ≤155."""
    problems = []
    ld_blocks = 0
    for root, _, files in os.walk(DIST):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            rel = os.path.relpath(os.path.join(root, fn), DIST)
            content = open(os.path.join(root, fn), encoding="utf-8").read()
            for block in _LD_RE.findall(content):
                ld_blocks += 1
                try:
                    json.loads(block)
                except json.JSONDecodeError as exc:
                    problems.append(f"{rel}: invalid JSON-LD ({exc})")
            for desc in _DESC_RE.findall(content):
                if len(desc) > META_DESC_MAX:
                    problems.append(f"{rel}: meta description {len(desc)} > {META_DESC_MAX} chars")
    if problems:
        raise SystemExit("SEO self-check failed:\n  " + "\n  ".join(problems))
    print(f"seo self-check ok ({ld_blocks} JSON-LD blocks valid, descriptions within "
          f"{META_DESC_MAX} chars)")


def main():
    clean()
    for key, render in RENDERERS.items():
        for lang in LANGS:
            write(out_path(ROUTES[key][lang]), render(lang))
    # Single bilingual 404 at the web root (no lang loop, no /pt/ variant).
    write(os.path.join(DIST, "404.html"), render_notfound())
    write(os.path.join(DIST, "sitemap.xml"), render_sitemap())
    copy_static()
    seo_selfcheck()
    print("done. output in dist/")


if __name__ == "__main__":
    main()
