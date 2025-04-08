import spacy
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables and spaCy model
load_dotenv()
nlp = spacy.load("en_core_web_sm")

# Database config
DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT", 5432),
}

# Define categories and keywords (you can improve this with LLMs later)
CATEGORIES = {
    "Recon": ["recon", "information gathering", "scan"],
    "Exploitation": ["exploit", "payload", "shell", "bypass"],
    "OSINT": ["osint", "open-source intelligence", "social media", "metadata"],
    "Forensics": ["forensics", "memory analysis", "disk image", "registry"],
    "Malware Analysis": ["malware", "reverse", "obfuscation", "unpack", "detonate"],
    "Network Security": ["sniff", "packet", "tcpdump", "wireshark"],
    "Web Security": ["xss", "sqli", "csrf", "http", "burp", "zap"],
    "Mobile Security": ["android", "ios", "apk", "mobile", "reverse"],
    "Cryptography": ["encryption", "hashing", "cipher", "key", "crypto"],
    "Cloud Security": ["cloud", "aws", "azure", "gcp", "s3"],
    "Red Teaming": ["red team", "evasion", "c2", "command and control"],
    "SOC/IR": ["incident response", "detection", "alert", "SIEM", "splunk", "elk", "SOC"],
    "IoT Security": ["iot", "firmware", "esp", "arduino", "embedded"],
    "Hardware Security": ["hardware", "side-channel", "jtag", "debug"],
    "Industrial Security": ["scada", "ics", "industrial control"],
    "Compliance": ["compliance", "gdpr", "pci", "iso"],
    "Threat Intelligence": ["threat intel", "ioc", "tactic", "technique"],
    "Vulnerability Assessment": ["vuln", "vulnerability", "assessment", "scan"],
    "Exploit Development": ["exploit dev", "fuzz", "pwn", "rop"],
    "Blockchain Security": ["blockchain-security", "smart contract", "solidity", "evm"]
}

def categorize_text(text):
    doc = nlp(text.lower())
    for category, keywords in CATEGORIES.items():
        if any(keyword in doc.text for keyword in keywords):
            return category
    return "Uncategorized"

async def categorize_repos():
    conn = await asyncpg.connect(**DB_CONFIG)
    repos = await conn.fetch("SELECT id, readme, description FROM github_repos WHERE category IS NULL")

    for record in repos:
        readme = record["readme"] or ""
        description = record["description"] or ""

        full_text = f"{description}\n{readme}"
        category = categorize_text(full_text)

        # Short summary using spaCy (extract first few meaningful lines)
        summary_doc = nlp(readme.strip().replace("\r", " ").replace("\n", " "))
        summary = summary_doc.text[:300] if summary_doc.text else None

        # Optional: Extract topics from README (e.g., based on tags seen in the crawler)
        detected_topics = []
        for tag in CATEGORIES.keys():
            if tag.lower() in full_text.lower():
                detected_topics.append(tag)

        await conn.execute(
            """
            UPDATE github_repos 
            SET category = $1, summary = $2, topics = $3 
            WHERE id = $4
            """,
            category, summary, detected_topics if detected_topics else None, record["id"]
        )

    await conn.close()
    print("✅ Categorization completed.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(categorize_repos())
