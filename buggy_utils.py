"""
Buggy module for testing sentinel-ai review
This file has intentional issues the bot should catch
"""

import os
import subprocess

# Issue 1: Hardcoded secret
API_KEY = "sk-1234567890abcdef"
DB_PASSWORD = "admin123"

# Issue 2: SQL Injection vulnerability
def get_user(username):
    query = f"SELECT * FROM users WHERE name = '{username}'"
    return db.execute(query)

# Issue 3: Command injection
def run_command(user_input):
    os.system("echo " + user_input)

# Issue 4: Using eval on user input
def calculate(expression):
    return eval(expression)

# Issue 5: No error handling, bare except
def divide(a, b):
    try:
        return a / b
    except:
        pass

# Issue 6: Debug mode left on
DEBUG = True
SECRET_KEY = "change-me-in-production"

# Issue 7: subprocess with shell=True
def backup_db(name):
    subprocess.call(f"pg_dump {name} > backup.sql", shell=True)

# Issue 8: No input validation
def process_data(data):
    result = data["key"]["nested"]["deep"]
    return result
