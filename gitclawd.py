import requests
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from dotenv import load_dotenv
import os
import anthropic

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())
claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="GitHub repos with Claude AI 👁️"
    ))
    print(f'{bot.user} successfully logged in!')
    await bot.tree.sync()

@bot.tree.command(name="analyze", description="🤖 GitClawd — AI-powered GitHub Repo Analyzer")
@app_commands.guild_only()
async def analyze(interaction: discord.Interaction, url: str):
    try:
        split_url = url.split('/')
        if len(split_url) < 5 or 'github.com' not in split_url[2]:
            await interaction.response.send_message("❌ Invalid URL. Use: `https://github.com/owner/repo`", ephemeral=True)
            return
        owner = split_url[3]
        repo = split_url[4].split('?')[0]
    except Exception:
        await interaction.response.send_message("❌ Could not parse that URL.", ephemeral=True)
        return
    await get_repo_data(interaction, url, owner, repo)

def get_headers():
    return {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

async def get_repo_data(interaction, repourl, owner, repo):
    await interaction.response.defer(ephemeral=False)
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 404:
        await interaction.followup.send("❌ Repository not found. Make sure it's public.")
        return
    if response.status_code == 403:
        await interaction.followup.send("❌ GitHub API rate limit. Add a GITHUB_TOKEN to your `.env`.")
        return
    if response.status_code != 200:
        await interaction.followup.send(f"❌ Error: {response.json().get('message', 'Unknown error')}")
        return

    data = response.json()
    loading_message = await interaction.followup.send(content="🔍 Fetching closed issues...", wait=True)

    await loading_message.edit(content="🔍 Fetching closed issues...")
    closed_issues = get_paginated_results(url + '/issues?state=closed&')
    await loading_message.edit(content="📊 Fetching open PRs...")
    open_pull_request = get_paginated_results(url + '/pulls?state=open&')
    await loading_message.edit(content="📈 Fetching closed PRs...")
    closed_pull_request = get_paginated_results(url + '/pulls?state=closed&')
    await loading_message.edit(content="✨ Fetching commits...")
    commits = get_paginated_results(url + '/commits?')
    await loading_message.edit(content="🧠 Claude is analyzing the repo...")

    forks_count = data["forks_count"]
    stars_count = data["stargazers_count"]
    open_issues_count = data["open_issues_count"]
    closed_issues_count = len(closed_issues)
    all_issue_count = open_issues_count + closed_issues_count
    open_pr_count = len(open_pull_request)
    closed_pr_count = len(closed_pull_request)
    all_pr_count = open_pr_count + closed_pr_count
    total_commits = len(commits)

    issue_resolution_rate = round((closed_issues_count / all_issue_count) * 100, 2) if all_issue_count > 0 else 0
    merged_pr_count = get_merged_pull_request_count(open_pull_request, closed_pull_request)
    pr_merge_rate = round((merged_pr_count / all_pr_count) * 100, 2) if all_pr_count > 0 else 0
    authenticity_score = calculate_score(stars_count, forks_count, open_issues_count, closed_issues_count, open_pr_count, closed_pr_count)
    code_uniqueness = get_code_uniqueness(commits)
    languages = get_languages(owner, repo)
    last_update_timestamp = format_timestamp(data.get("updated_at"))
    last_commit_timestamp = format_timestamp(data.get("pushed_at"))
    readme_content = get_readme(owner, repo)

    ai_analysis = await get_claude_analysis(
        owner=owner, repo=repo, description=data.get("description", "No description"),
        stars=stars_count, forks=forks_count, open_issues=open_issues_count,
        closed_issues=closed_issues_count, total_commits=total_commits, languages=languages,
        issue_resolution_rate=issue_resolution_rate, pr_merge_rate=pr_merge_rate,
        readme=readme_content, authenticity_score=authenticity_score
    )

    embed = discord.Embed(title=f"🤖 GitClawd Analysis: {owner}/{repo}", url=repourl, color=0x6e40c9)
    embed.set_footer(text="Powered by Claude AI · GitClawd")
    embed.add_field(name="⭐ Authenticity Score", value=f"`{authenticity_score}/100`", inline=True)
    embed.add_field(name="🔬 Code Uniqueness", value=code_uniqueness, inline=True)
    embed.add_field(name="📦 Total Commits", value=f"`{total_commits}`", inline=True)
    community = (f"Open Issues: `{open_issues_count}/{all_issue_count}`\nOpen PRs: `{open_pr_count}/{all_pr_count}`\n"
                 f"Resolution Rate: `{issue_resolution_rate}%`\nPR Merge Rate: `{pr_merge_rate}%`")
    embed.add_field(name="👥 Community Engagement", value=community, inline=True)
    embed.add_field(name="📌 About", value=f"⭐ Stars: `{stars_count}`\n🍴 Forks: `{forks_count}`", inline=True)
    if languages: embed.add_field(name="💻 Languages", value=f"`{languages}`", inline=False)
    if last_update_timestamp: embed.add_field(name="🕐 Last Update", value=last_update_timestamp, inline=False)
    if last_commit_timestamp: embed.add_field(name="🔀 Last Commit", value=last_commit_timestamp, inline=False)
    embed.add_field(name="🧠 Claude's AI Analysis", value=ai_analysis, inline=False)

    await loading_message.edit(content="", embed=embed)

async def get_claude_analysis(owner, repo, description, stars, forks, open_issues,
                               closed_issues, total_commits, languages, issue_resolution_rate,
                               pr_merge_rate, readme, authenticity_score):
    prompt = f"""You are GitClawd, an AI assistant specialized in analyzing GitHub repositories.
Give a concise, sharp, insightful summary (max 280 characters) for a Discord embed field.
Focus on: project quality, community health, and a brief honest verdict. Be direct and useful.

Repository: {owner}/{repo} | Description: {description}
Stars: {stars} | Forks: {forks} | Commits: {total_commits}
Languages: {languages}
Issue Resolution Rate: {issue_resolution_rate}% | PR Merge Rate: {pr_merge_rate}%
Authenticity Score: {authenticity_score}/100
README: {readme[:800] if readme else 'Not available'}

Respond with ONLY the analysis. No intro, no labels. Max 280 characters."""

    message = claude.messages.create(
        model="claude-opus-4-6", max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

def get_readme(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    r = requests.get(url, headers=get_headers())
    if r.status_code == 200:
        import base64
        try: return base64.b64decode(r.json().get("content", "")).decode("utf-8")
        except: return ""
    return ""

def format_timestamp(iso_str):
    if not iso_str: return None
    ts = int(datetime.fromisoformat(iso_str).timestamp())
    return f"<t:{ts}:f> (<t:{ts}:R>)"

def get_paginated_results(url):
    results, page = [], 1
    while True:
        r = requests.get(f"{url}per_page=100&page={page}", headers=get_headers())
        if r.status_code != 200: break
        data = r.json()
        if not isinstance(data, list) or not data: break
        results.extend(data)
        page += 1
    return results

def get_code_uniqueness(commits):
    if not commits: return "⚠️ No commits found."
    return "✅ No significant similarities." if len(set(c["sha"] for c in commits)) == len(commits) else "❌ Similarities detected."

def get_merged_pull_request_count(open_prs, closed_prs):
    return sum(1 for pr in open_prs + closed_prs if pr.get('merged_at'))

def calculate_score(stars, forks, open_issues, closed_issues, open_prs, closed_prs):
    all_prs = open_prs + closed_prs
    score = (0.3*(stars/(stars+1)) + 0.3*(forks/(forks+1)) +
             0.2*(1-(open_issues/(open_issues+closed_issues+1))) + 0.2*(all_prs/(all_prs+1))) * 100
    return round(score, 2)

def get_languages(owner, repo):
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/languages", headers=get_headers())
    return ', '.join(r.json().keys()) if r.status_code == 200 else ""

bot.run(TOKEN)
