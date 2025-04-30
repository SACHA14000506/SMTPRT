import os
import time
import subprocess
from mistralai import Mistral
import random
import src.settings as settings

api_key = os.environ.get("MISTRAL_API_KEY")

model = "mistral-large-latest"
client = Mistral(api_key=api_key)

def generate_smt2_content(prompt):
    response = client.chat.complete(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature = 0.9

    )
    if hasattr(response, 'choices') and len(response.choices) > 0:
        return response.choices[0].message.content
    else:
        raise ValueError("Unexpected response format")

def save_to_smt2_file(content):
    start_index = content.find("(set")
    end_index = content.find("(exit)")

    if start_index != -1 and end_index != -1:
        processed_content = content[start_index:end_index + len("(exit)")]
    elif start_index != -1:
        processed_content = content[start_index:]
    elif end_index != -1:
        processed_content = content[:end_index + len("(exit)")]
    else:
        processed_content = content
    return processed_content

def run_z3(file_path):
    result = subprocess.run(['z3', file_path], capture_output=True, text=True)
    return result.stdout

def r1_correct(smt2_content):
    smt2_file_path = 'error.smt2'
    start = time.time()
    error_detected = True
    it = 0
    while error_detected:
        with open(smt2_file_path, 'w') as file:
            file.write(smt2_content)
        z3_output = run_z3(smt2_file_path)
        print(f"Z3 Output: {z3_output}")

        it += 1
        if it < 4:
            if 'error' in z3_output.lower():
                print("Error detected in SMT2 file. Regenerating...")
                prompt = (
                    f"The following SMT2 content produced an error: {z3_output}. "
                    f"Original SMT2 content: {smt2_content}. "
                    "The logic type should be QF_S. The file should contain between 20 to 40 lines. "
                    "Modify the content to fix the error. If too many errors occur, consider changing the variation direction. "
                    "Only include the SMT2 content without any explanatory language."
                )
                smt2_content = generate_smt2_content(prompt)
                smt2_content = save_to_smt2_file(smt2_content)

            else:
                error_detected = False
        else:
            if 'error' in z3_output.lower():
                random_number = random.randint(1, 99999)
                file_name = f"error_{random_number}.smt2"
                error_folder = "error"
                if not os.path.exists(error_folder):
                    os.makedirs(error_folder)
                full_content = smt2_content + "\n" + z3_output
                file_path = os.path.join(error_folder, file_name)

                with open(file_path, 'w') as file:
                    file.write(full_content)
                print(f"Error content saved to {file_path}")
                folder_path = settings.repo
                smt2_files = [file for file in os.listdir(folder_path) if file.endswith(".smt2")]

                if not smt2_files:
                    print("NOTFOUND")
                else:
                    selected_file = random.choice(smt2_files)
                    file_path = os.path.join(folder_path, selected_file)

                    with open(file_path, "r", encoding="utf-8") as file:
                        smt2_content = file.read()
            else:
                error_detected = False

    end = time.time()
    print(f"Mistral API call took: {(end-start):.4f} seconds")
    return smt2_content

def correct(original_smt2):
    mutated_smt2 = r1_correct(original_smt2)
    return mutated_smt2
