# KB Purpose

## Knowledge Base Purpose Definition

### **Primary Purpose: Operational Intelligence Layer**

**The KB exists to provide structured, queryable context that enables both humans and AI agents to make intelligent decisions and take appropriate actions without searching through fragmented source systems.**
Think of it as: **A curated context layer that sits between you/your AI agents and your distributed data ecosystem.**

---

## Purpose Breakdown by Stakeholder

### **For AI Agents:**

Enable answering questions that require cross-system context:

- "Who should I contact about project X?" (requires People + Projects relationship)
- "What's the status of Y?" (requires current state across multiple sources)
- "What commitments did Unity make this week?" (requires Journal + commitment tracking)
- "Find all resources related to Z" (requires Resources + Projects relationship)
- "What do we know about topic W?" (requires Intelligence database)

### **For You (Unity or Nick):**

Provide instant reference during client calls, strategic planning, and decision-making:

- Quick lookup of project context before meetings
- Relationship mapping for strategic networking
- Resource inventory for capability assessment
- Intelligence repository for continuous learning
- Historical context for pattern recognition

### **For the 100x System:**

Serve as foundational infrastructure that other components depend on:

- Document Specialist queries KB for information retrieval
- Chief of Staff queries KB for commitment tracking and context
- Communication Agent queries KB for relationship context and preferences
- All agents write back to KB to maintain currency

### **For UnityOS Business:**

Demonstrate replicable methodology that becomes consulting deliverable:

- Proof of concept for client engagements
- Template for KB construction process
- Validation of data-first approach
- Case study for marketing and sales

---

## Core Design Principles (Derived from Purpose)

### **1\. Structured Context Over Raw Storage**

- Extract key entities, relationships, and facts
- Link to source documents rather than duplicating full content
- Focus on "what you need to know" not "everything that exists"

### **2\. Queryability Over Comprehensiveness**

- Optimize for AI agent questions, not human browsing
- Structured relationships enable complex queries
- Metadata enables filtering and pattern recognition

### **3\. Currency Over Archive**

- Maintain current state as priority
- Historical context only when it informs future decisions
- Stale data actively removed or flagged

### **4\. Actionable Over Informational**

- Information that enables decisions and actions
- Context that reduces "I need to look that up" moments
- Reference that prevents rediscovering what you already know

---

## Inclusion Criteria Framework

### **Include in KB if data meets 2+ of these criteria:**

✅ **Referenced repeatedly** - You/agents will query this information multiple times ✅ **Enables decisions** - Having this context improves decision quality ✅ **Reveals relationships** - Shows connections not visible in source systems ✅ **Persistent** - Relatively stable information (not changing hourly) ✅ **Cross-system** - Connects information from multiple sources ✅ **Saves significant time** - Structuring it eliminates repetitive searching

### **Exclude from KB if data is:**

❌ **Ephemeral** - Changes too frequently to maintain (use real-time MCP queries instead) ❌ **One-time reference** - Unlikely to be needed again (keep in source system) ❌ **Fully contained elsewhere** - Source system already provides good queryability ❌ **Detailed content** - Full documents belong in their source systems (KB just links to them) ❌ **Redundant** - Information derivable from other KB data ❌ **Low-value** - Cost of maintaining exceeds benefit of having it

---

## What This Means for Your KB Population

Based on the 100x project context and your needs:

### **High Priority for KB (Populate First):**

**People Database**

- Name, contact info, relationship type, trust level
- Communication preferences, key context
- Links to projects they're involved in
- Notable interactions and relationship history
  **Projects Database**
- Active projects with status, priority, progress
- Key stakeholders and their roles
- Goals, deadlines, blockers
- Links to relevant resources and documents
  **Resources Database**
- Tools, platforms, services you use
- Access details, costs, integration status
- Which projects use which resources
- Evaluation notes and decisions
  **Intelligence Database**
- Key learnings, methodologies, frameworks
- Technical discoveries and decisions
- Best practices and patterns
- Failed experiments (what didn't work and why)
  **Journal Database**
- Significant meetings, decisions, milestones
- Commitments made and received
- Strategic shifts and turning points
- Context for understanding "why we did X"

### **Lower Priority / Exclude from KB:**

❌ **Full email archive** - Keep in Gmail, query via MCP when needed ❌ **Complete document library** - Keep in Drive, KB just links to key docs ❌ **Calendar events** - Query live via calendar MCP, KB only stores significant meetings ❌ **Task lists** - Keep in ClickUp, query via MCP ❌ **Detailed meeting notes** - Store in source systems, KB contains extracted commitments/decisions ❌ **Media files** - Keep in cloud storage, KB just references them

---

## Practical Test: The "AI Agent Question" Filter

**Before adding something to KB, ask:**

> "If an AI agent needed this information to complete a task, would having it in the KB make the agent more effective than querying the source system?"
> **Examples:**
> ✅ **Unity's phone number** → YES, needed frequently, stable information ✅ **Nick's project goals** → YES, informs many decisions, persistent context
> ✅ **Tool integration status** → YES, affects technical decisions, saves research time ❌ **Yesterday's calendar** → NO, query live calendar via MCP instead ❌ **Full email thread** → NO, keep in Gmail, KB just notes key commitments from it ❌ **Draft document content** → NO, keep in Drive, KB links to it if significant

---

## Purpose-Driven Population Strategy

### **Phase 1: Essential Context (Week 1)**

Populate minimum data needed for AI agents to function:

- Core people (top 10 relationships)
- Active projects (current focus areas)
- Critical resources (tools used daily)
- Key intelligence (recent learnings)
  **Validation:** Can Document Specialist answer basic questions about your work?

### **Phase 2: Relationship Depth (Week 2)**

Add relational context that enables intelligent decisions:

- Connect people to projects
- Link resources to projects
- Add communication preferences
- Document project goals and status
  **Validation:** Can Chief of Staff provide strategic context about priorities?

### **Phase 3: Historical Context (Week 3-4)**

Add backlog that informs pattern recognition:

- Significant meetings/decisions
- Past project outcomes
- Tool evaluation history
- Accumulated intelligence
  **Validation:** Can agents learn from past patterns to inform future decisions?

### **Phase 4: Refinement (Ongoing)**

Continuous improvement based on actual usage:

- Remove data that's never queried
- Add data that you keep looking up manually
- Restructure relationships based on query patterns
- Optimize for actual AI agent needs

---

## Success Metrics (Purpose-Aligned)

Your KB is successful when:
✅ **AI agents can answer 80%+ of context questions** without you providing additional information
✅ **You save 30+ minutes daily** from not searching for information across systems
✅ **Decisions improve** because complete context is readily available
✅ **Relationships strengthen** because you remember key context about people
✅ **Learning accumulates** rather than being forgotten or scattered
✅ **Onboarding accelerates** - new agents/people can understand your context quickly
✅ **Methodology transfers** - process is documented well enough to replicate for clients

---

## Visual Purpose Framework

```scss
SOURCE SYSTEMS (Distributed)
    ↓
KNOWLEDGE BASE (Curated Context Layer)
    ↓
AI AGENTS & HUMAN (Intelligent Actions)
```

**Not this:**

```plain
Everything → KB → Comprehensive Archive
```

**But this:**

```sql
Key Context → KB → Enables Better Decisions
Full Content → Source Systems → Available when needed
```

---

## Decision Framework Summary

**When evaluating what to populate, ask:**

1. **Functional:** Does this enable better AI agent performance?
2. **Relational:** Does this reveal connections across systems?
3. **Persistent:** Is this stable enough to maintain?
4. **Actionable:** Does this inform decisions or actions?
5. **Efficient:** Is KB better than source system for this data?
   **If 3+ answers are YES → Include in KBIf 2 or fewer → Keep in source system, query via MCP when needed**

---

**This purpose definition should guide every population decision. Ready to use this framework to begin Phase 1 data discovery?**
