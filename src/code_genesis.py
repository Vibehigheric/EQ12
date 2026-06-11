import os
import json
import argparse
import requests
import re

# Configuration
OPENAI_API_KEY = "OPENROUTER_API_KEY_PLACEHOLDER"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

CODE_GENESIS_SYSTEM = """
You are "Code-Genesis", an AI Software Architect.
Your goal is to take a project description and generate the COMPLETE FILE STRUCTURE and CODE for it.

You must output a SINGLE JSON object representing the file system.
The JSON structure must be:
{
  "project_name": "name_of_project",
  "files": [
    {
      "path": "src/main.py",
      "content": "print('hello world')"
    },
    {
      "path": "requirements.txt",
      "content": "requests\\npandas"
    }
  ]
}

RULES:
1. Include ALL necessary files (README.md, requirements.txt, .gitignore, source code).
2. The code must be functional and production-ready.
3. Do not include markdown formatting around the JSON. Output RAW JSON only.
"""

def generate_codebase(description, output_dir):
    """Generates a full codebase from a description."""
    print(f"🎨 Code-Genesis is architecting: '{description}'...")
    
    payload = {
        "model": "openai/gpt-4o",
        "messages": [
            {"role": "system", "content": CODE_GENESIS_SYSTEM},
            {"role": "user", "content": f"Build this project: {description}"}
        ],
        "response_format": { "type": "json_object" }
    }
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://eq12.cluster", 
        "X-Title": "EQ12 Code-Genesis"
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        content = result['choices'][0]['message']['content']
        project_data = json.loads(content)
        
        project_name = project_data.get("project_name", "generated_project")
        base_path = os.path.join(output_dir, project_name)
        
        print(f"🚀 Building project '{project_name}' in {base_path}...")
        
        for file_obj in project_data.get("files", []):
            file_path = os.path.join(base_path, file_obj["path"])
            file_content = file_obj["content"]
            
            # Create directories
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file_content)
            
            print(f"  + Created: {file_obj['path']}")
            
        print(f"\n✅ Project '{project_name}' created successfully!")
        return base_path
        
    except Exception as e:
        print(f"Error generating codebase: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EQ12 Code-Genesis")
    parser.add_argument("description", help="Description of the software you want to build")
    parser.add_argument("--output", help="Directory to build in", default="c:\\EQ12_BROKEN_20251122_210342\\workspace")
    
    args = parser.parse_args()
    
    generate_codebase(args.description, args.output)
