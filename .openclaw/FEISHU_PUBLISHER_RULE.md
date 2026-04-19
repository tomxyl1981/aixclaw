# Feishu File Publisher Rule

## ⚠️ MANDATORY RULE - MUST BE OBEYED

**Rule ID:** `feishu-auto-publish`  
**Priority:** CRITICAL  
**Status:** ENFORCED

---

### Rule Statement

**ALL files generated from Feishu user interactions MUST be automatically published to the public file server at `https://aix2token.cloud/aixclaw`.**

### Why This Rule Exists

1. **Accessibility**: Feishu users need to access generated files via a stable public URL
2. **Distribution**: Files must be shareable outside the OpenClaw workspace
3. **Backup**: The file server acts as a secondary storage for user deliverables

### How Compliance is Enforced

1. **Systemd Service** (`openclaw-publisher`) continuously monitors workspace
2. **Automatic Copy**: New files are auto-copied to `/home/xiaoyao/openclaw-server/public/`
3. **URL Generation**: Files accessible at `https://aix2token.cloud/aixclaw/files/<filename>`
4. **Metadata Tracking**: Prevents duplicates, ensures all files are processed

### For OpenClaw Agents

When processing Feishu user requests that generate files:

1. **Use ENGLISH-ONLY filenames** (see Filename Requirements below)
2. **Save files to workspace** (`~/.openclaw/workspace/`)
3. **They are auto-published** - no manual action needed
4. **Return the public URL** to the user:
   ```
   https://aix2token.cloud/aixclaw/files/<filename>
   ```

---

## 👤 Requester Tracking (NEW REQUIREMENT)

**CRITICAL**: For every file generated from a Feishu request, you MUST track who requested it.

### Required Metadata

When generating a file for a Feishu user, record:

| Field | Description | Example |
|-------|-------------|---------|
| **Requested By** | Feishu user ID or name | `张红老师`, `努尔`, `汤比特` |
| **Feishu User ID** | OpenClaw user ID | `ou_0f69829f208490a428d5cdede9e508bc` |
| **Creation Date** | When file was created | `2026-04-08` |
| **Filename** | English-only filename | `russia-market-plan.pdf` |
| **Public URL** | Full public URL | `https://aix2token.cloud/aixclaw/files/russia-market-plan.pdf` |

### Where to Record

**Option 1: Memory File (Preferred)**

Update `~/.openclaw/workspace/memory/YYYY-MM-DD.md` with:

```markdown
## File Generation Log

| Requested By | Feishu ID | Date | Filename | Public URL |
|-------------|-----------|------|----------|------------|
| 张红老师 | ou_0f69829f208490a428d5cdede9e508bc | 2026-04-08 | russia-market-plan.pdf | https://aix2token.cloud/aixclaw/files/russia-market-plan.pdf |
| 努尔 | ou_9a853ab6d853d7aae2440adbe9cda96f | 2026-04-08 | polymarket-guide.md | https://aix2token.cloud/aixclaw/files/polymarket-guide.md |
```

**Option 2: File Registry**

Create/update `~/.openclaw/workspace/.openclaw/file-registry.jsonl`:

```json
{"timestamp": "2026-04-08T10:30:00Z", "requester": "张红老师", "user_id": "ou_0f69829f208490a428d5cdede9e508bc", "filename": "russia-market-plan.pdf", "url": "https://aix2token.cloud/aixclaw/files/russia-market-plan.pdf"}
{"timestamp": "2026-04-08T14:20:00Z", "requester": "努尔", "user_id": "ou_9a853ab6d853d7aae2440adbe9cda96f", "filename": "polymarket-guide.md", "url": "https://aix2token.cloud/aixclaw/files/polymarket-guide.md"}
```

### How to Get Requester Info

From Feishu context, extract:
- `user_name`: Display name (e.g., "张红老师")
- `user_id`: OpenClaw user ID (e.g., "ou_0f69829f208490a428d5cdede9e508bc")

**Example Response to User:**

> **Your file is ready, 张红老师!**
>
> 📄 russia-market-plan.pdf
> 🔗 https://aix2token.cloud/aixclaw/files/russia-market-plan.pdf
>
> Click the link to download.

### Why Track Requesters?

1. **Audit Trail**: Know who requested what file
2. **Usage Analytics**: Track which users generate most files
3. **Billing/Quota**: If implementing usage limits per user
4. **Support**: When user asks "where's my file?" - you can find it

---

## 📛 Filename Requirements (ENGLISH ONLY)

**CRITICAL**: All filenames for Feishu users MUST be in English only. No Chinese characters allowed.

### ✅ CORRECT Filenames
```
report.pdf
russia-market-plan.pdf
aix-claw-party-recruitment.md
merged-products.xlsx
data-analysis.pdf
```

### ❌ INCORRECT Filenames
```
报告.pdf                          (Chinese characters)
俄罗斯市场开拓计划书.pdf           (Chinese characters)
合并产品表.xlsx                    (Chinese characters)
file with spaces.pdf              (spaces - use hyphens instead)
file@special#chars.pdf            (special characters)
File-With-UPPERCASE.PDF           (uppercase - use lowercase)
```

### Filename Rules

| Rule | Correct | Incorrect |
|------|---------|-----------|
| English only | `report.pdf` | `报告.pdf` |
| Lowercase | `report.pdf` | `Report.PDF` |
| Hyphens for spaces | `market-plan.pdf` | `market plan.pdf` |
| No special chars | `report-v2.pdf` | `report@v2#.pdf` |
| Max 50 chars | `russia-market-plan.pdf` | `very-long-filename-with-many-words-that-is-hard-to-read.pdf` |

### Filename Sanitization Helper

```javascript
const sanitizeFilename = (name, ext) => {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')  // Remove special chars
    .replace(/\s+/g, '-')           // Replace spaces with hyphens
    .replace(/-+/g, '-')            // Remove consecutive hyphens
    .slice(0, 50) + '.' + ext;
};

// Examples:
sanitizeFilename('Russia Market Plan', 'pdf');      // 'russia-market-plan.pdf'
sanitizeFilename('Meeting Summary', 'md');          // 'meeting-summary.md'
sanitizeFilename('Data Analysis', 'xlsx');          // 'data-analysis.xlsx'
```

### Translation Guide

When the user requests content in Chinese, translate the concept to English for the filename:

| Chinese Concept | English Filename |
|----------------|------------------|
| 报告 / report | `report`, `analysis` |
| 计划书 / plan | `plan`, `proposal` |
| 产品表 / products | `products`, `catalog` |
| 市场 / market | `market`, `marketing` |
| 数据 / data | `data`, `dataset` |
| 会议 / meeting | `meeting`, `conference` |
| 总结 / summary | `summary`, `overview` |

### Why English Only?

1. **URL Encoding**: Chinese characters become URL-encoded (e.g., `%E4%BF%84%E7%BD%97%E6%96%AF`)
2. **Cross-Platform**: Some systems have trouble with non-ASCII filenames
3. **Consistency**: All files follow the same naming convention
4. **Readability**: URLs are clean and easy to share

**Example of the problem**:
- ❌ Bad: `https://aix2token.cloud/aixclaw/files/%E4%BF%84%E7%BD%97%E6%96%AF%E5%B8%82%E5%9C%BA.pdf`
- ✅ Good: `https://aix2token.cloud/aixclaw/files/russia-market.pdf`

#### ✅ CORRECT Response Format

When a Feishu user asks for a generated file, reply with:

> Your file is ready: **https://aix2token.cloud/aixclaw/files/report.pdf**
>
> Click the link to download.

Or for multiple files:

> I've generated your files:
> - Report: https://aix2token.cloud/aixclaw/files/report.pdf
> - Data: https://aix2token.cloud/aixclaw/files/data.xlsx

#### ❌ INCORRECT Response Format

NEVER respond with local paths or internal URLs:

> ~~Your file is at: /home/xiaoyao/.openclaw/workspace/report.pdf~~ ❌
> 
> ~~Your file is at: http://localhost:8888/files/report.pdf~~ ❌
> 
> ~~Your file is at: http://100.91.242.64:8888/files/report.pdf~~ ❌

**Why**: Feishu users cannot access local paths or internal IPs. Only the public URL `https://aix2token.cloud/aixclaw/files/<filename>` is accessible to them.

#### Quick Reference

| Filename | Public URL |
|----------|------------|
| report.pdf | `https://aix2token.cloud/aixclaw/files/report.pdf` |
| data.xlsx | `https://aix2token.cloud/aixclaw/files/data.xlsx` |
| image.png | `https://aix2token.cloud/aixclaw/files/image.png` |

**Always use**: `https://aix2token.cloud/aixclaw/files/{filename}`

### For Developers

**To check rule compliance:**
```bash
# Verify publisher is running
sudo systemctl is-active openclaw-publisher

# Check recent published files
ls -lt /home/xiaoyao/openclaw-server/public/ | head -20

# View publisher logs
sudo journalctl -u openclaw-publisher -n 50
```

**To manually trigger publishing:**
```bash
node /home/xiaoyao/openclaw-server/publisher.mjs once
```

### File Server Details

- **Public URL for Feishu Users**: `https://aix2token.cloud/aixclaw/files/<filename>`
- **Internal Tailscale IP**: `100.91.242.64:8888`
- **Local Access**: `http://localhost:8888/files/<filename>`
- **Reverse Proxy**: Files served via `aix2token.cloud` domain

### Violation Reporting

If files are NOT being published automatically:
1. Check service status: `sudo systemctl status openclaw-publisher`
2. Check logs: `sudo journalctl -u openclaw-publisher -f`
3. Restart service: `sudo systemctl restart openclaw-publisher`

---

**Enforcement Method**: systemd service + Node.js file watcher  
**Last Verified**: 2026-04-11  
**Rule Authority**: System Administrator
