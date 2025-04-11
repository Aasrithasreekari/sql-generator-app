import json
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load schema from multiple JSON files
def load_schema_from_json(json_paths):
    column_metadata = {}

    for json_path in json_paths:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading {json_path}: {e}")
            continue

        if isinstance(schema_data, dict):
            schema_data = [schema_data]

        for table in schema_data:
            table_name = table.get("tablename")
            if not table_name:
                print(f"Missing 'tablename' in {json_path}, skipping...")
                continue

            fields = table.get("fields", [])
            if not isinstance(fields, list):
                print(f"'fields' should be a list in {json_path}, skipping {table_name}...")
                continue

            cleaned_fields = []
            for field in fields:
                field_name = field.get("field", "").replace(" ", "").replace(".", "")
                datatype = field.get("Datatype", "")
                if field_name:
                    cleaned_fields.append({
                        "name": field_name,
                        "datatype": datatype
                    })

            if cleaned_fields:
                column_metadata[table_name] = cleaned_fields

    return column_metadata

# Generate SQL query using OpenAI
def query_llm(column_metadata, user_prompt):
    context = "Available tables and columns:\n"
    for table_name, fields in column_metadata.items():
        context += f"Table: {table_name}\n"
        for field in fields:
            context += f"  - {field['name']} ({field['datatype']})\n"
        context += "\n"

    full_prompt = (
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
                "content": full_prompt
            }
        ]
    )

    return response["choices"][0]["message"]["content"]

# Run if executed directly
if __name__ == "__main__":
    schema_paths = ["session.json", "registerdusers.json", "appusers.json"]
    user_prompt = "can you tell me how many sessions do users attend on avg per day"

    column_metadata = load_schema_from_json(schema_paths)
    sql_response = query_llm(column_metadata, user_prompt)
    print(sql_response)
