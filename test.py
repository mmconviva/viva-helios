import requests
import base64

username = "mmitra@conviva.com"
api_token = "ATATT3xFfGF0GhHttPAIRb4cXB_SKPiYc4UIgS7ArHPZigNnpmmBf2GAYM2LO-NXJkiB5goXRmbKqC3jmyYh6SgSraudFc6Hd-NvpCNin2EZrEe2QoxwczQjxbqKXzZQXv6TPE2Il2D91W13fkVEKXRGNiQaMDvblEHT5-0q88XOQTImm-6OPtg=C9F5EB73"
auth_string = f"{username}:{api_token}"
encoded_auth = base64.b64encode(auth_string.encode()).decode()

headers = {
    "Authorization": f"Basic {encoded_auth}",
    "Content-Type": "application/json",
}

response = requests.get("https://conviva.atlassian.net/rest/api/2/issue/VH-1", headers=headers)
print(response.json())