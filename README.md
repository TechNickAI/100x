# 100x: AI Agents That Build Themselves

<img alt="100x Logo" src="./logo.png" style="width:25%" align="right"/>

**When AI agents can build other AI agents, your workforce evolves to meet whatever you need.**

The gap between knowing about AI and actually using it is embarrassingly large. Even people building AI struggle to apply that expertise to their own lives. 100x solves this: agents recognize when they lack a capability—and create the missing agent themselves.

---

## 🎯 What We're Building

Imagine having a team of AI employees helping you execute on your visions, where you can move at the speed of creativity.

Here's what that looks like:

- Every conversation and meeting gets processed, extracting commitments with context
- Your knowledge base stays current without manual updates
- Agents recognize their limitations and request new capabilities
- They learn from patterns to improve their own performance

You go from drowning in scattered information to having an AI team that handles the cognitive load while you focus on decisions and creative work.

## 📖 README-Driven Development

**Important:** This project follows README-driven development. We're documenting the complete vision and architecture before full implementation. Not all described functionality exists yet—see the [Progress Table](#-current-progress) below for what's actually built.

## 🔄 The 100x Framework

The framework follows a three-stage progression from personal efficiency to world-changing leverage. For the complete philosophy and detailed examples at each stage, see the [100x Framework](context/100x-framework.md).

### **1x → Efficiency**

Achieving 100% baseline by organizing your data and knowledge. Building a clean, human-readable knowledge base that eliminates chaos before adding automation. **Organization before automation.**

### **10x → Capacity**

Building an AI team where before there was only you. Specialized agents handle commitment tracking, memory management, research, and documentation while you focus on decisions and strategy. **One person becomes a team of ten.**

### **100x → Creativity**

Having an AI execution partner that turns visions into reality. Whether launching ventures, coordinating social impact, or validating research—the AI handles analysis, development, and deployment. **The barrier between imagining and executing dissolves.**

## 🔨 The Core Insight: Forge the Coder

Everything starts with one agent: **Forge the Coder**.

You build Forge manually. Then Forge builds everything else.

1. You build Forge once (the only agent you create by hand)
2. Forge builds all other agents from natural language descriptions
3. Agents recognize their limitations and request improvements
4. Your workforce evolves to meet emerging needs

The workflow:

```
You: "Build an agent that reconciles credit card statements"
→ Task assigned to AI
→ Forge generates the agent
→ Pull request created
→ You review and approve
→ New agent joins your workforce
```

## 📊 Current Progress

This table shows actual implementation status versus planned functionality:

| Phase                              | Component                    | Status         | Description                                   |
| ---------------------------------- | ---------------------------- | -------------- | --------------------------------------------- |
| **Phase 0: Bootstrap**             |                              |                |                                               |
|                                    | Repository Setup             | ✅ Complete    | Tooling, AI rules, pre-commit hooks, CI/CD    |
|                                    | Core Infrastructure          | ⬜ Not Started | FastAPI, Redis, Celery setup                  |
|                                    | BaseAgent Framework          | ⬜ Not Started | Agent definition and execution framework      |
|                                    | Forge the Coder              | ⬜ Not Started | The bootstrap agent that creates all others   |
|                                    | GitHub Integration           | ⬜ Not Started | PR creation and code management               |
|                                    | ClickUp Integration          | ⬜ Not Started | Task monitoring and updates                   |
| **Phase 1: Knowledge Layer**       |                              |                |                                               |
|                                    | Maya the Memory Keeper       | ⬜ Not Started | Knowledge base maintenance from conversations |
|                                    | Limitless Integration        | ⬜ Not Started | Personal conversation processing              |
|                                    | Fireflies Integration        | ⬜ Not Started | Meeting transcript analysis                   |
|                                    | Notion Provider              | ⬜ Not Started | Knowledge base storage and retrieval          |
|                                    | Winston the Wolf             | ⬜ Not Started | Privacy protection and data cleanup           |
| **Phase 2: Commitment Management** |                              |                |                                               |
|                                    | Sarah the Commitment Manager | ⬜ Not Started | Commitment extraction and tracking            |
|                                    | Task Creation Logic          | ⬜ Not Started | Smart routing and assignment                  |
|                                    | Progress Monitoring          | ⬜ Not Started | Active tracking and escalation                |
| **Phase 3: Orchestration**         |                              |                |                                               |
|                                    | Piper the Chief of Staff     | ⬜ Not Started | User interface and agent coordinator          |
|                                    | Agent Registry               | ⬜ Not Started | Discovery and capability matching             |
|                                    | Inter-Agent Communication    | ⬜ Not Started | Internal delegation patterns                  |
| **Phase 4: Self-Evolution**        |                              |                |                                               |
|                                    | Self-Improvement Logic       | ⬜ Not Started | Agents requesting enhancements                |
|                                    | Capability Creation          | ⬜ Not Started | Dynamic capability generation                 |
|                                    | Evolution Tracking           | ⬜ Not Started | Version history and audit trail               |

Legend: ✅ Complete | 🚧 In Progress | ⬜ Not Started

## 🛠️ Technology Choices

Built with modern, proven technologies:

- **Python 3.13+** with async support and type hints
- **FastAPI** for webhook handling and APIs
- **Pydantic AI** for structured agent outputs
- **OpenRouter** for unified LLM access (Claude Sonnet 4.5 default)
- **Celery + Redis** for task queue and caching
- **Logfire** for comprehensive observability
- **Click + Rich** for beautiful CLI tools
- **Docker** for consistent deployment

## 🎯 Data Sources

Connects to where your work actually happens:

- **Wearable recordings** (Limitless AI)
- **Meeting transcripts** (Fireflies AI)
- **Project management** (ClickUp/Asana/Linear)
- **Knowledge bases** (Notion/Obsidian/Confluence)
- **Communication** (Email, WhatsApp, Telegram)
- **Documents** (Dropbox, Google Drive)

Dedicated agents automatically extract facts, commitments, and context from these sources.

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

### Long-Term Vision

It evolves based on actual use:

- Agents recognize patterns and create specialized helpers
- Capabilities improve from real-world experience
- New agents emerge from identified gaps
- Human creativity flows into execution without friction

## 📚 Documentation

The [100x Framework](context/100x-framework.md) explains the philosophy and progression from 1x → 10x → 100x.

For detailed architecture, agent specifications, and implementation guides, explore the [context/](context/) folder.

## 💡 Core Principles

These principles emerged from real implementation challenges:

- **Self-evolution over features** - Create capabilities when you need them, not based on prediction
- **Agent-first design** - Autonomous agents that communicate and evolve, not predetermined workflows
- **Data-first architecture** - Store everything raw, let multiple agents extract different insights
- **Human oversight** - All agent creation flows through pull requests for review
- **Heart-centered AI** - Agents operate from compassion and emotional intelligence

## 🤝 Contributing

This is an open-source foundation for autonomous AI systems. We welcome contributions that align with the vision of self-evolving, human-amplifying AI.

## 📝 License

See [LICENSE](LICENSE) for details.

---

<div align="center">

_From a place of universal love, we're building AI that amplifies human potential._

</div>
