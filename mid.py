import os
import json
import openai
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origin(s) in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for request body
class QueryRequest(BaseModel):
    schema_files: List[str]
    user_prompt: str

# Load table schema from multiple JSON files
def load_schema_from_json(json_paths: List[str]) -> dict:
    column_metadata = {}

    for path in json_paths:
        if not os.path.exists(path):
            print(f"[Warning] File not found: {path}")
            continue

        try:
            with open(path, "r", encoding="utf-8") as f:
                schema_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[Error] JSON decode error in {path}: {e}")
            continue

        if isinstance(schema_data, dict):
            schema_data = [schema_data]

        for table in schema_data:
            table_name = table.get("tablename")
            if not table_name:
                print(f"[Warning] Missing 'tablename' in {path}, skipping entry.")
                continue

            fields = table.get("fields", [])
            if not isinstance(fields, list):
                print(f"[Warning] Invalid 'fields' in {table_name}, skipping table.")
                continue

            cleaned_fields = [
                {
                    "name": field.get("field", "").replace(" ", "").replace(".", ""),
                    "datatype": field.get("Datatype", "")
                }
                for field in fields
                if field.get("field")
            ]

            if cleaned_fields:
                column_metadata[table_name] = cleaned_fields

    return column_metadata

# Generate SQL query using OpenAI
def query_llm(column_metadata: dict, user_prompt: str) -> str:
    context = "Available tables and columns:\n"
    for table, fields in column_metadata.items():
        context += f"Table: {table}\n"
        for field in fields:
            context += f"  - {field['name']} ({field['datatype']})\n"
        context += "\n"

    prompt = (
        f"{context}\n"
        f"User Question: {user_prompt}\n\n"
        f"Using the above tables and fields, write a SQL query that answers the user's question. "
        f"Search across all tables if needed. Do not assume missing fields. Infer based on naming patterns if appropriate. "
        f"Output only the SQL query. Do not include explanation."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful SQL assistant. You can use any of the tables and fields provided to generate the query. "
                    "Search across all tables if needed. Don't ask for clarification. Just output the best possible SQL query using available data."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["choices"][0]["message"]["content"]

# POST endpoint for SQL generation
@app.post("/generate-sql")
def generate_sql(req: QueryRequest):
    column_metadata = load_schema_from_json(req.schema_files)
    if not column_metadata:
        raise HTTPException(status_code=400, detail="No valid schema data found.")

    try:
        sql_query = query_llm(column_metadata, req.user_prompt)
        return {"sql_query": sql_query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
