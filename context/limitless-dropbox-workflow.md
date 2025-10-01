# Limitless to Dropbox Workflow Documentation

## Overview

This n8n workflow automatically syncs audio transcriptions from Limitless AI to Dropbox every 15 minutes. It intelligently avoids duplicate uploads by checking existing files and only processes new lifelogs.

## Workflow Purpose

The workflow bridges Limitless AI's lifelog system with Dropbox storage, creating organized text files with YAML frontmatter for personal knowledge management and archival purposes.

## Node Flow

### 1. Every 15 Minutes (Schedule Trigger)

- **Type**: `n8n-nodes-base.scheduleTrigger`
- **Function**: Triggers the workflow every 15 minutes
- **Configuration**: `minutesInterval: 15`

### 2. Fetch Recent Lifelogs (HTTP Request)

- **Type**: `n8n-nodes-base.httpRequest`
- **Function**: Retrieves up to 100 recent lifelogs from Limitless AI API
- **Endpoint**: `https://api.limitless.ai/v1/lifelogs`
- **Parameters**:
  - `limit`: 100
  - `includeMarkdown`: true
  - `includeHeadings`: true
  - `includeContents`: true
- **Authentication**: HTTP Header Auth
- **Retry**: 3 attempts with 2-second delays

### 3. List Existing Dropbox Files (Dropbox)

- **Type**: `n8n-nodes-base.dropbox`
- **Function**: Lists all existing files in `/Conversations/Limitless/` folder
- **Operation**: List folder contents
- **Purpose**: Enables deduplication by identifying already processed lifelogs
- **Error Handling**: `continueOnFail: true` (workflow continues even if Dropbox fails)

### 4. Filter Unprocessed (Smart) (Code Node)

- **Type**: `n8n-nodes-base.code`
- **Function**: Intelligent filtering to identify unprocessed lifelogs
- **Logic**:
  1. Validates Limitless API response structure
  2. Extracts existing lifelog IDs from Dropbox filenames (format: `topic.people.ID.txt`)
  3. Filters out lifelogs that already exist in Dropbox
  4. Returns array of unprocessed lifelogs
- **Output Format**: `{unprocessedLifelogs: [...], totalCount: number}`

### 5. Parse & Format Lifelog (Code Node)

- **Type**: `n8n-nodes-base.code`
- **Function**: Transforms lifelog data into formatted text files
- **Processing**:
  - Generates YAML frontmatter with metadata
  - Creates readable transcript from conversation blocks
  - Generates filename: `{slugified-title}.Me.{lifelog-id}.txt`
  - Handles speaker attribution (defaults "Unknown" to "Me")
- **Output**: Formatted content ready for Dropbox upload

### 6. Upload to Dropbox (with Timestamp) (HTTP Request)

- **Type**: `n8n-nodes-base.httpRequest`
- **Function**: Uploads formatted files to Dropbox with proper timestamps
- **Endpoint**: `https://content.dropboxapi.com/2/files/upload`
- **Features**:
  - Sets `client_modified` timestamp from original lifelog
  - Uses `overwrite` mode for consistent behavior
  - Uploads to `/Conversations/Limitless/` directory
- **Retry**: 2 attempts with 5-second delays

## File Format

### Filename Convention

```
{slugified-topic}.Me.{lifelog-id}.txt
```

Example: `project-discussion.Me.abc123def.txt`

### File Structure

```yaml
---
id: abc123def
date: 2024-01-15T09:30:00.000Z
end_time: 2024-01-15T10:15:00.000Z
duration_minutes: 45
title: Project Discussion
is_starred: false
topics:
  - Project Planning
  - Resource Allocation
source: limitless
updated_at: 2024-01-15T10:16:23.456Z
---

# Project Planning

Me: Let's discuss the new project timeline...

## Resource Allocation

Me: We need to allocate resources for Q2...
```

## Authentication Requirements

### Limitless AI

- **Type**: HTTP Header Authentication
- **Required**: API key in header
- **Credential ID**: `6dOV3wkYeLZAux2b`

### Dropbox

- **Type**: OAuth2
- **Required**: Dropbox app with file access permissions
- **Credential ID**: `IEord86sZ1RjYNtB`

## Error Handling

### Robust Design Features

- **API Validation**: Strict validation of Limitless API response structure
- **Dropbox Resilience**: Continues processing even if Dropbox listing fails
- **Retry Logic**: Automatic retries for network operations
- **Deduplication**: Prevents duplicate uploads through intelligent filtering

### Common Error Scenarios

1. **Limitless API Failure**: Workflow logs detailed error and stops
2. **Dropbox Authentication**: Workflow continues with warning
3. **File Upload Failure**: Retries up to 2 times before failing
4. **Empty Results**: Workflow completes successfully with no action

## Recent Fixes

### ✅ Batch Processing Issue - RESOLVED

**Previous Problem**: The workflow only processed one lifelog per execution, even when multiple unprocessed lifelogs were available.

**Root Cause**: The workflow was bundling all unprocessed lifelogs into a single item, but only processing the first one.

**Solution Applied**:

1. **Modified "Filter Unprocessed (Smart)" node**: Changed the return statement to output each unprocessed lifelog as a separate item:

   ```javascript
   // OLD: Bundled approach
   return [{json: {unprocessedLifelogs: [...], totalCount: X}}];

   // NEW: Individual items approach
   return unprocessedLifelogs.map(lifelog => ({json: lifelog}));
   ```

2. **Updated "Parse & Format Lifelog" node**: Simplified the input access:

   ```javascript
   // OLD: Trying to extract from bundled data
   const lifelog = $input.all()[0].json.unprocessedLifelogs[0];

   // NEW: Direct access to individual lifelog
   const lifelog = $input.first().json;
   ```

**Result**: The workflow now processes ALL unprocessed lifelogs in a single execution with **dramatically richer data**:

### ✅ Data Quality Upgrade - NEW

**Enhancement**: Added individual API calls for each lifelog to get structured content data.

**Key Improvements**:

- **Speaker Attribution**: Precise speaker identification per segment
- **Timing Data**: Start/end timestamps for each utterance
- **Content Structure**: Headings, dialogue, and content types
- **Enhanced Metadata**: Speaker lists, segment counts, data source tracking

**Technical Implementation**: Hybrid approach using batch API for filtering + individual API calls for rich data extraction, dramatically improving LLM analysis capabilities.

## Monitoring and Logs

### Execution Logs

The workflow provides detailed console logging for:

- API response validation
- File filtering decisions
- Processing summaries
- Upload confirmations

### Success Metrics

- Lifelogs fetched from API
- Existing files detected
- New files processed
- Upload confirmations

## Maintenance

### Regular Checks

- Monitor Dropbox storage usage
- Verify credential validity
- Review error logs for API changes
- Test duplicate detection accuracy

### Configuration Updates

- Adjust sync frequency if needed (currently 15 minutes)
- Modify batch size for processing optimization
- Update file naming conventions if required

## Python Alternative

n8n fully supports Python in Code nodes! Here are the key differences and advantages:

### JavaScript vs Python Syntax

| JavaScript       | Python              | Purpose                   |
| ---------------- | ------------------- | ------------------------- |
| `$input.all()`   | `_input.all()`      | Get all input items       |
| `$input.first()` | `_input.first()`    | Get first input item      |
| `$('Node Name')` | `_('Node Name')`    | Access other node data    |
| `console.log()`  | `print()`           | Debug output              |
| `item.json`      | `item.json.to_py()` | Convert to native objects |

### Python Advantages

- **Readability**: Cleaner, more intuitive syntax
- **Data Processing**: Built-in libraries like `datetime`, `re`, `json`
- **Error Handling**: More descriptive exception handling
- **List Comprehensions**: Elegant data transformations

### Example Conversions

**Filter Logic (Python):**

```python
# Get data and convert from JsProxy to native Python
lifelog_data = _('Fetch Recent Lifelogs').first().json.to_py()
dropbox_files = [f.json.to_py() for f in _('List Existing Dropbox Files').all()]

# Extract IDs using list comprehension
existing_ids = [f['name'].split('.')[-2] for f in dropbox_files
                if f.get('name', '').endswith('.txt') and len(f['name'].split('.')) >= 3]

# Filter and return
unprocessed = [log for log in all_lifelogs if log['id'] not in existing_ids]
return [{"json": lifelog} for lifelog in unprocessed]
```

**Date Processing (Python):**

```python
from datetime import datetime
import re

# Clean datetime parsing
start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
duration_minutes = int((end_dt - start_dt).total_seconds() / 60)

# Clean regex operations
dropbox_timestamp = re.sub(r'\.\d{3}Z$', 'Z', end_time)
```

**String Processing (Python):**

```python
import re

def slugify(text):
    text = text.strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return re.sub(r'^-+|-+$', '', text)
```

Python makes the code more readable and maintainable, especially for complex data transformations!
