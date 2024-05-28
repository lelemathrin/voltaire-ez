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
    # Enters the training section
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.singleRunnable'))).click()
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".top-side-bar-training")))
    
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
    
            # Find all words within the sentence
            span_elements = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".sentence .pointAndClickSpan")))
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
                        correct_element = driver.find_element(By.CSS_SELECTOR, '.answerStatusBar.correct')
                        print("🏅 Gotcha!")
                        no_mistake = 1
                        mistake_text = None  # No mistake text when there are no mistakes
                    except:
                        print("✒️ There's a mistake! Saving it...")
                        no_mistake = 0
                        mistake_element = driver.find_element(By.CSS_SELECTOR, '.answerWord')
                        mistake_text = mistake_element.text
                        # Remove unwanted characters from mistake_text
                        mistake_text = mistake_text.replace("'", "").replace(".", "").replace(",", "")
                        mistake_text = mistake_text.split(' ')[0].split('-')[0].split('‑')[0]
                    # Inserts the sentence and the correctness of the answer into the 'Sentences' table
                    c.execute("INSERT INTO Sentences VALUES (?, ?, ?)", (sentence, no_mistake, mistake_text))
                    conn.commit()
                # Goes to the next question
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".nextButton"))).click()
            else:
                # Checks whether we're at the end screen or not
                try:
                    # Check if the element .trainingEndViewDiv is present
                    WebDriverWait(driver, 0.2).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.trainingEndViewDiv')))
                    print("")
                    print("🎉 Level completed!")
                    response = input("Do you want to continue? (y/n) ")
                    if response.lower() == 'y':
                        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".trainingEndViewGoHome"))).click()
                        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.singleRunnable'))).click()
                    # Exiting the while loop
                    elif response.lower() == 'n':
                        break
                    else:
                        print("")
                        print("❌ Invalid input. Please enter 'y' or 'n'.")
                except TimeoutException:
                    # If the element is not present, do nothing and continue the loop
                    pass
    
            
    # If we get out of the while loop, end the program
    print("")
    print("❤️ Thanks for using Voltaire Ez!")
    driver.quit()

if __name__ == "__main__":
    main()