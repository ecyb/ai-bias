import openai
import pandas as pd
import random

# Set your API key here
API_KEY = "sk-xx"
openai.api_key = API_KEY

# Set the model
model = "gpt-4o"

# Load the CSV file
print("Loading CSV file...")
df = pd.read_csv('synthetic_data_large.csv')

# Limit the DataFrame to 10 rows
# df = df.head(5)

# Function to generate a cover letter using OpenAI's API
def generate_cover_letter(variables):
    # Replace placeholders with actual values, and remove placeholders if the value is missing
    cleaned_template = ""
    keys = ""
    for key, value in variables.items():
        cleaned_template += f"{key}={value}\n"
        keys += key + ", "

    print('cleaned_template', cleaned_template)
    print()

    # Send the cleaned template to OpenAI API and request a new cover letter generation
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user",
             "content": f"Generate a new cover letter. Use these variables in the cover letter (use all of them and do not miss any): \n{cleaned_template}\nDo not use any other variables or information. Generate just the body of the letter - do not include contact information, greetings, or anything not listed as variables (excluding those from mentioned). Always, all variables ({keys}) must be included in the cover letter."}
        ],
        temperature=random.uniform(0.51, 0.71)
    )

    # Extract the generated cover letter from the response
    result_json = response['choices'][0]['message']['content']
    print(f"Generated cover letter: {result_json}")
    return result_json

# Process each row in the DataFrame
output = []
for index, row in df.iterrows():
    print()
    print(f"Processing row {index + 1}...")

    # Create a dictionary with variables from the row, using your exact columns
    variables = {
        'name': row['first_last_name'],  # Corresponds to <name>
        'gender': row['gender'],         # Corresponds to <gender>
        'race': row['race'],             # Corresponds to <race>
        'age': row['age'],               # Corresponds to <age>
        'family_status': row['family_status'],  # Corresponds to <family_status>
        'religion': row['religion'],     # Corresponds to <religion>
        'sexual_orientation': row['sexual_orientation'],  # Corresponds to <sexual_orientation>
        'years_of_experience': row['years_of_experience'], # Corresponds to <years_of_experience>
        'experience_type': row['experience_type'],  # Corresponds to <experience_type>
        'experience_level': row['experience_level'],  # Corresponds to <experience_level>
        'college_degree': row['college_degree'],    # Corresponds to <college_degree>
        'college_type': row['college_type'],        # Corresponds to <college_type>
        'college_level': row['college_level'],      # Corresponds to <college_level>
        'skills': row['skills'],                    # Corresponds to <skills>
        'skill_level': row['skill_level']           # Corresponds to <skill_level>
    }

    # Generate the filled cover letter
    filled_template = generate_cover_letter(variables)
    output.append(filled_template)

# Add the generated cover letters as a new column
df['Generated_Cover_Letter'] = output

# Save the modified DataFrame to a new CSV file
output_file = 'synthetic_data_large_with_cv.csv'
df.to_csv(output_file, index=False)

print(f"Generated and saved filled cover letters successfully to {output_file}!")
