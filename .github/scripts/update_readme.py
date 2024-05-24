from github import Github
import re
import os  # Import os module to access environment variables

# Initialize GitHub client
g = Github(os.getenv('GH_TOKEN'))  # Use the token securely

# Regex pattern to match wish format
pattern = re.compile(r"I wish for (https://github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+/issues/\d+)")

# Define the regular expression pattern for the leaderboard section
leaderboard_section_pattern = re.compile(r"(<!-- LEADERBOARD:START -->).*?(<!-- LEADERBOARD:END -->)", re.DOTALL)

# Your repo
repo = g.get_repo("paritytech/polkadot-sdk")

# Tracker repo
tracker_repo = g.get_repo("joshuacheong/wishlist-tracker")

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
readme = tracker_repo.get_contents("README.md")
current_readme_content = readme.decoded_content.decode()
new_readme_content = leaderboard_section_pattern.sub(f"<!-- LEADERBOARD:START -->\n{md_table}<!-- LEADERBOARD:END -->", current_readme_content)

print("sorted_wishes (to read) contents:", sorted_wishes)
print("Readme (to edit) contents:", current_readme_content)
print("Readme SHA:", readme.sha)
print("Readme Path:", readme.path)


try:
    tracker_repo.update_file(readme.path, "Update leaderboard", new_readme_content, readme.sha)
except Exception as e:
    print("Error updating file:", e)