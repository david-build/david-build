<div align="center">

# David Build

**Full-stack engineer · system architect · founder of [Perfecto Web](https://perfecto-web.com)**

Building for the web since 2004. Lately also native apps for macOS and iPhone, and a bit of hardware.

[![Website](https://img.shields.io/badge/perfecto--web.com-1f6bff?style=flat&logo=safari&logoColor=white)](https://perfecto-web.com)
[![Telegram](https://img.shields.io/badge/Telegram-@PerfectoWeb-1f6bff?style=flat&logo=telegram&logoColor=white)](https://t.me/PerfectoWeb)
[![X](https://img.shields.io/badge/X-@PerfectoWeb-111?style=flat&logo=x&logoColor=white)](https://x.com/PerfectoWeb)
[![Organisation](https://img.shields.io/badge/GitHub-@PerfectoWeb-111?style=flat&logo=github&logoColor=white)](https://github.com/PerfectoWeb)
[![Homebrew](https://img.shields.io/badge/homebrew-perfectoweb%2Ftap-1f6bff?style=flat&logo=homebrew&logoColor=white)](https://github.com/PerfectoWeb/homebrew-tap)

[![Years on GitHub](https://badges.strrl.dev/years/david-build?style=flat&labelColor=333333&logoColor=E7E7E7)](https://github.com/david-build)
[![Contributions this year](https://badges.strrl.dev/contributions/yearly/david-build?style=flat&labelColor=333333&logoColor=E7E7E7&color=1f6bff)](https://github.com/david-build)
[![Commits this month](https://badges.strrl.dev/commits/monthly/david-build?style=flat&labelColor=333333&logoColor=E7E7E7&color=1f6bff)](https://github.com/david-build)
[![Followers](https://img.shields.io/github/followers/david-build?style=flat&labelColor=333333&logoColor=E7E7E7&label=Followers&logo=github)](https://github.com/david-build?tab=followers)

</div>

---

## About

I started coding professionally in 2004, before modern frameworks existed: Adobe Flash and ActionScript, then PHP and the early web stack, and every generation since. Twenty years of shipping production systems taught me one thing above all: **own your stack**. Fewer dependencies, fewer surprises, and code you can still read ten years later.

My core is backend architecture and scalable web systems, but I cover the whole cycle: product thinking, UX, frontend, DevOps and production deployment. Most of what I build is closed-source client work; the tools I made for myself are open and live at [@PerfectoWeb](https://github.com/PerfectoWeb).

---

## What I build

### 🧱 Perfecto CMS

A proprietary content management system I have been developing and evolving since 2009. It powers the sites and platforms Perfecto Web ships to clients.

- PHP 8.3, MySQL/MariaDB, **zero third-party dependencies**: no framework, no Composer, own template engine
- Own frontend and admin component set in plain JavaScript, no jQuery, no build step
- Multilingual out of the box, SEO-first routing, one-click theming
- Security by default: CSRF everywhere, TOTP two-factor auth, pluggable anti-bot layer, hardened uploads, tamper-evident activity log, redacted structured logging
- Own cache layer (files / APCu / Redis), mail queue with retry and backoff, cron dispatcher, soft-delete trash, image pipeline with automatic WebP
- Dark-theme admin panel with a modern rich-text editor, analytics, ticket desk and newsletter engine built in

### 🍎 Native apps (Swift)

Lately I write native apps for macOS and iPhone: SwiftUI + AppKit, no Electron, no telemetry.

| | |
| --- | --- |
| [**Belay**](https://github.com/PerfectoWeb/Belay) | Keeps your Mac awake while AI coding agents work, then lets it sleep. [Mac App Store](https://apps.apple.com/app/belay-awake-for-ai-agents/id6801207644) · [Homebrew](https://github.com/PerfectoWeb/homebrew-tap) · [site](https://perfectoweb.github.io/Belay/) |
| [**Gibson**](https://github.com/PerfectoWeb/Gibson) | A macOS screen saver: the hacker-film dashboard, driven by real system telemetry |
| **f64** | A pure RAW camera for iPhone with manual dials and zero AI. In development |

### 🔧 Hardware & embedded

- [**PocketLab**](https://github.com/PerfectoWeb/flipper-pocketlab): a native Flipper Zero app that teaches the device through interactive lessons. In the [Flipper Apps Catalog](https://lab.flipper.net/apps/pocketlab)
- [**IBM VFD Display**](https://github.com/PerfectoWeb/IBM-VFD-Display-ESP32-S3): ESP32-S3 driving a Futaba/IBM 20x2 vacuum fluorescent display
- Nova editor extensions: [Perfect Dark](https://github.com/PerfectoWeb/nova-perfectdark-theme), [Favicon Clip](https://github.com/PerfectoWeb/nova-favicon-clip), [Lorem Clip](https://github.com/PerfectoWeb/nova-lorem-clip)

---

## Stack

<div align="center">

![PHP](https://img.shields.io/badge/PHP_8.3-777BB4?style=flat&logo=php&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL_/_MariaDB-4479A1?style=flat&logo=mysql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=flat&logo=nginx&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=111)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-339933?style=flat&logo=nodedotjs&logoColor=white)
![Swift](https://img.shields.io/badge/Swift-F05138?style=flat&logo=swift&logoColor=white)
![SwiftUI](https://img.shields.io/badge/SwiftUI_/_AppKit-0D84FF?style=flat&logo=apple&logoColor=white)
![C](https://img.shields.io/badge/C_/_ESP32-A8B9CC?style=flat&logo=c&logoColor=111)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Figma](https://img.shields.io/badge/Figma-F24E1E?style=flat&logo=figma&logoColor=white)
![Telegram Bots](https://img.shields.io/badge/Telegram_Bots_&_Mini_Apps-26A5E4?style=flat&logo=telegram&logoColor=white)
![Claude Code](https://img.shields.io/badge/Agentic_workflows-Claude_Code-D97757?style=flat&logo=anthropic&logoColor=white)

</div>

| Area | What I do with it |
| --- | --- |
| **Backend** | PHP 8+ (20 years in production), Node.js, RESTful API design, high-load and security-focused systems |
| **Data & infra** | MySQL/MariaDB schema design, Redis/APCu caching, Nginx/Apache, Linux servers, deployment and monitoring |
| **Frontend** | Semantic HTML/CSS, design tokens, plain JavaScript components, performance and accessibility first |
| **Native** | Swift, SwiftUI, AppKit, AVFoundation; notarized and App Store releases, Homebrew distribution |
| **Embedded** | ESP32 / Arduino (C/C++), Flipper Zero apps |
| **Product & design** | UI/UX, design systems, Figma, Telegram Mini Apps |
| **Workflow** | Agentic engineering with Claude Code and Codex, CI on GitHub Actions, structured docs for every project |

---

## GitHub stats

<div align="center">

[![All contributions](https://badges.strrl.dev/contributions/all/david-build?style=flat&labelColor=333333&logoColor=E7E7E7&color=1f6bff)](https://github.com/david-build)
[![All commits](https://badges.strrl.dev/commits/all/david-build?style=flat&labelColor=333333&logoColor=E7E7E7&color=1f6bff)](https://github.com/david-build)
[![All PRs](https://badges.strrl.dev/prs/all/david-build?style=flat&labelColor=333333&logoColor=E7E7E7&color=1f6bff)](https://github.com/david-build?tab=repositories)

<a href="https://github.com/david-build"><img src="https://ghchart.rshah.org/1f6bff/david-build" alt="Contribution graph" width="100%"></a>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username=david-build&theme=github_dark">
  <img src="https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username=david-build&theme=github" alt="Profile details" width="100%">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-profile-summary-cards.vercel.app/api/cards/stats?username=david-build&theme=github_dark">
  <img src="https://github-profile-summary-cards.vercel.app/api/cards/stats?username=david-build&theme=github" alt="Stats" width="49%">
</picture>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-profile-summary-cards.vercel.app/api/cards/productive-time?username=david-build&theme=github_dark&utcOffset=3">
  <img src="https://github-profile-summary-cards.vercel.app/api/cards/productive-time?username=david-build&theme=github&utcOffset=3" alt="Productive time" width="49%">
</picture>

<sub>Most of my commits land in private repositories, so the public graph is the tip of the iceberg.</sub>

</div>

---

## Experience

### 🧠 Perfecto Web ® LLC (2008 – Present)

Founder & Lead Engineer

- Full-cycle development: architecture, backend, frontend, UX, deployment
- Websites, SaaS platforms, bots, native apps; long-term client partnerships
- Author and maintainer of Perfecto CMS

### 💳 Fintech Platform (2018 – 2026)

Technical Lead / CTO

- Architecture of a high-load payment and settlement platform
- Security-focused API integrations with banks and payment providers
- Team leadership and engineering strategy

### 🔗 Tonkeeper Partner (2023 – 2026)

Technical Integration Partner

- Native in-app purchase flow integrated into the wallet
- Close collaboration with the ecosystem teams

### 💾 Xcite Computer Solution, New York (2004 – 2008)

Full-Stack Developer & UI/UX Designer

- Adobe Flash & ActionScript development, early web application systems
- UI/UX design before "UX" became mainstream

---

## Achievements

🏆 Two-time 1st place winner of the Yandex Alice skill development competition (2019): [Guess the Dinosaur](https://perfecto-web.com/ru/portfolio/apps/415-alice-skill-dinosaurus.html) and [Colors Mixer](https://perfecto-web.com/ru/portfolio/apps/410-colors-mixer.html)

⭐ Flawless freelance reputation across [Weblancer](https://www.weblancer.net/users/PerfectoWeb/), [Freelance.ru](https://freelance.ru/reviews/PerfectoWeb/) and [FL.ru](https://www.fl.ru/users/perfectoweb/portfolio/), 2008 – 2022

---

<div align="center">

I thrive in complex systems. I take responsibility. I build for performance, scalability and longevity.

</div>
