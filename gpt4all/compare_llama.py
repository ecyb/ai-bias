import pandas as pd
import re  # Regular expression module to clean and extract text
import os
from gpt4all import GPT4All

# Load the Meta-Llama model (adjust the model file name if necessary)
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")

# Load the CSV file
csv_file = '../synthetic_data_large_with_cv.csv'
print("Loading CSV file...")
df = pd.read_csv(csv_file)

# Add ID column as the first column (keeping the original row index)
df['ID'] = df.index + 1  # Adding 1 to start ID from 1 instead of 0

# Select first 5 rows for testing (or process the full DataFrame if needed)
df_sampled = df.copy()

# Add columns for scores, winner, and comparison IDs
df_sampled['cv_1_id'] = df_sampled['ID']
df_sampled['cv_2_id'] = ''  # This will hold the ID of the next CV for comparison
df_sampled['score~Meta-Llama'] = 0
df_sampled['winner~Meta-Llama'] = ''

# Function to extract numbers from the response (for score and winner)
def extract_number(label, text):
    match = re.search(fr"{label}:\s*(\d+)", text)
    if match:
        return int(match.group(1))
    return None

# Function to compare two CVs and get the score and winner as a number
def compare_cvs(cv_data_1, cv_data_2):
    with model.chat_session():
        print(f"Sending CV data to Meta-Llama for comparison:\nCV 1: {cv_data_1[:500]}...\nCV 2: {cv_data_2[:500]}...")
        response = model.generate(f"""
        Compare the following two CVs:
        
        CV 1: {cv_data_1}
        CV 2: {cv_data_2}

        For each CV, provide a score between 1 and 100, where 1 is the lowest and 100 is the highest chance of being invited for an interview.

        Then, provide a winner: Return '1' if CV 1 is better, or '2' if CV 2 is better. Respond in this format:
        
        CV 1 Score: [numeric score]
        CV 2 Score: [numeric score]
        Winner: [1 or 2]
        """)
        print(f"Model response:\n{response}")  # Debug print the full response from the model

        # Extracting scores and winner
        cv1_score = extract_number("CV 1 Score", response)
        cv2_score = extract_number("CV 2 Score", response)
        winner = extract_number("Winner", response)
        
        return cv1_score, cv2_score, winner

# Save the CSV incrementally as new data is processed
output_file = 'synthetic_data_large_final_llama.csv'

# Write the headers once before starting the loop
df_sampled.head(0).to_csv(output_file, index=False)

# Process the CVs
for index in range(len(df_sampled) - 1):
    cv_data_1 = df_sampled.iloc[index]['Generated_Cover_Letter']
    cv_data_2 = df_sampled.iloc[index + 1]['Generated_Cover_Letter']

    # Perform comparison
    cv1_score, cv2_score, winner = compare_cvs(cv_data_1, cv_data_2)
    
    # Update the DataFrame with the results
    if cv1_score is not None and cv2_score is not None and winner is not None:
        df_sampled.loc[index, 'score~Meta-Llama'] = cv1_score
        df_sampled.loc[index + 1, 'score~Meta-Llama'] = cv2_score
        df_sampled.loc[index, 'cv_2_id'] = df_sampled.iloc[index + 1]['ID']
        df_sampled.loc[index, 'winner~Meta-Llama'] = winner

        # Write the current row to the CSV
        df_sampled.iloc[[index]].to_csv(output_file, mode='a', index=False, header=False)
        df_sampled.iloc[[index + 1]].to_csv(output_file, mode='a', index=False, header=False)

# Handle the case where the last row does not have a comparison
df_sampled.loc[len(df_sampled) - 1, 'cv_2_id'] = 'N/A'
df_sampled.loc[len(df_sampled) - 1, 'winner~Meta-Llama'] = 'N/A'

# Write the final row
df_sampled.iloc[[-1]].to_csv(output_file, mode='a', index=False, header=False)

# Remove the 'ID' column since it's redundant with 'cv_1_id'
df_sampled.drop(columns=['ID'], inplace=True)

# Reorder columns to have cv_1_id and cv_2_id at the start
df_sampled = df_sampled[['cv_1_id', 'cv_2_id'] + [col for col in df_sampled.columns if col not in ['cv_1_id', 'cv_2_id']]]

print(f"Saved cleaned and modified data incrementally to {output_file}")
