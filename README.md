# 🧠 SQL Generator App

This is an intelligent SQL query generator powered by OpenAI. It takes schema definitions in JSON format and allows users to ask natural language questions, generating SQL queries as responses. It's ideal for non-technical users, analysts, or developers who want to streamline their workflow.

## 🚀 Features

- Upload one or more schema JSON files
- Ask questions in plain English
- Automatically generates optimized SQL queries using OpenAI's GPT-4
- Clean chat-style interface
- Backend powered by FastAPI

## 🧪 Example

You upload schema files like:
- `users.json`
- `sessions.json`

Then ask:  
**"How many sessions do users attend on avg per day?"**

And the system responds with the correct SQL query based on the uploaded schema.

## 📦 Tech Stack

- **Frontend**: React.js
- **Backend**: FastAPI (Python)
- **AI Engine**: OpenAI's GPT-4
- **Styling**: CSS

## 🔐 API Key Requirement

This app requires an **OpenAI API Key** to function.  
Make sure to create a `.env` file in the backend directory and include:

```env
OPENAI_API_KEY=your_openai_api_key_here


## 📂 How to Run Locally

1. **Clone the repository**

```bash
git clone https://github.com/your-username/sql-generator-app.git
cd sql-generator-app
Install backend dependencies

bash
cd backend
pip install -r requirements.txt
Start FastAPI backend

bash
uvicorn main:app --reload
Start frontend

bash
cd frontend
npm install
npm start
