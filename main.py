import pandas as pd
import random
import pywhatkit as kit
import yaml

# Load students from students.yaml file
with open('students.yaml') as f:
    students = yaml.safe_load(f)

# Display list of students and ask user to choose one
print("Which student do you want to generate the questions for?")
for i, student in enumerate(students.keys(), 1):
    print(f"{i}. {student}")

selected_student_index = int(input()) - 1
selected_student = list(students.keys())[selected_student_index]
selected_phone = students[selected_student]

# Read the question bank Excel file
df = pd.read_excel('questionbank.xlsx')

# Ensure the "Attempted By" column is treated as a string type
df['Attempted By'] = df['Attempted By'].astype(str)

# Function to pick two random questions not yet attempted by the selected student
def pick_random_questions(df, student_name):
    unattempted_questions = df[~df['Attempted By'].apply(lambda x: student_name in str(x))]
    if len(unattempted_questions) < 2:
        raise ValueError(f"Not enough unattempted questions for {student_name}.")
    selected_questions = unattempted_questions.sample(2)
    return selected_questions

# Pick two random questions for the selected student
try:
    selected_questions = pick_random_questions(df, selected_student)
    for idx, row in selected_questions.iterrows():
        # Safely evaluate or handle the "Attempted By" field
        attempted_by_str = row['Attempted By']
        attempted_by = []
        if attempted_by_str != 'nan':  # Check for 'nan' string
            try:
                attempted_by = eval(attempted_by_str)
            except (SyntaxError, NameError):
                pass  # If eval fails, treat it as an empty list
        
        attempted_by.append(selected_student)
        df.at[idx, 'Attempted By'] = str(attempted_by)
    
    # Save the updated Excel file
    df.to_excel('questionbank.xlsx', index=False)
    
    # Prepare the message with the selected questions
    message_body = f"Hi {selected_student}, here are your questions:\n\n"
    for i, row in selected_questions.iterrows():
        message_body += f"Q{row['Question Number']}: {row['Question']}\n"
    
    # Send the message via WhatsApp using pywhatkit
    kit.sendwhatmsg_instantly(selected_phone, message_body)
    
    print(f"Questions sent to {selected_student} via WhatsApp.")
except ValueError as e:
    print(e)
