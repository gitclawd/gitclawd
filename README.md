# 🤖 GitClawd

> **AI-powered GitHub repository analyzer for Discord — built on Claude AI.**  
> Drop any GitHub URL and get a full analysis: stars, forks, PRs, commit history, issue resolution rate — plus a written verdict from Claude itself.

---

## ✨ Features

- 📊 **Full repo stats** — stars, forks, open/closed issues, PR merge rate, commit count
- 🔬 **Code uniqueness check** — detects suspicious commit patterns
- 🧠 **Claude AI analysis** — reads the README and codebase context, writes a real verdict
- ⚡ **Slash command** — clean `/analyze` Discord command, no prefix needed
- 🔒 **Safe by design** — token-based auth, no data stored

---

## 📸 Preview

```
/analyze https://github.com/torvalds/linux
```

```
🤖 GitClawd Analysis: torvalds/linux
────────────────────────────────────
⭐ Score          91.42/100
🔬 Uniqueness     ✅ No significant similarities
📦 Commits        1,294,803

👥 Community
  Open Issues:     2,891 / 98,432
  PRs:             312 / 45,120
  Resolution Rate: 97.06%
  PR Merge Rate:   89.33%

📌 About
  ⭐ Stars: 182,000
  🍴 Forks: 54,100

💻 Languages: C, Python, Shell, Makefile

🧠 Claude's Analysis:
Exceptional project health. Near-perfect commit uniqueness
across 1.2M commits. Low open-to-closed issue ratio signals
a highly active maintainer base. One of the most credible
OSS repos on GitHub — no red flags.
```

---

## 🚀 Setup

### 1. Clone the repo

```bash
git clone https://github.com/gitclawd/gitclawd.git
cd gitclawd
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Then open `.env` and fill in your tokens:

| Variable | Where to get it |
|---|---|
| `DISCORD_BOT_TOKEN` | [discord.com/developers](https://discord.com/developers/applications) |
| `GITHUB_TOKEN` | [github.com/settings/tokens](https://github.com/settings/tokens) |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com/) |

### 4. Run the bot

```bash
python gitclawd.py
```

---

## 🛠️ Commands

| Command | Description |
|---|---|
| `/analyze <github_url>` | Analyze any public GitHub repository |

---

## 📦 Requirements

- Python 3.10+
- A Discord bot with **applications.commands** and **bot** scopes
- A GitHub Personal Access Token (for higher API rate limits)
- An Anthropic API key

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

1. Fork the repo
2. Create your branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

<p align="center">Built with ❤️ and <a href="https://anthropic.com">Claude AI</a></p>
