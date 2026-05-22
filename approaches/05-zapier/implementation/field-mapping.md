# Field Mapping — GHAzDO Alert → ADO Work Item

> How GHAzDO webhook payload fields map to Azure DevOps work item fields

## Core Field Mapping

| ADO Work Item Field | JSON Path | Source | Transformation |
|---------------------|-----------|--------|----------------|
| **System.Title** | `resource.alertType` + `resource.title` / `resource.secretType` / `resource.advisoryTitle` | Webhook | Prefix with `[GHAzDO-{Type}]` (see Title Rules below) |
| **System.Description** | Multiple fields | Webhook | HTML table with alert details (see Description Template) |
| **System.Tags** | `resource.alertType` + `resource.severity` + computed tag | Webhook | Semicolon-separated: `GHAzDO;{alertType};{severity};GHAzDO-{repo}-{alertId}` |
| **Microsoft.VSTS.Common.Priority** | `resource.severity` | Webhook | Severity-to-Priority mapping (see below) |
| **System.State** | N/A (create) / `resource.state` (close) | Webhook | New → default state; Fixed/Dismissed → Done |
| **System.History** | N/A (create) / computed | Code step | Close comment with reason |
| **System.WorkItemType** | N/A | Config | `Issue` (configurable — can use `Bug` or `Task`) |

---

## Title Rules by Alert Type

| Alert Type | Title Prefix | Title Source Field | Fallback |
|------------|-------------|-------------------|----------|
| `secret` | `[GHAzDO-Secret]` | `resource.secretType` | `"Secret detected"` |
| `code` | `[GHAzDO-CodeScan]` | `resource.title` → `resource.rule.description` | `"Code scanning alert"` |
| `dependency` | `[GHAzDO-Dependency]` | `resource.title` → `resource.advisoryTitle` | `"Dependency alert"` |
| unknown | `[GHAzDO-Alert]` | `resource.title` → `message.text` | `"Security alert"` |

### Examples

| Alert Type | Webhook Data | Resulting Title |
|------------|-------------|-----------------|
| Secret | `secretType: "Amazon AWS Access Key ID"` | `[GHAzDO-Secret] Amazon AWS Access Key ID` |
| Code | `title: "SQL Injection vulnerability"` | `[GHAzDO-CodeScan] SQL Injection vulnerability` |
| Dependency | `advisoryTitle: "Prototype Pollution in lodash"` | `[GHAzDO-Dependency] Prototype Pollution in lodash` |

---

## Severity → Priority Mapping

| GHAzDO Severity | ADO Priority | Priority Name |
|-----------------|-------------|---------------|
| `critical` | 1 | Critical |
| `high` | 1 | Critical |
| `medium` | 2 | High |
| `low` | 3 | Medium |

> Note: ADO Priority values are 1-4 (1=highest). We map to 1-3, leaving 4 (Low) unused since all security alerts warrant at least medium priority.

---

## Tags Format

Tags are semicolon-separated in ADO. The tag string follows this pattern:

```
GHAzDO;{alertType};{severity};GHAzDO-{repoName}-{alertId}
```

### Tag Breakdown

| Tag | Purpose | Example |
|-----|---------|---------|
| `GHAzDO` | Identifies all GHAzDO-created work items | `GHAzDO` |
| `{alertType}` | Alert category for filtering | `secret`, `code`, `dependency` |
| `{severity}` | Severity level for filtering | `critical`, `high`, `medium`, `low` |
| `GHAzDO-{repo}-{alertId}` | **Unique dedup tag** — used for search | `GHAzDO-my-app-42` |

### Dedup Tag

The dedup tag `GHAzDO-{repoName}-{alertId}` is critical:
- **Create Zap:** Searches for existing work items with this tag before creating
- **Close Zap:** Searches for work items with this tag to find what to close
- Must be identical in both Zaps for the workflow to function

---

## Description Template (HTML)

The work item description is an HTML table generated in the Code by Zapier step:

```html
<h3>GHAzDO Security Alert</h3>
<table border="1" cellpadding="5">
  <tr><td><b>Alert Type</b></td><td>{alertType}</td></tr>
  <tr><td><b>Severity</b></td><td>{severity}</td></tr>
  <tr><td><b>Repository</b></td><td>{repoName}</td></tr>
  <tr><td><b>File</b></td><td>{filePath}</td></tr>
  <tr><td><b>Line</b></td><td>{lineNumber}</td></tr>
  <tr><td><b>Alert ID</b></td><td>{alertId}</td></tr>
  <tr><td><b>Tag</b></td><td>{ghasTag}</td></tr>
</table>
<p><a href="{alertUrl}">View Alert in Azure DevOps</a></p>
<hr/>
<p><i>Auto-created by GHAzDO Zapier Integration</i></p>
```

---

## Close Event Field Mapping

| When Closing | Source | ADO Field | Value |
|-------------|--------|-----------|-------|
| State | Config | `System.State` | `Done` (configurable) |
| Comment | `resource.state` | `System.History` | `"Auto-closed: GHAzDO alert resolved/fixed."` or `"Auto-closed: GHAzDO alert dismissed as non-issue."` |

---

## Zapier-Specific Field Access

In Zapier, nested JSON fields are accessed with double underscores:

| JSON Path | Zapier Reference |
|-----------|-----------------|
| `eventType` | `eventType` |
| `resource.alertId` | `resource__alertId` |
| `resource.alertType` | `resource__alertType` |
| `resource.severity` | `resource__severity` |
| `resource.state` | `resource__state` |
| `resource.repository.name` | `resource__repository__name` |
| `resource.location.file` | `resource__location__file` |
| `resource.location.line` | `resource__location__line` |
| `resource.link` | `resource__link` |
| `resource.title` | `resource__title` |
| `resource.secretType` | `resource__secretType` |
| `resource.advisoryTitle` | `resource__advisoryTitle` |
| `resource.rule.description` | `resource__rule__description` |
| `resource.previousState` | `resource__previousState` |

> 💡 Zapier flattens nested objects using `__` (double underscore) as the separator. This is how you reference nested webhook fields in Zap steps.
