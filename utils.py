from bs4 import BeautifulSoup
import requests
from openai import OpenAI
import os
import streamlit as st



def scrape_job(url):
    try:
        res = requests.get(url)
        res.raise_for_status()  # Raises HTTPError for bad responses (4xx and 5xx)
        
        soup = BeautifulSoup(res.text, 'html.parser')
        job_description = soup.find('div', class_='description__text')
        
        if job_description:
            return 'Job Description: \n' + job_description.get_text(strip=True, separator='\n')
        else:
            return "No job description found on the webpage."
    except Exception as e:
        print(e)
        return f"Failed to retrieve the webpage: {e}"    


def check_key(openai_api_key) -> bool:

    if not openai_api_key:
        return False
    try:
        client = OpenAI(api_key = openai_api_key)
        chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="gpt-3.5-turbo",)    
    
    except Exception as e:
        st.error(f"{e.__class__.__name__}: {e}")
        return False

    return True