import aiohttp
import asyncio
import asyncpg
import os
from datetime import datetime, timedelta

# GitHub API details
GITHUB_API_URL = "https://api.github.com/search/repositories"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Store in environment variable
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}" if GITHUB_TOKEN else None
}

# Database connection
DB_CONFIG = {
    "user": os.getenv("DB_USER", "cysearch_user"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "cysearch"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432)
}

# Define the search query
tags = ["security", "pentesting", "cybersecurity", "infosec", "pentest", "osint", 
    "forensics", "malware", "reverse-engineering", "data-forensics",
    "ethical-hacking", "mobile-security", "network-security", "wireless-security",
    "vulnerability-assessment", "web-security", "code-analysis", "exploit-development",
    "iot-security", "cryptography", "hardware-security", "smart-grid", "industrial-security",
    "cloud-security", "compliance", "threat-intelligence", "soc", "blockchain-security",
    "incident-response", "malware-analysis", "threat-hunting", "red-teaming"]
QUERY = " OR ".join([f"topic:{tag}" for tag in tags])

async def fetch_repositories():
    """Fetch repositories from GitHub API."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{GITHUB_API_URL}?q={QUERY}&sort=updated&order=desc&per_page=50", headers=HEADERS) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("items", [])
            else:
                print(f"GitHub API error: {response.status}")
                return []

async def fetch_readme(session, repo):
    """Fetch README content for a given repo."""
    url = repo["url"] + "/readme"
    async with session.get(url, headers=HEADERS) as response:
        if response.status == 200:
            readme_data = await response.json()
            return readme_data.get("content", "").encode("utf-8").decode("base64")
        return ""

async def store_repositories(repos):
    """Store fetched repositories into PostgreSQL."""
    conn = await asyncpg.connect(**DB_CONFIG)
    for repo in repos:
        last_updated = datetime.strptime(repo["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
        if last_updated < datetime.utcnow() - timedelta(days=730):  # Skip repos older than 2 years
            continue
        async with aiohttp.ClientSession() as session:
            readme_content = await fetch_readme(session, repo)
        await conn.execute(
            """
            INSERT INTO github_repos (repo_name, description, stars, forks, last_updated, readme)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (repo_name) DO UPDATE SET last_updated = EXCLUDED.last_updated
            """,
            repo["full_name"], repo["description"], repo["stargazers_count"], repo["forks_count"], last_updated, readme_content
        )
    await conn.close()

async def main():
    repos = await fetch_repositories()
    if repos:
        await store_repositories(repos)
        print("✅ Repositories stored successfully.")
    else:
        print("⚠️ No repositories found.")

if __name__ == "__main__":
    asyncio.run(main())

