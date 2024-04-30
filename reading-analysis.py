import sqlite3

def create_translated_database(original_data, translated_texts):
    conn = sqlite3.connect('./translated_toefltporead.db')
    cursor = conn.cursor()

    # Assuming the table and column names are the same and the table exists
    # You might need to create a table if it doesn't exist.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tpo_reading_question_analysis (
            id INTEGER PRIMARY KEY,
            reading_ques_analysis_analysisContent TEXT
        )
    ''')

    for (id, _), translated in zip(original_data, translated_texts):
        cursor.execute('''
            INSERT INTO tpo_reading_question_analysis (id, reading_ques_analysis_analysisContent) 
            VALUES (?, ?)
        ''', (id, translated))

    conn.commit()
    cursor.close()
    conn.close()


# Connect to SQLite database
conn = sqlite3.connect('./toefltporead.db')
cursor = conn.cursor()

# Query to select data from the table
query = "SELECT id, reading_ques_analysis_analysisContent FROM tpo_reading_question_analysis"
cursor.execute(query)

# Fetch all the data
data = cursor.fetchall()

# Close the connection
cursor.close()
conn.close()


translator = Translator()
translated_texts = []

for _, text in data:
    # Assuming the text is a mix of English and Chinese
    translated = translator.translate(text, src='zh-CN', dest='en').text
    translated_texts.append(translated)
    time.sleep(0.2)


create_translated_database(data, translated_texts)
