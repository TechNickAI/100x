# Cursor Rules Library

Reusable cursor rules for AI-assisted coding. Symlink or copy what you need.

## Organization

Rules organized by topic:

- **Root level** - Universal (git, naming, code style, prompt engineering, user-facing language)
- **`python/`** - Python standards and patterns
- **`django/`** - Django framework conventions
- **`observability/`** - Logging and error tracking
- **`ai/`** - AI development patterns
- **`frontend/`** - Frontend frameworks and tools

Each `.mdc` file is self-contained and works independently.

## How Rules Apply

### Always Applied

Only heart-centered AI philosophy applies to all files.

### Auto-Applied by File Pattern

Some rules trigger automatically based on file globs. Check individual `.mdc` files for patterns. Common triggers:

- Django models, commands, and templates
- Celery tasks
- React components
- Framework-specific files

### Manual Invocation

Most rules get invoked with `@` when you need them, or Cursor applies them intelligently based on context.

## Usage

Set a variable for convenience:

```bash
AI_CONFIG=~/src/ai-coding-config  # adjust to your clone path
```

### Symlink Everything (Easiest)

```bash
ln -s $AI_CONFIG/.cursor .cursor
```

### Cherry-Pick Directories

```bash
mkdir -p .cursor/rules
ln -s $AI_CONFIG/.cursor/rules/python .cursor/rules/python
ln -s $AI_CONFIG/.cursor/rules/django .cursor/rules/django
```

### Copy What You Need

```bash
mkdir -p .cursor/rules
cp $AI_CONFIG/.cursor/rules/*.mdc .cursor/rules/
cp -r $AI_CONFIG/.cursor/rules/python .cursor/rules/
```

## Manual Invocation

Invoke any rule with `@` + rule name (without `.mdc`):

- `@git-commit-message`
- `@python-coding-standards`
- `@django-models`
- `@user-facing-language`

Type `@` in Cursor to browse available rules.

## Customization

**Use as-is** - Symlink and use rules unchanged

**Override** - Create same-named files locally to override specific rules

**Extend** - Add project-specific rules alongside these

**Modify** - Adjust glob patterns in frontmatter as needed

## Philosophy

These rules enforce:

- Heart-centered AI collaboration
- Clear coding standards
- Thoughtful testing and error handling
- Modern Python and framework best practices
- Universal patterns that work across projects
