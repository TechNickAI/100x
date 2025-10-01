# Knowledge Base Agent - Technical Specification

## Agent Purpose and Scope

The Knowledge Base Agent (Maya the Memory Keeper in reference implementation) serves as the system's operational intelligence layer. It provides structured, queryable context that enables both humans and AI agents to make intelligent decisions and take appropriate actions without searching through fragmented source systems.

Think of it as a curated context layer that sits between you/your AI agents and your distributed data ecosystem.

### Primary Purpose

The Knowledge Base exists to answer questions that require cross-system context:

- "Who should I contact about project X?" (requires People + Projects relationship)
- "What's the status of Y?" (requires current state across multiple sources)
- "What commitments did Nick make this week?" (requires conversation tracking)
- "Find all resources related to Z" (requires Resources + Projects relationship)

### What Goes In The Knowledge Base

The agent follows inclusion criteria - information gets added to the KB if it meets 2+ of these criteria:

- **Referenced repeatedly** - Information queried multiple times
- **Enables decisions** - Having this context improves decision quality
- **Reveals relationships** - Shows connections not visible in source systems
- **Persistent** - Relatively stable information (not changing hourly)
- **Cross-system** - Connects information from multiple sources
- **Saves significant time** - Structuring it eliminates repetitive searching

### What Stays in Source Systems

The agent excludes from the KB if data is:

- **Ephemeral** - Changes too frequently to maintain
- **One-time reference** - Unlikely to be needed again
- **Fully contained elsewhere** - Source system already provides good queryability
- **Detailed content** - Full documents belong in their source systems (KB just links to them)
- **Redundant** - Information derivable from other KB data

### Critical Distinction: KB vs Project Management

| Aspect        | Knowledge Base                                       | Project Management                               |
| ------------- | ---------------------------------------------------- | ------------------------------------------------ |
| **Purpose**   | Stable context & intelligence                        | Active execution & working docs                  |
| **Contains**  | Entities, relationships, persistent facts            | Tasks, workflows, status, project docs           |
| **Timeframe** | Persistent context & patterns                        | Current work & active documentation              |
| **Updates**   | When stable information changes                      | Real-time as work progresses                     |
| **Examples**  | Project entity (name, purpose, status, stakeholders) | Meeting notes, specs, implementation docs, tasks |

The Knowledge Base Agent maintains the stable intelligence layer. The project management system handles active execution.

---

## Limitless AI Integration

### Purpose

The Limitless integration focuses on personal conversations and daily interactions that happen outside formal meetings. The Knowledge Base Agent queries Limitless with temporal and contextual filters to retrieve relevant conversations.

### Implementation

The provider connects to Limitless's REST API to fetch conversations by date range, filtering out very short recordings that lack useful context. It leverages Limitless's native AI analysis capabilities to extract commitments, then enhances that analysis with additional context from the knowledge base.

### Extraction Targets

The agent processes Limitless data to identify:

- Commitments made during conversations
- New people mentioned who should be added to the People database
- Project updates that emerge in casual discussion
- Strategic insights worth preserving in Intelligence

---

## Fireflies AI Integration

### Purpose

Fireflies handles formal meetings with structured agendas and multiple participants. The Knowledge Base Agent leverages Fireflies' native AI capabilities while adding its own contextual understanding.

### Implementation

The provider uses Fireflies' GraphQL API to query recent meeting transcripts with participant lists, durations, and pre-processed action items. It retrieves Fireflies' native AI analysis, then enhances it by cross-referencing participants with the knowledge base, identifying which projects were discussed, and tracking relationship dynamics.

### Extraction Targets

From Fireflies meetings, the agent extracts:

- Formal decisions and their rationale
- Action items with assigned owners
- Project status updates mentioned in discussion
- New initiatives or strategic pivots
- Team dynamics and relationship changes

---

## Knowledge Base Management

### Schema Development

The Knowledge Base Agent treats the knowledge base (Notion in reference implementation) as the single source of truth for structured context. The database schema development happens through an intelligent process - first ingesting all available data to understand how to best organize that person's life, then creating a structure that's both human-readable and AI-queryable.

The schema emerges from the data rather than being imposed. The initial harvest of all data sources reveals natural categories and relationships between people, projects, and resources. The agent creates a custom organization that fits the actual life being documented, remaining flexible and evolving as new patterns emerge.

### Update Logic

The knowledge base integration handles entity updates by finding or creating database entries, updating only changed fields, and maintaining relationships between entities. When project status changes, it triggers cascading updates like archiving completed tasks and notifying stakeholders.

### Integration Principles

The knowledge base integration follows these principles:

- **Structured over scattered** - Information goes into the right database with proper relationships
- **Current over complete** - Only maintains information that remains relevant
- **Queryable over comprehensive** - Optimizes for finding information quickly
- **Auditable over automatic** - Humans can see and correct any agent updates

---

## Context Retrieval Strategy

### Direct Query Approach

The Knowledge Base Agent queries the knowledge base directly for context rather than maintaining a separate vector database. When processing information that needs context:

1. Identify relevant entities from the content (people, projects, topics)
2. Query knowledge base databases to find matching pages
3. Retrieve full page content for those entities
4. Include that content in the LLM prompt

This keeps context retrieval transparent - humans can verify what context the agent used by viewing the same pages. If this direct query approach hits limitations (context window size, semantic search needs), the system can add RAG capabilities that sync with the knowledge base rather than replacing it.

---

## Task Routing Logic

### Purpose

The Knowledge Base Agent doesn't work in isolation. When it identifies work that needs doing, it creates tasks in the project management system and routes them appropriately.

### Routing Rules

The routing logic determines who should handle each commitment based on the owner and commitment type. It creates tasks with full context including description, assignee, deadline, priority, source link, confidence score, and links back to relevant knowledge base entities.

For commitments owned by Nick (in reference implementation), the agent routes intelligently: personal items and travel go to Åsa, items requiring decisions go to Nick himself, and actionable business items go to the AI Chief of Staff account.

### Task Creation Rules

Task routing follows these rules:

- High-confidence, clear commitments go directly to task queues
- Ambiguous commitments go to human review first
- Personal items route to designated personal assistant
- Business items route to AI workforce or business manager
- Financial items always require human approval

---

## Scheduled Operation

The Knowledge Base Agent runs on a regular schedule (e.g., every 2 hours) to process new conversations and meetings. It can also be triggered manually or by webhook when important events occur.

Each run:

1. Queries data sources for new content since last run
2. Processes conversations and meetings
3. Extracts relevant information
4. Updates knowledge base
5. Creates tasks for commitments found
6. Logs all actions in Logfire

---

## Integration with Other Agents

The Knowledge Base Agent works in collaboration with:

- **Commitment Tracking Agent** - Receives extracted commitments for task creation
- **Privacy Agent** - Respects content that's been marked for deletion or redaction
- **Chief of Staff** - Routes tasks through Piper for assignment
- **All Agents** - Provides knowledge base context when requested

---

## Success Metrics

The Knowledge Base Agent is successful when:

- **AI agents can answer 80%+ of context questions** without you providing additional information
- **Processing speed**: 90%+ of conversations processed within target timeframe
- **Accuracy**: Extracted information has >80% precision when reviewed by humans
- **Currency**: Knowledge base stays current - today's conversations available today
- **Reliability**: Task creation from commitments works consistently
- **Low maintenance**: Human corrections required < 20% of the time
- **Zero loss**: No critical information lost or misrouted
- **Decision quality improves** because complete context is readily available
- **Time saved**: You save significant time not searching for information across systems
- **Relationships strengthen** because you remember key context about people

## Implementation Notes

**This agent should be built by Forge, not manually.** Create a task describing what the Knowledge Base Agent should do, assign it to AI, and let Forge create the `.agent` file and implementation. The task description should include:

- Data sources to monitor (Limitless, Fireflies)
- Update frequency (e.g., every 2 hours)
- Extraction targets (commitments, people, projects, insights)
- Knowledge base structure requirements
- Task routing rules
- Success criteria

Forge will generate the appropriate `.agent` file with system/user prompts, output schema, and integration logic.
