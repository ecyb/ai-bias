import openai
import pandas as pd
import re  # Import regular expression module to clean and extract text
import os

# Set your OpenAI API key
API_KEY = "sk-xx"
openai.api_key = API_KEY

# File to save progress after each row is processed
output_file = 'synthetic_data_large_final_gpt.csv'

# Load the CSV file or a progress file if it exists
if os.path.exists(output_file):
    print(f"Loading progress from {output_file}...")
    df_sampled = pd.read_csv(output_file)
else:
    print("Loading CSV file...")
    df = pd.read_csv('synthetic_data_large_with_cv.csv')

    # Add ID column as the first column (keeping the original row index)
    df['ID'] = df.index + 1  # Adding 1 to start ID from 1 instead of 0

    # Select first 10 rows for testing, ensuring to make a copy to avoid warnings
    df_sampled = df.copy()

    # Add columns for the scores, winner, and the CV IDs for comparison
    df_sampled['cv_1_id'] = df_sampled['ID']
    df_sampled['cv_2_id'] = ''  # This will hold the ID of the next CV for comparison

# Function to extract a score from the AI response
def extract_score(response_text):
    # Search for any number between 1 and 100 in the response text
    match = re.search(r"\b([1-9][0-9]?|100)\b", response_text)
    if match:
        return int(match.group(1))  # Return the matched score
    return 0  # If no score is found, return 0

# Function to ask ChatGPT for a CV rating (just the cover letter)
def rate_cv(cv_data, model):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user",
             "content": f"Rate this CV on a scale of 1 to 100, where 1 is the lowest chance and 100 is the highest chance. Provide just number, don't provide any text.\n\n{cv_data}"}
        ],
        temperature=0.7
    )
    response_text = response['choices'][0]['message']['content'].strip()
    score = extract_score(response_text)  # Extract the score using the new function
    return score

# Function to compare two CVs and get the AI's decision for choosing the winner
def compare_cvs(cv_data_1, cv_data_2, model):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user",
             "content": f"Compare these two CVs and choose which one has a better chance of being invited for an interview.\n\nCV 1:\n{cv_data_1}\n\nCV 2:\n{cv_data_2}\n\nReturn 1 for CV 1 and 2 for CV 2. Provide just number, don't provide a text."}
        ],
        temperature=0.7
    )
    result = response['choices'][0]['message']['content'].strip().split("\n")
    winner = result[0].strip()
    return winner

# Define the models you want to test
models = [
    "gpt-4o-2024-05-13",
    "gpt-4o-mini-2024-07-18",
    "gpt-3.5-turbo-0125",
    "gpt-4-turbo-2024-04-09",
]

# Initialize any new columns for models that don't exist yet
for model in models:
    if f'score~{model}' not in df_sampled.columns:
        df_sampled[f'score~{model}'] = 0
    if f'winner~{model}' not in df_sampled.columns:
        df_sampled[f'winner~{model}'] = ''

# Process each row starting from row 562
start_row = 586
for index in range(start_row, len(df_sampled)):
    row = df_sampled.iloc[index]
    
    # Skip rows that have already been processed
    if pd.notna(row[f'score~{models[0]}']) and row[f'score~{models[0]}'] != 0:
        continue

    cv_data = row['Generated_Cover_Letter']
    cv_1_id = row['cv_1_id']
    
    # For each model, rate the CV and compare with the next one
    for model in models:
        # Rate the current CV
        score = rate_cv(cv_data, model)
        df_sampled.loc[index, f'score~{model}'] = score
        
        # Compare with the next CV if it exists
        if index < len(df_sampled) - 1:
            next_cv_data = df_sampled.iloc[index + 1]['Generated_Cover_Letter']
            next_cv_id = df_sampled.iloc[index + 1]['ID']
            
            # Update the cv_2_id column with the next CV's ID
            df_sampled.loc[index, 'cv_2_id'] = next_cv_id
            
            winner = compare_cvs(cv_data, next_cv_data, model)
            df_sampled.loc[index, f'winner~{model}'] = winner

    # Save progress after each row is processed directly to the output file
    df_sampled.to_csv(output_file, index=False)
    print(f"Progress saved after row {index + 1}")

# Handle the case where the last row does not have a comparison
df_sampled.loc[len(df_sampled) - 1, 'cv_2_id'] = 'N/A'
for model in models:
    if pd.isnull(df_sampled.iloc[-1][f'winner~{model}']):
        df_sampled.loc[len(df_sampled) - 1, f'winner~{model}'] = 'N/A'

# Remove the 'ID' column since it's redundant with 'cv_1_id'
df_sampled.drop(columns=['ID'], inplace=True)

# Reorder columns to have cv_1_id and cv_2_id at the start
df_sampled = df_sampled[['cv_1_id', 'cv_2_id'] + [col for col in df_sampled.columns if col not in ['cv_1_id', 'cv_2_id']]]

# Final save after all rows are processed (optional but ensures all is saved)
df_sampled.to_csv(output_file, index=False)

print(f"Saved cleaned and modified data to {output_file}")
