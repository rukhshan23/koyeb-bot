import requests

# response_main = requests.get("https://new-courtnay-rukhshans-org-20d6f220.koyeb.app/")
# print('Web Application Response:\n', response_main.text, '\n\n')


data = {"text":"Paper Number: 1\nFeedback: Great Paper.", "user_name":"rukhshan"}
response_llmproxy = requests.post("https://new-courtnay-rukhshans-org-20d6f220.koyeb.app/query", json=data)
print('LLMProxy Response:\n', response_llmproxy.text)
