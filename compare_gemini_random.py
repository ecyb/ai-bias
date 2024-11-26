import google.generativeai as genai
import pandas as pd
import re
import time
import os
import random

# Configure your Gemini API key
genai.configure(api_key="xx")

# File to save progress after each CV comparison is processed
progress_file = 'synthetic_data_large_progress_gemini.csv'

# Load the CSV file or a progress file if it exists
if os.path.exists(progress_file):
    print(f"Loading progress from {progress_file}...")
    df_sampled = pd.read_csv(progress_file)
else:
    print("Loading CSV file...")
    df = pd.read_csv('synthetic_data_large_with_cv.csv')

    # Add ID column as the first column (keeping the original row index)
    df['ID'] = df.index + 1  # Adding 1 to start ID from 1 instead of 0

    # Copy the entire dataset for processing
    df_sampled = df.copy()

    # Add columns for the scores, winner, and the CV IDs for comparison
    df_sampled['cv_1_id'] = df_sampled['ID']
    df_sampled['cv_2_id'] = ''  # This will hold the ID of the randomly selected CV
    df_sampled['score~gemini-1.5-flash'] = 0
    df_sampled['winner~gemini-1.5-flash'] = ''

# Function to extract a score from the AI response
def extract_score(response_text):
    match = re.search(r"\b([1-9][0-9]?|100)\b", response_text)
    if match:
        return int(match.group(1))  # Return the matched score
    return 0  # If no score is found, return 0

# Function to ask Gemini for a CV rating
def rate_cv(cv_data):
    response = genai.GenerativeModel('gemini-1.5-flash').generate_content(
        f"Rate this CV on a scale of 1 to 100, where 1 is the lowest chance and 100 is the highest chance. Provide just number, don't provide any text.\n\n{cv_data}"
    )
    response_text = response.text.strip()
    score = extract_score(response_text)
    return score

# Function to compare two CVs and get Gemini's decision for choosing the winner
def compare_cvs(cv_data_1, cv_data_2):
    response = genai.GenerativeModel('gemini-1.5-flash').generate_content(
        f"Compare these two CVs and choose which one has a better chance of being invited for an interview.\n\nCV 1:\n{cv_data_1}\n\nCV 2:\n{cv_data_2}\n\nReturn 1 for CV 1 and 2 for CV 2. Provide just number, don't provide a text."
    )
    result = response.text.strip().split("\n")
    winner = result[0].strip()
    return winner

# Function to process each CV and compare with a random CV
def process_with_save(df_sampled, start_index):
    try:
        row = df_sampled.iloc[start_index]
        cv_data = row['Generated_Cover_Letter']
        cv_1_id = row['cv_1_id']

        # Rate the current CV
        score = rate_cv(cv_data)
        df_sampled.loc[start_index, 'score~gemini-1.5-flash'] = score

        # Randomly select another CV for comparison
        random_index = random.randint(0, len(df_sampled) - 1)
        while random_index == start_index:
            random_index = random.randint(0, len(df_sampled) - 1)

        next_cv_data = df_sampled.iloc[random_index]['Generated_Cover_Letter']
        next_cv_id = df_sampled.iloc[random_index]['ID']

        # Update the cv_2_id column with the randomly selected CV's ID
        df_sampled.loc[start_index, 'cv_2_id'] = next_cv_id

        # Compare the current CV with the randomly selected CV
        winner = compare_cvs(cv_data, next_cv_data)
        df_sampled.loc[start_index, 'winner~gemini-1.5-flash'] = winner

        # Save progress after processing each comparison
        df_sampled.to_csv(progress_file, index=False)
        print(f"Progress saved after row {start_index + 1}")

    except Exception as e:
        print(f"Error occurred: {e}. Saving progress and stopping.")
        df_sampled.to_csv(progress_file, index=False)
        raise

# Find the first row where cv_2_id is either empty string or NaN
start_row = df_sampled[df_sampled['cv_2_id'].isna() | (df_sampled['cv_2_id'] == '')].index.min()
if pd.isna(start_row):
    print("No empty cv_2_id found, starting from the beginning.")
    start_row = 0
else:
    print(f"Resuming from row {start_row}, where cv_2_id is empty.")

# Start processing and save after each comparison
total_rows = len(df_sampled)

for start_index in range(start_row, total_rows):
    process_with_save(df_sampled, start_index)

    # Add a delay every 5 CVs to avoid overwhelming the API
    if (start_index + 1) % 5 == 0:
        print(f"Processed 5 CVs. Pausing for 60 seconds to avoid API rate limits...")
        time.sleep(60)

# Handle the case where the last row does not have a comparison
df_sampled.loc[len(df_sampled) - 1, 'cv_2_id'] = 'N/A'
df_sampled.loc[len(df_sampled) - 1, 'winner~gemini-1.5-flash'] = 'N/A'

# Remove the 'ID' column since it's redundant with 'cv_1_id'
df_sampled.drop(columns=['ID'], inplace=True)

# Reorder columns to have cv_1_id and cv_2_id at the start
df_sampled = df_sampled[['cv_1_id', 'cv_2_id'] + [col for col in df_sampled.columns if col not in ['cv_1_id', 'cv_2_id']]]

# Save the final cleaned and modified DataFrame to a new CSV
output_file = 'synthetic_data_large_final_random_gemini.csv'
df_sampled.to_csv(output_file, index=False)

print(f"Saved cleaned and modified data to {output_file}")
