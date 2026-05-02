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
                {"role": "system", "content": "You are DevOps expert"},
                {
                    "role": "user",
                    "content": f"Analyze the following test log and provide a detailed explanation of the failure: {log}",
                },
            ],
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
        print("Explanation:")
        print(explaintaion)

        print("----------POST PR COMMENT----------")
        post_pr_comment(f"❌ **Tests Failed**\n\n🧠 AI Analysis:\n{explaintaion}")

    else:
        print("\n✅ Tests passed")

def post_pr_comment(message):
    print("----------POST PR COMMENT----------")

    repo = os.getenv("GITHUB_REPOSITORY")
    token = os.getenv("GITHUB_TOKEN")
    event_path = os.getenv("GITHUB_EVENT_PATH")

    print("Repo:", repo)
    print("Event path:", event_path)

    if not event_path:
        print("No event path found")
        return

    with open(event_path, "r") as f:
        event = json.load(f)

    pr_number = event.get("pull_request", {}).get("number")

    print("PR number:", pr_number)

    if not pr_number:
        print("Not a PR event. Skipping comment.")
        return

    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    data = {
        "body": message
    }

    response = requests.post(url, headers=headers, json=data)

    print("Status:", response.status_code)
    print("Response:", response.text)


if __name__ == "__main__":
    try:
        agent()
    except Exception as e:
        print("Agent error:", str(e))


