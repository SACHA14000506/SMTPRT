import os
import time
import re
import string
import subprocess
from openai import OpenAI
import tempfile
import src.settings as settings
import random

generation_config = {
    "temperature": 0.9,
    "top_p": 0.9,
    "max_tokens": 10000,
    "frequency_penalty": 1.5,
    "presence_penalty": 0.3,
    "stop": ["timestamp"]
}
client = OpenAI(
    api_key=os.environ.get("ARK_API_KEY"),
    base_url="your url",
)

def generate_smt2_content(prompt, max_retries=20, retry_delay=5):
    attempt = 0
    while attempt < max_retries:
        try:
            response = client.chat.completions.create(
                model="your model",
                messages=[{"role": "user", "content": prompt}],
                **generation_config
            )
            if hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                raise ValueError("Unexpected response format")
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
            attempt += 1
            time.sleep(retry_delay)
    raise RuntimeError(f"Failed to generate content after {max_retries} attempts")

def cleaned(content):
    start = content.find('{')
    end = content.rfind('}')
    if start == -1 or end == -1:
        return ""
    extracted_content = content[start:end + 1]
    cleaned_content = extracted_content.replace("; ", "")
    return cleaned_content

def mutate_smt2_v2(original_smt2):
    folder_path = "/home/cass/Webstorm_project/SMTPRT/src/prompt"
    file_name = settings.theory

    file_path = f'{folder_path}/{file_name}'
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            prompt = file.read()
    except FileNotFoundError:
        print(f"NOT FIND {file_path} ")
    except Exception as e:
        print(f"error：{e}")

    start = time.time()
    it = 0
    smt2_content = generate_smt2_content(prompt)
    smt2_content = cleaned(smt2_content)
    end = time.time()
    print(f"Mistral API call took: {(end - start):.4f} seconds")
    return smt2_content

def generate_mutated_smt2_v2(original_smt2):
    mutated_smt2 = mutate_smt2_v2(original_smt2)
    return mutated_smt2
