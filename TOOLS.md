# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Feishu File Sharing (CRITICAL)

When generating files for Feishu users, always return the public URL:

```
https://aix2token.cloud/aixclaw/files/{filename}
```

### Quick Command

Generate the public URL in code:
```javascript
const filename = "report.pdf";
const publicUrl = `https://aix2token.cloud/aixclaw/files/${encodeURIComponent(filename)}`;
// Result: https://aix2token.cloud/aixclaw/files/report.pdf
```

### Response Template

```
Your file is ready: https://aix2token.cloud/aixclaw/files/{filename}

Click the link to download.
```

### Common File Types

| Extension | Example URL |
|-----------|-------------|
| .pdf | `https://aix2token.cloud/aixclaw/files/document.pdf` |
| .xlsx | `https://aix2token.cloud/aixclaw/files/data.xlsx` |
| .docx | `https://aix2token.cloud/aixclaw/files/report.docx` |
| .png | `https://aix2token.cloud/aixclaw/files/chart.png` |
| .md | `https://aix2token.cloud/aixclaw/files/notes.md` |

**NEVER use**: Local paths (`/home/xiaoyao/...`), `localhost`, or `100.91.242.64` - Feishu users cannot access these!

### Filename Sanitization (ENGLISH ONLY)

When generating files for Feishu, filenames MUST be English-only. Use this helper:

```javascript
const sanitizeFilename = (name, ext) => {
  // Translate common terms
  const translations = {
    '报告': 'report',
    '计划书': 'plan',
    '产品表': 'products',
    '分析': 'analysis',
    '总结': 'summary',
    '数据': 'data',
    '会议': 'meeting',
    '市场': 'market',
    '俄罗斯': 'russia',
    '中国': 'china',
    '美国': 'usa',
    '日本': 'japan',
    '韩国': 'korea'
  };
  
  // Replace known Chinese terms with English
  let english = name;
  for (const [cn, en] of Object.entries(translations)) {
    english = english.replace(new RegExp(cn, 'g'), en);
  }
  
  return english
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')  // Remove non-ASCII chars
    .replace(/\s+/g, '-')           // Replace spaces with hyphens
    .replace(/-+/g, '-')            // Remove consecutive hyphens
    .replace(/^-+|-+$/g, '')        // Remove leading/trailing hyphens
    .slice(0, 50) + '.' + ext;
};

// Examples:
sanitizeFilename('Russia Market Plan', 'pdf');        // 'russia-market-plan.pdf'
sanitizeFilename('Meeting Summary', 'md');            // 'meeting-summary.md'
sanitizeFilename('Data Analysis Report', 'xlsx');     // 'data-analysis-report.xlsx'
```

#### Filename Rules
- ✅ Use English only (no Chinese characters)
- ✅ Use hyphens instead of spaces
- ✅ Use lowercase letters
- ✅ Keep it under 50 characters
- ❌ No special characters: `@#$%^&*()[]{}<>|\\;:'",.?/~+=`

### 👤 Requester Tracking Template

When generating files for Feishu users, record this information:

```markdown
## Generated Files Log - 2026-04-11

| Requested By | User ID | Filename | Public URL |
|-------------|---------|----------|------------|
| {requester_name} | {user_id} | {filename} | https://aix2token.cloud/aixclaw/files/{filename} |
```

**How to get requester info from Feishu context:**
```javascript
// From Feishu message context
const requester = {
  name: message.user.name,           // e.g., "张红老师"
  id: message.user.id,               // e.g., "ou_0f69829f208490a428d5cdede9e508bc"
  displayName: message.user.display_name
};

// Generate filename
const filename = sanitizeFilename('Russia Market Plan', 'pdf');
// -> 'russia-market-plan.pdf'

// Response to user
const response = `**Your file is ready, ${requester.name}!**

📄 ${filename}
🔗 https://aix2token.cloud/aixclaw/files/${filename}

Click the link to download.`;

// Log to memory
const logEntry = `| ${requester.name} | ${requester.id} | ${filename} | https://aix2token.cloud/aixclaw/files/${filename} |`;
// Append to ~/.openclaw/workspace/memory/YYYY-MM-DD.md
```

**Response Example:**

> **Your file is ready, 张红老师!**
>
> 📄 russia-market-plan.pdf
> 🔗 https://aix2token.cloud/aixclaw/files/russia-market-plan.pdf
>
> Click the link to download.

---

Add whatever helps you do your job. This is your cheat sheet.
