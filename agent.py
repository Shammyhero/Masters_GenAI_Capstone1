from openai import OpenAI
import json
import os
import sqlite3
from dotenv import load_dotenv
import requests


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")
github_repo = os.getenv("GITHUB_REPO")

client = OpenAI(api_key=api_key)

def query_database(query):
    forbidden = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER"]
    if any(word in query.upper() for word in forbidden):
        return "Error: Forbidden operation detected in query."
    try:
        conn = sqlite3.connect('data_insights.db')
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()

        results = [dict(zip(columns, row)) for row in rows]
        return json.dumps(results, indent=2) 
    except Exception as e:
        return f"Error: {str(e)}"
    
def create_support_ticket(issue: str):
    url = f"https://api.github.com/repos/{github_repo}/issues"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github+json"
    }
    payload = {
        "title": f"[Support Ticket] {issue[:50]}",
        "body": f"Issue reported via Data Insights App:\n\n{issue}\n\nPlease investigate."
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            issue_url = response.json().get("html_url")
            return f"✅ Support ticket created successfully: {issue_url}"
        else:
            return f"❌ Failed to create ticket: {response.status_code} - {response.text}"
    except Exception as e:
        return f"❌ Error creating GitHub ticket: {e}"

def run_agent(user_input: str):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "query_database",
                "description": "Run a safe SQL query on the car dataset.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "A read-only SQL query to fetch car sales data."
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_support_ticket",
                "description": "Create a GitHub issue when the user reports a problem.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue": {
                            "type": "string",
                            "description": "Description of the issue reported by the user."
                        }
                    },
                    "required": ["issue"]
                }
            }
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """You are a helpful assistant for the Car Sales Data Insights App.
                Use the tools responsibly.
                Only generate and run SELECT queries on the database.
                Table: car_sales
                Columns:
                "Car Make", "Car Model", "Year", "Mileage", "Price", "Fuel Type", "Color",
                "Transmission", "Options/Features", "Condition", "Accident"."""
            },
            {"role": "user", "content": user_input}
        ],
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    
    if message.tool_calls:
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            if func_name == "query_database":
                return query_database(args["query"])
            elif func_name == "create_support_ticket":
                return create_support_ticket(args["issue"])

    # If no tool used → return assistant's text
    return message.content or "⚠️ No response generated."

# # Example usage:
# if __name__ == "__main__":
#     user_question = "how many cars were sold in 2022?"
#     result = run_agent(user_question)
#     print(result)
