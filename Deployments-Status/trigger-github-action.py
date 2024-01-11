import requests

url = 'https://api.github.com/repos/adhirajpandey/Deployments-Tracker/dispatches'
headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': 'Bearer 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',
    'X-GitHub-Api-Version': '2022-11-28',
    'Content-Type': 'application/x-www-form-urlencoded'
}

data = {
    'event_type': 'do-something'
}

response = requests.post(url, headers=headers, json=data)

print(response.status_code)
