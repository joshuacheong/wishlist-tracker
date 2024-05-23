from github import Github
import re

# Initialize GitHub client
g = Github("your_github_token")

# Regex pattern to match wish format
pattern = re.compile(r"I wish for (https://github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+/issues/\d+)")

# Your repo
repo = g.get_repo("paritytech/polkadot-sdk")

# Get the issue where wishes are collected
issue_number = 3900  # Change this to your issue number
issue = repo.get_issue(number=issue_number)

# Parse comments for wishes
wishes = {}
for comment in issue.get_comments():
    urls = pattern.findall(comment.body)
    for url in urls:
        if url in wishes:
            wishes[url] += 1
        else:
            wishes[url] = 1

# Sort wishes by count
sorted_wishes = sorted(wishes.items(), key=lambda x: x[1], reverse=True)

# Prepare markdown table
md_table = "| Feature Request | Votes |\n| --- | --- |\n"
for wish, count in sorted_wishes:
    md_table += f"| {wish} | {count} |\n"

# Fetch and update README.md
readme = repo.get_contents("README.md")
current_readme_content = readme.decoded_content.decode()
new_readme_content = leaderboard_section_pattern.sub(f"<!-- LEADERBOARD:START -->\n{md_table}<!-- LEADERBOARD:END -->", current_readme_content)
repo.update_file(readme.path, "Update leaderboard", new_readme_content, readme.sha)