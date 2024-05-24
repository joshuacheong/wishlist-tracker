from github import Github
import re
import os

# Initialize GitHub client
g = Github(os.getenv('GH_TOKEN'))  # Use the token securely

# Regex pattern to match wish format
pattern = re.compile(r"I wish for (https://github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)/issues/(\d+))")

# Define the regular expression pattern for the leaderboard sections
leaderboard_section_pattern_dev = re.compile(r"(<!-- LEADERBOARD_DEV:START -->).*?(<!-- LEADERBOARD_DEV:END -->)", re.DOTALL)
leaderboard_section_pattern_user = re.compile(r"(<!-- LEADERBOARD_USER:START -->).*?(<!-- LEADERBOARD_USER:END -->)", re.DOTALL)

# Repositories and issues
issues = {
    'Developer': ('paritytech/polkadot-sdk', 3900),
    'User': ('paritytech/polkadot-sdk', 3901)
}

# Tracker repo
tracker_repo = g.get_repo("joshuacheong/wishlist-tracker")

# Markdown tables for each category
md_tables = {
    'Developer': "| Feature Request | Summary | Votes |\n| --- | --- | --- |\n",
    'User': "| Feature Request | Summary | Votes |\n| --- | --- | --- |\n"
}

# Process each issue
for category, (repo_name, issue_number) in issues.items():
    repo = g.get_repo(repo_name)
    issue = repo.get_issue(issue_number)
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

    # Sort wishes by count and add to the markdown table
    sorted_wishes = sorted(wishes.items(), key=lambda x: x[1], reverse=True)
    for (url, _, _, _), count in sorted_wishes:
        summary = issue_details.get(url, "No summary available")
        md_tables[category] += f"| {url} | {summary} | {count} |\n"

# Fetch and update README.md
readme = tracker_repo.get_contents("README.md")
current_readme_content = readme.decoded_content.decode()
new_readme_content_dev = leaderboard_section_pattern_dev.sub(f"<!-- LEADERBOARD_DEV:START -->\n{md_tables['Developer']}<!-- LEADERBOARD_DEV:END -->", current_readme_content)
new_readme_content_user = leaderboard_section_pattern_user.sub(f"<!-- LEADERBOARD_USER:START -->\n{md_tables['User']}<!-- LEADERBOARD_USER:END -->", new_readme_content_dev)

# Try updating the README
try:
    tracker_repo.update_file(readme.path, "Update leaderboard", new_readme_content_user, readme.sha)
except Exception as e:
    print("Error updating file:", e)
    if hasattr(e, 'data'):
        print("Error Data:", e.data)  # Printing more detailed error information