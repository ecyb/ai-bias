import google.generativeai as genai
import pandas as pd
import re
import time
import os

# Configure your Gemini API key
genai.configure(api_key="xx")

# File to save progress after each batch is processed
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

    # Select first 10 rows for testing, ensuring to make a copy to avoid warnings
    df_sampled = df.copy()  # Limit to first 10 rows for the example

    # Add columns for the scores, winner, and the CV IDs for comparison
    df_sampled['cv_1_id'] = df_sampled['ID']
    df_sampled['cv_2_id'] = ''  # This will hold the ID of the next CV for comparison
    df_sampled['score~gemini-1.5-flash'] = 0
    df_sampled['winner~gemini-1.5-flash'] = ''

# Function to extract a score from the AI response
def extract_score(response_text):
    match = re.search(r"\b([1-9][0-9]?|100)\b", response_text)
    if match:
        return int(match.group(1))  # Return the matched score
    return 0  # If no score is found, return 0

# Function to ask Gemini for a CV rating (just the cover letter)
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

# Add a delay to avoid exceeding API limits
def process_with_delay(df_sampled, start_index, batch_size=8):
    try:
        for index in range(start_index, min(start_index + batch_size, len(df_sampled))):
            row = df_sampled.iloc[index]
            cv_data = row['Generated_Cover_Letter']
            cv_1_id = row['cv_1_id']

            # Rate the current CV
            score = rate_cv(cv_data)
            df_sampled.loc[index, 'score~gemini-1.5-flash'] = score

            # Compare with the next CV if it exists
            if index < len(df_sampled) - 1:
                next_cv_data = df_sampled.iloc[index + 1]['Generated_Cover_Letter']
                next_cv_id = df_sampled.iloc[index + 1]['ID']

                # Update the cv_2_id column with the next CV's ID
                df_sampled.loc[index, 'cv_2_id'] = next_cv_id

                winner = compare_cvs(cv_data, next_cv_data)
                df_sampled.loc[index, 'winner~gemini-1.5-flash'] = winner

            # Save progress after each batch is processed
            df_sampled.to_csv(progress_file, index=False)
            print(f"Progress saved after row {index + 1}")
        
        # Delay for 60 seconds after processing the batch
        print(f"Batch of {batch_size} rows processed. Waiting for 60 seconds to avoid rate limits...")
        time.sleep(60)

    except Exception as e:
        print(f"Error occurred: {e}. Saving progress and stopping.")
        df_sampled.to_csv(progress_file, index=False)
        raise

# Process the DataFrame starting from row 137 in batches of 8 rows
start_row = 1000
batch_size = 8
total_rows = len(df_sampled)

for start_index in range(start_row, total_rows, batch_size):
    process_with_delay(df_sampled, start_index, batch_size)

# Handle the case where the last row does not have a comparison
df_sampled.loc[len(df_sampled) - 1, 'cv_2_id'] = 'N/A'
df_sampled.loc[len(df_sampled) - 1, 'winner~gemini-1.5-flash'] = 'N/A'

# Remove the 'ID' column since it's redundant with 'cv_1_id'
df_sampled.drop(columns=['ID'], inplace=True)

# Reorder columns to have cv_1_id and cv_2_id at the start
df_sampled = df_sampled[['cv_1_id', 'cv_2_id'] + [col for col in df_sampled.columns if col not in ['cv_1_id', 'cv_2_id']]]

# Save the final cleaned and modified DataFrame to a new CSV
output_file = 'synthetic_data_large_final_gemini.csv'
df_sampled.to_csv(output_file, index=False)

print(f"Saved cleaned and modified data to {output_file}")
