# Core AGentic AI
# 1. Observe
# 2. Detect
# 3. Decide
# 4. ACt

import subprocess

def run_tests():
    result = subprocess.run(
        ["pytest"],
        capture_output = True
        text = True
    )
    return result.stdout

def detect_failure(log):
    return "FAILED in log or "ERROR" in log"

def analyze_log(log):
    response = client.chat.completions.create(
        model = "gpt-4.1-mini", 
        messages= [
            {"role": "system", "content" = "You are DevOps expert"},
            {"role" = "user", "content": f"Analyze the following test log and provide a detailed explanation of the failure: {log}" }
        ]
    )
    return response.choices[0].message.content


def agent():
    log = run_tests()

    print("----------TEST RESULTS----------")
    print(log)

    if detect_failure(log):
        print("\n❌ Tests failed. Analyzing...\n")
        explaintaion = analyze_log(log)
        print("Explanation:")
        print(explaintaion)

    else:
        print("\n✅ Tests passed")
