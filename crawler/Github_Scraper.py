import requests
import json
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base

# GitHub API setup
GITHUB_API_URL = "https://api.github.com/search/repositories"
HEADERS = {"Accept": "application/vnd.github.v3+json"}
QUERY_TOPICS = [
    "pentest tool",
    "osint tool", 
    "forensics tool", 
    "malware tool", 
    "reverse-engineering tool",
    "data forensics tool",
    "ethical hacking tool",
    "mobile hacking tool",
    "network attacks tool",
    "Wireless security tool",
    "vulnerability assessment tool",
    "web appsec tool",
    "osint tool",
    "code assessment tool",
    "malware offense tool",
    "iot security tool",
    "cryptography tool",
    "arsenal lab tool",
    "hardware security tool",
    "smart grid tool",
    "industrial control systems tool",
    "embedded security tool",
    "malware defense tool",
    "network defense tool",
    "reverse engineering tool",
    "industrial security tool",
    "cloud security tool",
    "security compliance tool",
    "threat intelligence tool",
    "soc tool",
    "blockchain security tool",
    "incident response tool",
    "malware analysis tool",
    "threat hunting tool",
    "exploit development tool",
    "red teaming tool",
]
DATABASE = "cysearch.db"

# Database setup
DATABASE_URL = "postgresql://cysearch_user:securepassword@localhost:5432/cysearch"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Define database model
class Tool(Base):
    __tablename__ = "tools"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    stars = Column(Integer, nullable=False)
    description = Column(Text)
    readme = Column(Text)
    category = Column(String)

Base.metadata.create_all(engine)


# Fetch repositories from GitHub
def fetch_repos():
    repos = []
    for topic in QUERY_TOPICS:
        params = {"q": f"topic:{topic}", "sort": "stars", "order": "desc", "per_page": 10}
        response = requests.get(GITHUB_API_URL, headers=HEADERS, params=params)
        if response.status_code == 200:
            data = response.json()
            for repo in data.get("items", []):
                repos.append({
                    "name": repo["name"],
                    "url": repo["html_url"],
                    "stars": repo["stargazers_count"],
                    "description": repo.get("description", ""),
                    "readme_url": repo["html_url"] + "/blob/main/README.md"
                })
    return repos

# Extract README content
def fetch_readme(repo_url):
    try:
        response = requests.get(repo_url, headers=HEADERS)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            readme = soup.get_text()
            return readme[:1000]  # Limit to 1000 chars for now
    except Exception as e:
        print(f"Error fetching README: {e}")
    return ""

# Store in PostgreSQL
def save_to_db(repos):
    for repo in repos:
        readme = fetch_readme(repo["readme_url"])
        tool = Tool(name=repo["name"], url=repo["url"], stars=repo["stars"], description=repo["description"], readme=readme, category="Unknown")
        session.add(tool)
    session.commit()

if __name__ == "__main__":
    repos = fetch_repos()
    save_to_db(repos)
    print("Data collection complete!")