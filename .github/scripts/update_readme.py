from github import Github
import re
import os

# Initialize GitHub client
g = Github(os.getenv('GH_TOKEN'))  # Use the token securely

# Regex pattern to match wish format
pattern = re.compile(r"I wish for (https://github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)/issues/(\d+))")

# Define the regular expression pattern for the leaderboard section
leaderboard_section_pattern = re.compile(r"(<!-- LEADERBOARD:START -->).*?(<!-- LEADERBOARD:END -->)", re.DOTALL)

# Your repo
repo = g.get_repo("paritytech/polkadot-sdk")

# Tracker repo
tracker_repo = g.get_repo("joshuacheong/wishlist-tracker")

# Get the issue where wishes are collected
issue_number = 3900  # Change this to your issue number
issue = repo.get_issue(number=issue_number)

# Parse comments for wishes and count likes
wishes = {}
issue_details = {}
for comment in issue.get_comments():
    matches = pattern.findall(comment.body)
    for match in matches:
        url, org, repo_name, issue_id = match
        issue_key = (url, org, repo_name, issue_id)
        # Get the count of thumbs-up reactions for the comment
        thumbs_up_count = sum(1 for reaction in comment.get_reactions() if reaction.content == '+1')
        if issue_key in wishes:
            wishes[issue_key] += thumbs_up_count
        else:
            wishes[issue_key] = thumbs_up_count
            # Fetch the issue to get the title
            temp_repo = g.get_repo(f"{org}/{repo_name}")
            temp_issue = temp_repo.get_issue(int(issue_id))
            issue_details[url] = temp_issue.title  # or temp_issue.body for more detailed summary

# Sort wishes by count
sorted_wishes = sorted(wishes.items(), key=lambda x: x[1], reverse=True)

# Prepare markdown table
md_table = "| Feature Request | Summary | Votes |\n| --- | --- | --- |\n"
for (url, _, _, _), count in sorted_wishes:
    summary = issue_details.get(url, "No summary available")
    md_table += f"| {url} | {summary} | {count} |\n"

# Fetch and update README.md
readme = tracker_repo.get_contents("README.md")
current_readme_content = readme.decoded_content.decode()
new_readme_content = leaderboard_section_pattern.sub(f"<!-- LEADERBOARD:START -->\n{md_table}<!-- LEADERBOARD:END -->", current_readme_content)

# Print information for debugging
print("sorted_wishes (to read) contents:", sorted_wishes)
print("Readme (to edit) contents:", current_readme_content)
print("new_readme_content (edited) contents:", new_readme_content)
print("Readme SHA:", readme.sha)
print("Readme Path:", readme.path)

# Try updating the README
try:
    tracker_repo.update_file(readme.path, "Update leaderboard", new_readme_content, readme.sha)
except Exception as e:
    print("Error updating file:", e)
    if hasattr(e, 'data'):
        print("Error Data:", e.data)  # Printing more detailed error information