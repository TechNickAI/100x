# 🤖 100x AI Agent Infrastructure

Agent framework for the 100x system. Agents are defined in `.agent.md` files (markdown with YAML frontmatter) and executed through a clean Python interface.

## Architecture

### Core Components

**Agent Definition Format** - `.agent.md` files:

- YAML frontmatter for configuration
- HTML comments for section markers (`<!-- System Prompt -->`)
- Code fences for prompts (Jinja2) and schemas (Python)
- Single-file agent definitions that are both human and LLM-readable

**BaseAgent** - Core execution class:

- Loads and parses `.agent.md` files
- Renders Jinja2 templates with context
- Calls OpenRouter with structured output via Pydantic AI
- Wraps execution in Logfire spans for observability
- Tracks token usage and costs

**OpenRouter Integration** - Model management:

- Unified interface to Claude Sonnet, OpenAI, and others
- Automatic fallback routing
- Anthropic prompt caching
- Cost tracking per request

**CLI** - Beautiful command-line interface:

- `hundredx agents list` - Show all agents
- `hundredx agents run <name>` - Execute an agent
- `hundredx agents validate` - Check agent files
- Or use `python -m cli.main` for local testing
- Built with Click + Rich for gorgeous output

## Directory Structure

```
ai/
├── agents/
│   ├── patrick.agent.md       # Test agent (12yo kid)
│   └── shared/
│       └── heart_centered.jinja  # Shared prompt component
│
├── core/
│   ├── config.py              # Pydantic settings (from .env)
│   ├── agent_config.py        # .agent.md parser
│   └── openrouter.py          # LLM model management
│
├── tests/
│   ├── test_agent_config.py   # Parser tests
│   ├── test_base_agent.py     # Agent execution tests
│   └── fixtures/              # Test .agent.md files
│
└── README.md                  # This file
```

## Quick Start

```bash
# Set up environment
workon 100x
cp .env.example .env
# Add your OPENROUTER_API_KEY to .env

# Install dependencies
uv pip compile requirements/requirements.in
pip install -e ".[dev]"

# Run Patrick (our test agent)
hundredx agents run patrick --query "What's your favorite dinosaur?"

# Or use python -m for local testing
python -m cli.main agents run patrick --query "What's your favorite dinosaur?"

# List all agents
hundredx agents list

# Validate agent files
hundredx agents validate
```

## Agent File Format

```markdown
---
name: Agent Name
description: What this agent does
model: anthropic/claude-sonnet-4 # See ai/core/openrouter.py for supported models
temperature: 0.7
purpose: |
  Detailed explanation of the agent's purpose
  for other agents to understand.
capabilities:
  - capability_one
  - capability_two
---

# Agent Name

Human-readable description.

<!-- System Prompt -->

\`\`\`jinja2
{{ heart_centered_prompt }}

You are {{ agent_name }}. Your purpose is...
\`\`\`

<!-- User Prompt -->

\`\`\`jinja2
User query: {{ query }}
\`\`\`

<!-- Output Schema -->

\`\`\`python
from pydantic import BaseModel

class Output(BaseModel):
response: str
\`\`\`
```

## Development

### Running Tests

```bash
pytest ai/tests/ -v
```

### Creating a New Agent

1. Create `ai/agents/your_agent.agent.md`
2. Follow the format above
3. Test it: `100x agents run your_agent`

### Adding Shared Prompts

Place reusable prompt components in `ai/agents/shared/` and include them:

```jinja2
{% include 'shared/heart_centered.jinja' %}
```

## Configuration

All configuration via `.env` file (see `.env.example`):

- `OPENROUTER_API_KEY` - Required for LLM calls
- `LOGFIRE_TOKEN` - Optional, for observability
- `LOG_LEVEL` - Default: INFO

## Philosophy

Agents are **declarative**. The `.agent.md` file describes what the agent is, not how it works. This makes agents:

- **Readable** - Humans and LLMs can understand them
- **Versionable** - Git tracks changes meaningfully
- **Modifiable** - Forge (future) can edit them
- **Testable** - Easy to test prompts and schemas separately

From a place of universal love, we build AI that amplifies human potential.

---

## 📊 Current Status

**✅ MVP Infrastructure Complete**

- 25 tests passing (93% coverage)
- All ruff checks passing
- Beautiful CLI operational
- Patrick the 12-year-old agent ready to chat!

**Next Steps**:

1. **Test with Real LLM**:

   ```bash
   # Add OPENROUTER_API_KEY to .env
   python -m cli.main agents run patrick --query "Tell me about velociraptors!"
   ```

2. **Build Forge the Coder** - Use this infrastructure to create the bootstrap agent
3. **Evolve** - Let agents build agents!

**Status**: Ready for Phase 0 (Forge the Coder)  
**See**: `IMPLEMENTATION_SUMMARY.md` for complete details
