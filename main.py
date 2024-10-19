import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests

app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Data store for logging requests and responses
log_data = []

class Email(BaseModel):
    subject: str
    description: str | None = None

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@app.post("/webhook")
async def handle_webhook(email: Email):
    # Extract relevant details from the email object
    subject = email.subject
    description = email.description or ""
    
    prompt = description + " Generate a response to the user query."
    
    # Generate a response using GPT-4 model
    response = requests.post(
        "https://llmfoundry.straive.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}:freshdesk_test"},
        json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
    )

    # Extract the generated response text
    generated_text = response.json()['choices'][0]['message']['content']

    # Store the logged information
    log_data.append({
        "subject": subject,
        "description": description,
        "response": generated_text
    })

    # Redirect to the log page
    return RedirectResponse(url="/log", status_code=303)

@app.get("/log")
async def display_log(request: Request):
    # Render the log.html template with log_data
    return templates.TemplateResponse("log.html", {"request": request, "log_data": log_data})

# Home route for form submission (optional)
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("log.html", {"request": request, "log_data": log_data})
