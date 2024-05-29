import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import sqlite3
import random
from dotenv import load_dotenv

load_dotenv()

email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')

def send_keys_human_speed(element, keys):
    for key in keys:
        element.send_keys(key)
        time.sleep(0.15)  # Adjust the sleep duration to control the typing speed

def main():
    driver = uc.Chrome()
    driver.maximize_window()
    driver.get('https://projet-voltaire.fr/')
    
    print("👋 Welcome to Voltaire Ez!")
    # Checks cookie
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "cmpboxbtn"))).click()
    
    # Clicks on the login button
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "authenticateOption"))).click()
    
    # Fills the email and password fields
    email_field = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "login-username")))
    password_field = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "login-pwd")))
    send_keys_human_speed(email_field, email)
    send_keys_human_speed(password_field, password)
    
    # Waits for the user to complete the captcha
    print("Please resolve the captcha and click the sign in button to continue...")
    
    # Clicks on the cookie button
    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".modal-footer > button"))).click()
    
    # Enters "orthographe" section
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#applicationOrthographe"))).click()
    
    print("")
    print("Entering the training...")
    # CSS selectors for the three categories
    categories = ['#productTab_1', '#productTab_2', '#productTab_3']
    for category in categories:
        try:
            # Try to enter the category
            WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, category))).click()

            # Try to start an exercise
            WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.singleRunnable'))).click()

            # If an exercise was started, wait for it to load and then break the loop
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".top-side-bar-training")))
            break
        except TimeoutException:
            # If there's no exercise available in this category, continue with the next category
            continue
    else:
        # If there's no exercise available in any category, exit the program
        print("❌ No more exercises available. Exiting the program...")
        driver.quit()
        exit()

    print("")
    response_auto = input("❓ Do you want to go automatically to the next exercises? (y/n) ")
    if response_auto.lower() == 'y':
        pass
    elif response_auto.lower() == 'n':
        pass
    else:
        print("")
        print("❌ Invalid input. Please enter 'y' or 'n'.")
                        
    # Connect to the database
    with sqlite3.connect('sentences.db') as conn:
        # Create a cursor object
        c = conn.cursor()
        # Create table named 'Sentences' if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS Sentences
            (sentence TEXT, no_mistake INTEGER, mistake_text TEXT)''')
    
        # Forloop connected to the database to go through the exercices
        while True:    
            print("")
            print("🤞 Starting new exercise...")
            # Check if a popup has appeared
            try:
                WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".popupPanel")))
                # print("")
                # print("Popup!")
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".understoodButton"))).click()
                time.sleep(0.1)
                # Click on random buttons
                intensive_questions = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.intensiveQuestion')))
                for question in intensive_questions:
                    # Randomly choose between .buttonOk and .buttonKo
                    button = random.choice(['.buttonOk', '.buttonKo'])
                    question.find_element(By.CSS_SELECTOR, button).click()
                    time.sleep(0.1)
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".exitButton"))).click()
            except TimeoutException:
                # print("")
                # print("No popup!")
                pass
    
            try:
                # Find all words within the sentence
                span_elements = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".sentence .pointAndClickSpan")))
                if span_elements:
                    # Initialize an empty string to store the sentence
                    sentence = ''
                    # Iterate over the span elements and concatenate their text
                    for span in span_elements:
                        # If the span is empty, add a space to the sentence
                        if span.text == '':
                            sentence += ' '
                        # Otherwise, add the span's text to the sentence
                        else:
                            sentence += span.text
                    # print("")
                    # print("Sentence is:")
                    # print(sentence)
        
                    # Execute a SELECT query to check if a row with the sentence already exists
                    c.execute("SELECT * FROM Sentences WHERE sentence = ?", (sentence,))
                    row = c.fetchone()
        
                    # If the row exists, clicks on the mistake
                    if row is not None:
                        print("🚀 Sentence already exists in the database!")
                        no_mistake = row[1]  # Assuming no_mistake is the second column in the table
                        # If there's no mistake
                        if no_mistake == 1:
                            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".noMistakeButton"))).click()
                            print("🏅 Gotcha!")
                        else:
                            mistake_text = row[2]  # Assuming mistake_text is the third column in the table
                            # print(mistake_text)
                            for span in span_elements:
                                if span.text == mistake_text:
                                    span.click()
                                    print("🏅 Gotcha!")
                                    break
        
                    # If the row doesn't exist, insert the sentence into the 'Sentences' table
                    else:
                        print("⛏️ New sentence found!")
                        # Clicks on the "No mistake" button
                        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".noMistakeButton"))).click()
        
                        # Waits for the answer to appear
                        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".answerStatusBar")))
        
                        # Checks if the answer is correct or not
                        try:
                            driver.find_element(By.CSS_SELECTOR, '.answerStatusBar.correct')
                            print("🏅 Gotcha!")
                            no_mistake = 1
                            mistake_text = None  # No mistake text when there are no mistakes
                        except:
                            print("✒️ There's a mistake! Saving it...")
                            no_mistake = 0
                            mistake_element = driver.find_element(By.CSS_SELECTOR, '.answerWord')
                            mistake_text = mistake_element.text
                            # Removes delimiters if they are at the beginning or end of the word
                            # If they're not, splits the word by the delimiter and takes the first part
                            def split_text(mistake_text, iterations=5):
                                for _ in range(iterations):
                                    for delimiter in [' ', '-', '‑', "'", ",", ".", ":", ";", "!", "?", "(", ")", "[", "]", "{", "}", "<", ">", "«", "»", "“", "”", "‘", "’", "„", "‟", "‹", "›", "‛", "‚", "‵", "‶", "‷", "‸"]:
                                        if mistake_text and mistake_text[0] == delimiter:
                                            mistake_text = mistake_text[1:]
                                        elif mistake_text and mistake_text[-1] == delimiter:
                                            mistake_text = mistake_text[:-1]
                                        else:
                                            parts = mistake_text.split(delimiter)
                                            if len(parts) > 1:
                                                mistake_text = parts[0]
                                return mistake_text

                            # Runs multiple times to handle long compound words
                            mistake_text = split_text(mistake_text)
                        # Inserts the sentence and the correctness of the answer into the 'Sentences' table
                        c.execute("INSERT INTO Sentences VALUES (?, ?, ?)", (sentence, no_mistake, mistake_text))
                        conn.commit()
                    # Goes to the next question
                    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".nextButton"))).click()
            except TimeoutException:
                # Checks whether we're at the end screen or not
                try:
                    # Check if the element .trainingEndViewDiv is present
                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.trainingEndViewDiv')))
                    print("")
                    print("🎉 Level completed!")
                    # If the user chose to go manually to the next exercises
                    if response_auto.lower() == 'n':
                        response = input("Do you want to continue? (y/n) ")
                        if response.lower() == 'y':
                            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".trainingEndViewGoHome"))).click()
                            try:
                                # If there's an exercise available, click it
                                WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.singleRunnable'))).click()
                            except TimeoutException:
                                try:
                                    # If there's no exercise available, tries to go on Orthotypographie
                                    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#productTab_2'))).click()
                                    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.singleRunnable'))).click()
                                except TimeoutException:
                                    try:
                                        # If there's no exercise available, tries to go on Excellence
                                        WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#productTab_3'))).click()
                                        WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.singleRunnable'))).click()
                                    except TimeoutException:
                                        # If there's no exercise available, exits the program
                                        print("❌ No more exercises available. Exiting the program...")
                                        break
                        # Exiting the while loop
                        elif response.lower() == 'n':
                            break
                        else:
                            print("")
                            print("❌ Invalid input. Please enter 'y' or 'n'.")
                    # If the user chose to go automatically to the next exercises
                    else:
                        print("🚀 Going to the next exercise...")
                        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".trainingEndViewGoHome"))).click()
                        try:
                            # If there's an exercise available, click it
                            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.singleRunnable'))).click()
                        except TimeoutException:
                            try:
                                # If there's no exercise available, tries to go on Orthotypographie
                                WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#productTab_2'))).click()
                                WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.singleRunnable'))).click()
                            except TimeoutException:
                                try:
                                    # If there's no exercise available, tries to go on Excellence
                                    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#productTab_3'))).click()
                                    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.singleRunnable'))).click()
                                except TimeoutException:
                                    # If there's no exercise available, exits the program
                                    print("❌ No more exercises available. Exiting the program...")
                                    break
                # If we're not at the end screen, do nothing and continue the loop
                except TimeoutException:
                    pass
            
    # If we get out of the while loop, end the program
    print("")
    print("❤️ Thanks for using Voltaire Ez!")
    driver.quit()
    exit()

if __name__ == "__main__":
    main()