import json
import os
import subprocess
import urllib.request

API_URL = "https://models.github.ai/inference/chat/completions"
MODEL = "openai/gpt-4.1"
MAX_CHARS = 12000  # keep the prompt small


def read_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()[-MAX_CHARS:]
    except FileNotFoundError:
        return "(no output)"


def get_diff():
    base = os.environ["BASE_SHA"]
    head = os.environ["HEAD_SHA"]
    result = subprocess.run(
        ["git", "diff", f"{base}...{head}", "--", "app", "tests"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout[:MAX_CHARS]


def ask_model(diff, test_output):
    prompt = (
        "You are a senior code reviewer in a CI pipeline.\n"
        "A pull request FAILED the quality gate. Explain to a student, "
        "in simple Persian, why it failed and how to fix it.\n"
        "Use this format:\n"
        "1. Why the gate failed (1-2 sentences)\n"
        "2. Which functions or lines are the problem\n"
        "3. A short example of a test or fix\n"
        "Be concise and friendly.\n\n"
        f"=== TEST AND COVERAGE OUTPUT ===\n{test_output}\n\n"
        f"=== PR DIFF ===\n{diff}\n"
    )
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 800,
    }).encode()
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    return data["choices"][0]["message"]["content"]


def post_comment(text):
    repo = os.environ["REPO"]
    pr = os.environ["PR_NUMBER"]
    url = f"https://api.github.com/repos/{repo}/issues/{pr}/comments"
    body = json.dumps({"body": text}).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        },
    )
    urllib.request.urlopen(req, timeout=30)


def main():
    diff = get_diff()
    test_output = read_file("test_output.txt")
    review = ask_model(diff, test_output)
    comment = "## 🤖 AI Review\n\n" + review
    post_comment(comment)
    print("Comment posted.")


if __name__ == "__main__":
    main()
