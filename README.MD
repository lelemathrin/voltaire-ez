# Projet Voltaire Ez

Pour les flemmards qui préfèrent laisser tourner leur PC plutôt que d'apprendre le français.
Automatise le passage des niveaux de la partie "Orthographe" de Projet-Voltaire.

## Prerequisites

- Python 3.6 or higher
- Google Chrome browser

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/lelemathrin/voltaire-ez.git

2. Navigate to the project directory:
    ```bash
    cd voltaire-ez

3. Install the required Python packages:
    ```bash
    pip install -r requirements.txt

## Configuration

1. Rename .env.example to .env

2. Open the .env file and replace your-email@projet-voltaire.fr and your-password with your email and password.

## Running the Script

To run the script, use the following command:
    ```bash
    python voltaire-pwner.py

After running the script, it will start entering your credentials and you will be asked to resolve a captcha and click the sign in button, be sure to focus the window during this process.
Once you've done that, the script will take over and start gathering the correct answers.