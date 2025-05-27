import requests
import json
from pydantic import BaseModel
import pathlib
import textwrap
import os
import gradio as gr
from openai import OpenAI
from datetime import datetime, timedelta

class AnswerFormat(BaseModel):
    Team_Name1: str
    Team_Name2: str
    final_score: str
    location: str

def get_monday_of_current_week():
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    return monday.strftime('%Y-%m-%d')

def get_sunday_of_current_week():
    today = datetime.now()
    sunday = today + timedelta(days=(6 - today.weekday()))
    return sunday.strftime('%Y-%m-%d')

    # Example usage
#print("Sunday of the current week:", get_sunday_of_current_week())
    # Example usage
#print("Monday of the current week:", get_monday_of_current_week())
    
def perpl_chat_builder(game_input,details_input):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": "Bearer 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"}
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "Be precise and concise."},
            {"role": "user", "content": (
                f"""Tell me about {game_input} games from {get_monday_of_current_week()} to {get_sunday_of_current_week()} and score of the teams. """
                "Please output a JSON object containing the following fields: "
                "Team_Name1, Team_Name2, final_score, location. "
            )},
        ],
        "response_format": {
		    "type": "json_schema",
            "json_schema": {"schema": AnswerFormat.model_json_schema()},
        },
    }
    print(payload)
    response = requests.post(url, headers=headers, json=payload).json()
    if "choices" in response and response["choices"] and "message" in response["choices"][0] and "content" in response["choices"][0]["message"]:
        content = response["choices"][0]["message"]["content"]
        try:
            data = json.loads(content)
            team_names_and_score = {
            "Team_Name1": data.get("Team_Name1"),
            "Team_Name2": data.get("Team_Name2"),
            "final_score": data.get("final_score"),
            }
            print(team_names_and_score)
            return json.dumps(team_names_and_score, indent=4)
        except json.JSONDecodeError:
            return "Invalid JSON received."
    return "No valid response received."
    #print(response["choices"][0]["message"]["content"])

demo=gr.Interface(
    perpl_chat_builder,[
    gr.Dropdown(
        ["NBA","NFL","IPL","FIFA"],multiselect=False,label="Game",info="Select Game",value="NBA"
    ),
    gr.Textbox(
        label="Input Details",
        info="Add details to get game details",
        lines=1,
        value="Tell me about the game and score of the teams."
    )],
    "text",title="Current Game",css="footer {visibility: hidden}",allow_flagging="never",submit_btn=gr.Button("Search")
)

if __name__=='__main__':
    demo.launch()