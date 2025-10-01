# Commitment Manager Agent - Technical Specification

## Agent Purpose and Scope

The Commitment Manager Agent (Sarah the Commitment Manager in reference implementation) ensures nothing you promise falls through the cracks. It monitors all conversations, identifies commitments with their deadlines and stakeholders, and orchestrates follow-through via the project management system.

Sarah understands the difference between a casual "I'll think about it" and a firm "I'll have it to you by Friday." Her personality is methodical but not annoying - she won't nag about vague future possibilities, but she absolutely will ensure that when you tell a client something will be done by Tuesday, it gets done by Tuesday.

### Primary Purpose

The Commitment Manager Agent transforms the exhausting mental load of remembering everything you've promised into a reliable system that ensures completion and maintains stakeholder trust.

---

## Commitment Extraction Intelligence

### Analysis Approach

Sarah analyzes conversations using LLM prompts that distinguish between firm commitments ("I'll send you the proposal by Friday"), soft possibilities ("I should probably update the documentation"), and exploratory discussion ("We might want to consider...").

She extracts specific actions with owners, deadlines, dependencies, and stakeholders. Each commitment receives a confidence score, and only those above the threshold get processed automatically. Lower-confidence items go to human review.

### Nuance Understanding

Sarah's extraction logic understands nuance:

- "I'll try to..." → Lower confidence, might create task but mark as tentative
- "I'll definitely..." → High confidence, create task immediately
- "Let me see if I can..." → Track but don't create task yet
- "I commit to..." → Highest confidence, priority task

### Commitment Requirements

A valid commitment must have:

- A specific action or deliverable
- An explicit or strongly implied agreement to do it
- An owner (who will do it)

Optionally may have:

- A deadline (explicit or contextual)
- Dependencies (what must happen first)
- Stakeholders (who cares about completion)

---

## Task Creation and Assignment

### Task Creation Process

When Sarah identifies commitments, she creates appropriately structured tasks complete with context and smart assignment logic.

She checks if similar tasks already exist to avoid duplicates, then creates new tasks with formatted titles, detailed descriptions, appropriate assignees, calculated deadlines, priority assessments, and tags indicating confidence levels. Tasks include custom fields for tracking the source, stakeholders, creating agent, and whether human review is needed.

If a commitment requires preparation work, Sarah creates those prerequisite tasks automatically with proper dependencies.

### Assignment Logic

Assignment routing is based on commitment type:

- Code or implementation tasks → AI Chief of Staff (Piper delegates internally to code review agent)
- Financial or budget items → AI Chief of Staff (Piper delegates internally to finance agent)
- Research requests → AI Chief of Staff (Piper delegates internally to research agent)
- Personal items → Personal assistant (e.g., Åsa)
- Decision items → The decision maker themselves
- Actionable business items → AI Chief of Staff
- Other owners → Assigned to the person who made the commitment

All AI work appears assigned to the single AI Chief of Staff account. Internal delegation to specialized agents happens invisibly.

---

## Follow-up Tracking

### Active Monitoring

Sarah doesn't just create tasks and forget about them. She actively monitors progress and ensures commitments are met.

Running periodically via Celery, Sarah checks all active commitment tasks. For each task she identifies the status: blocked, overdue, needing check-in, or deadline approaching. Based on status, she takes appropriate action.

### Handling Blocked Tasks

For blocked tasks, she identifies the blocker type:

- **Dependency blocker**: Finds and prioritizes the blocking task while notifying the assignee
- **Missing information**: Creates an information request task and links them
- **Decision needed**: Escalates to the appropriate human

### Status Reporting

Sarah generates daily and weekly status reports showing:

- Commitments made today
- Commitments due today
- Overdue items requiring attention
- Upcoming deadlines (next 3-7 days)
- Completion rate metrics

---

## Integration with Human Workflows

### Review Workflow for Ambiguous Commitments

Sarah understands that not all commitments are equal and that humans need visibility and control. For ambiguous commitments below the confidence threshold, she creates review tasks assigned to the appropriate human (Unity or whoever handles commitment validation).

Review tasks include the commitment description, speaker, source context, and confidence level. They ask the reviewer to approve, modify, or reject the commitment. Based on the human response, Sarah either creates the commitment task, creates it with modifications, or archives the pending commitment.

### Escalation Patterns

Sarah escalates to humans when:

- Commitment confidence is below threshold (< 80-90%)
- Deadline is impossible given dependencies
- Stakeholder conflict detected (two people committed to conflicting things)
- Resource constraint identified (not enough capacity to complete)
- Financial commitment above approval threshold

---

## Learning from Patterns

### Continuous Improvement

Sarah improves over time by learning from patterns in commitment completion and human feedback.

She analyzes completed commitments to track:

- **Typical durations** for different task types
- **Reliability scores** for each person (who consistently meets deadlines)
- **Common blockers** that cause delays
- **Deadline estimation accuracy** across commitment types

These patterns inform future predictions. If research tasks typically take 3 days, Sarah's deadline suggestions reflect that. If someone has a 95% on-time completion rate, their commitments get higher confidence scores.

### Feedback Integration

When humans modify Sarah's extractions or reassign tasks, she learns from those corrections:

- Phrases that seemed like commitments but weren't → Lower future confidence
- Deadline adjustments → Improve future estimation models
- Assignment changes → Refine routing logic for similar future tasks

---

## Success Metrics

The Commitment Manager Agent is successful when:

- **80%+ of commitments from meetings** automatically become tracked tasks
- **Commitment completion rate** improves (fewer missed deadlines)
- **Follow-up efficiency** - Stakeholders get proactive updates before asking
- **Trust increases** - People know you'll deliver because Sarah ensures it
- **Mental load eliminated** - You stop worrying about what you might have forgotten
- **Low false positives** - <10% of extracted "commitments" aren't real commitments
- **Low false negatives** - <5% of real commitments get missed
- **Appropriate escalation** - Humans only see issues that truly need human judgment

## Implementation Notes

**This agent should be built by Forge, not manually.** Create a task describing what the Commitment Manager Agent should do, assign it to AI, and let Forge create the `.agent` file and implementation. The task description should include:

- Data sources to monitor (processed conversations from Knowledge Base Agent)
- Commitment extraction criteria and confidence thresholds
- Task creation requirements and routing rules
- Follow-up monitoring frequency and escalation patterns
- Learning mechanisms for continuous improvement
- Success criteria and quality metrics

Forge will generate the appropriate `.agent` file with system/user prompts, output schema for structured commitment extraction, and the monitoring logic.
