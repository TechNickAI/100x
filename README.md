# 100x Your Life with an AI Team

[![Build Status](https://img.shields.io/github/actions/workflow/status/TechNickAI/100x/build.yml?branch=main&label=build&style=flat-square)](https://github.com/TechNickAI/100x/actions/workflows/build.yml)
[![Coverage](https://img.shields.io/codecov/c/github/TechNickAI/100x?style=flat-square)](https://app.codecov.io/gh/TechNickAI/100x)
[![Python](https://img.shields.io/badge/python-3.13-blue?style=flat-square)](https://www.python.org/downloads/release/python-3130/)
[![License](https://img.shields.io/badge/license-Fair%20Use-yellow?style=flat-square)](LICENSE)

<img alt="100x Logo" src="./logo.png" style="width:25%" align="right"/>

**Reclaim your presence. Build an AI team. Move at the speed of creativity.**

You know AI could transform your work. You've heard about automation tools but they're too complex. You can see the value of AI employees but don't know how to build them.

This gives you a team of AI employees that builds itself. You describe what you need in plain English. The AI generates the agent, you review the code, and your workforce grows. Every agent can create new agents when it hits a limitation.

---

## 🎯 What You Get

A team of AI employees helping you execute on your visions. Move at the speed of creativity.

Specifically:

- Every conversation and meeting gets processed, extracting commitments with context
- Your knowledge base stays current without manual updates
- Agents recognize their limitations and request new capabilities
- They learn from patterns to improve their own performance

Your AI team handles the cognitive load while you focus on decisions and creative work.

## 📖 README-Driven Development

**Important:** This project follows README-driven development. We're documenting the complete vision and architecture before full implementation. Not all described functionality exists yet—see the [Progress Table](#-current-progress) below for what's actually built.

## 🔄 The 100x Framework

The framework follows a three-stage progression from personal efficiency to world-changing leverage. For the complete philosophy and detailed examples at each stage, see the [100x Framework](context/100x-framework.md).

```mermaid
graph LR
    A[📋 1x: Efficiency<br/>Organize Data] --> B[👥 10x: Capacity<br/>Build AI Team]
    B --> C[🎨 100x: Creativity<br/>Execute Visions]
    style A fill:#fff3cd
    style B fill:#d1ecf1
    style C fill:#d4edda
```

### **📋 1x → Efficiency**

Achieving 100% baseline by organizing your data and knowledge. Building a clean, human-readable knowledge base that eliminates chaos before adding automation. **Organization before automation.**

### **👥 10x → Capacity**

Building an AI team where before there was only you. Specialized agents handle commitment tracking, memory management, research, and documentation while you focus on decisions and strategy. **One person becomes a team of ten.**

### **🎨 100x → Creativity**

Having an AI execution partner that turns visions into reality. Whether launching ventures, coordinating social impact, or validating research—the AI handles analysis, development, and deployment. **Go from idea to working prototype in days, not months.**

## 🔨 The Core Insight: Forge the Coder

Everything starts with one agent: **Forge the Coder**.

You build Forge manually. Then Forge builds everything else.

1. You build Forge once (the only agent you create by hand)
2. Forge builds all other agents from natural language descriptions
3. Agents recognize their limitations and request improvements
4. Your workforce evolves to meet emerging needs

The workflow:

```mermaid
graph LR
    A[You: Create Task] --> B[Forge Generates Agent]
    B --> C[Pull Request]
    C --> D[You Review & Merge]
    D --> E[New Agent Joins Workforce]
    E -.Agent can create more agents.-> A
    style A fill:#e1f5ff
    style E fill:#d4f1d4
```

## 📊 Current Progress

This table shows actual implementation status versus planned functionality:

| Phase                              | Component                    | Status         | Description                                     |
| ---------------------------------- | ---------------------------- | -------------- | ----------------------------------------------- |
| **Phase 0: Bootstrap**             |                              |                |                                                 |
|                                    | Repository Setup             | ✅ Complete    | Tooling, AI rules, pre-commit hooks, CI/CD      |
|                                    | Agent Infrastructure         | 🚧 In Progress | Pydantic AI, OpenRouter, Logfire, Redis, Celery |
|                                    | BaseAgent Framework          | ⬜ Not Started | Agent definition and execution framework        |
|                                    | Forge the Coder              | ⬜ Not Started | The bootstrap agent that creates all others     |
|                                    | Git/gh CLI Integration       | ⬜ Not Started | Branch and PR creation via CLI tools            |
|                                    | ClickUp Integration          | ⬜ Not Started | Task monitoring via polling                     |
| **Phase 1: Knowledge Layer**       |                              |                |                                                 |
|                                    | Maya the Memory Keeper       | ⬜ Not Started | Knowledge base maintenance from conversations   |
|                                    | Limitless Integration        | ⬜ Not Started | Personal conversation processing                |
|                                    | Fireflies Integration        | ⬜ Not Started | Meeting transcript analysis                     |
|                                    | Notion Provider              | ⬜ Not Started | Knowledge base storage and retrieval            |
|                                    | Winston the Wolf             | ⬜ Not Started | Privacy protection and data cleanup             |
| **Phase 2: Commitment Management** |                              |                |                                                 |
|                                    | Sarah the Commitment Manager | ⬜ Not Started | Commitment extraction and tracking              |
|                                    | Task Creation Logic          | ⬜ Not Started | Smart routing and assignment                    |
|                                    | Progress Monitoring          | ⬜ Not Started | Active tracking and escalation                  |
| **Phase 3: Orchestration**         |                              |                |                                                 |
|                                    | Piper the Chief of Staff     | ⬜ Not Started | User interface and agent coordinator            |
|                                    | Agent Registry               | ⬜ Not Started | Discovery and capability matching               |
|                                    | Inter-Agent Communication    | ⬜ Not Started | Internal delegation patterns                    |
| **Phase 4: Self-Evolution**        |                              |                |                                                 |
|                                    | Self-Improvement Logic       | ⬜ Not Started | Agents requesting enhancements                  |
|                                    | Capability Creation          | ⬜ Not Started | Dynamic capability generation                   |
|                                    | Evolution Tracking           | ⬜ Not Started | Version history and audit trail                 |

Legend: ✅ Complete | 🚧 In Progress | ⬜ Not Started

## 🛠️ Technology Choices

Built with modern, proven technologies:

- **Python 3.13+** with async support and type hints
- **Pydantic AI** for structured agent outputs and LLM interactions
- **OpenRouter** for unified LLM access (see ai/core/openrouter.py for models)
- **Celery + Redis** for task queue and caching
- **Logfire** for comprehensive observability
- **Click + Rich** for beautiful CLI tools
- **Git + gh CLI** for version control and pull request creation
- **Docker** for consistent deployment

**Post-MVP additions:** FastAPI (webhooks), PostgreSQL (database), Django Admin (UI)

## 🎯 How It Works

Your conversations and meetings flow through agents that extract what matters:

```mermaid
graph TB
    A[🎙️ Conversations<br/>Limitless, Fireflies] --> D[🤖 Agents Extract<br/>Commitments & Context]
    B[📧 Messages<br/>Email, WhatsApp] --> D
    C[📄 Documents<br/>Dropbox, Drive] --> D
    D --> E[📚 Knowledge Base<br/>Notion: People, Projects, Intelligence]
    D --> F[✅ Tasks Created<br/>ClickUp: Commitments & Actions]
    style D fill:#e1f5ff
    style E fill:#d4edda
    style F fill:#fff3cd
```

**Data sources:**

- Wearable recordings (Limitless AI)
- Meeting transcripts (Fireflies AI)
- Communication (Email, WhatsApp, Telegram)
- Documents (Dropbox, Google Drive)
- Project management (ClickUp/Asana/Linear)
- Knowledge bases (Notion/Obsidian/Confluence)

## 🚀 The Path Forward

### Immediate Next Step

Build Forge the Coder—the only agent you'll build manually. Everything else gets built by Forge through natural language task descriptions.

### Then What?

Once Forge works:

1. Create a task: "Build Maya the Memory Keeper agent"
2. Forge generates the code
3. Review the PR
4. Maya joins your workforce
5. Repeat for each needed capability

### 🌱 Long-Term Vision

Your AI workforce evolves with you:

- Agents recognize patterns and create specialized helpers
- Capabilities improve from real-world experience
- New agents emerge from identified gaps
- You spend time on creative decisions, not implementation details

## 📚 Documentation

The [100x Framework](context/100x-framework.md) explains the philosophy and progression from 1x → 10x → 100x.

For detailed architecture, agent specifications, and implementation guides, explore the [context/](context/) folder.

## 💡 Core Principles

These principles emerged from real implementation challenges:

- **Self-evolution over features** - Create capabilities when you need them, not based on prediction
- **Agent-first design** - Autonomous agents that communicate and evolve, not predetermined workflows
- **Data-first architecture** - Store everything raw, let multiple agents extract different insights
- **Human oversight** - All agent creation flows through pull requests for review
- **Heart-centered AI** - All agents use [heart-centered-prompts](https://github.com/TechNickAI/heart-centered-prompts) to operate from compassion, recognize when to offer emotional support vs. analysis, and treat interactions as mutual flourishing

## 🤝 Contributing

This is an open-source foundation for autonomous AI systems. We welcome contributions that align with the vision of self-evolving, human-amplifying AI.

## 📝 License

See [LICENSE](LICENSE) for details.

---

<div align="center">

_From a place of universal love, we're building AI that amplifies human potential._

</div>
