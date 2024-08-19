# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
load_dotenv()
a = os.getenv('g1')
b = os.getenv('g2')
c = os.getenv('g3')
d = os.getenv('g4')
e = os.getenv('g5')
f = os.getenv('g6')

groq_keys = [a,b,c,d,e,f]


import numpy as np
def keys():
    number = np.random.randint(len(groq_keys))
    models = np.random.randint(0,2)
    return number,models


def groq(input,key):
    chat = ChatGroq(
        temperature=0,
        model="llama3-70b-8192",
        api_key=key
    )
    
    return chat.invoke(input)
def final(Input,api):
       

    print("calling from groq")
    print(keys()[0])
    # return groq(Input,groq_keys[keys()[0]])
    return groq(Input,api).content


