# Core AGentic AI
# 1. Observe
# 2. Detect
# 3. Decide
# 4. ACt

import subprocess
import os
from openai import OpenAI
import requests
import json

client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_tests():
    result = subprocess.run(
        ["pytest"],
        capture_output=True, 
        text=True
    )
    return result.stdout

def detect_failure(log):
    return "FAILED" in log or "ERROR" in log

def analyze_log(log):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior DevOps engineer. Analyze CI failures and suggest fixes."
                },
                {
                    "role": "user",
                    "content": f"""
                    CI FAILED. Analyze and respond in this format:

                    1. Root Cause
                    2. Why it failed
                    3. Suggested Fix (code or steps)

                    Logs:
                    {log}
                    """
                }
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"AI unavailable: {str(e)}"

def agent():
    log = run_tests()

    print("----------TEST RESULTS----------")
    print(log)

    print("----------DETECTING FAILURE----------: ", detect_failure(log))
    if detect_failure(log):
        print("\n❌ Tests failed. Analyzing...\n")
        explaintaion = analyze_log(log)
        message = f"""
        🤖 **AI DevOps Agent Report**

        ❌ Tests Failed

        {explaintaion}

        ---
        _This comment is auto-updated by AI agent_
        """
        try:
            post_pr_comment(message)
        except Exception as e:
            print("Comment failed:", str(e))

    else:
        print("\n✅ Tests passed")

def post_pr_comment(message):
    print("----------POST PR COMMENT----------")

    repo = os.getenv("GITHUB_REPOSITORY")
    token = os.getenv("GITHUB_TOKEN")
    event_path = os.getenv("GITHUB_EVENT_PATH")

    with open(event_path, "r") as f:
        event = json.load(f)

    pr_number = event.get("pull_request", {}).get("number")

    if not pr_number:
        print("Not a PR event")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    # 🔍 Step 1: Get existing comments
    comments_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    response = requests.get(comments_url, headers=headers)
    comments = response.json()

    bot_comment_id = None

    # 🔎 Step 2: Find existing bot comment
    for comment in comments:
        if "🤖 AI DevOps Agent" in comment["body"]:
            bot_comment_id = comment["id"]
            break

    # ✏️ Step 3: Update or Create
    if bot_comment_id:
        print("Updating existing comment...")
        update_url = f"https://api.github.com/repos/{repo}/issues/comments/{bot_comment_id}"
        requests.patch(update_url, headers=headers, json={"body": message})
    else:
        print("Creating new comment...")
        requests.post(comments_url, headers=headers, json={"body": message})


if __name__ == "__main__":
    try:
        agent()
    except Exception as e:
        print("Agent error:", str(e))


