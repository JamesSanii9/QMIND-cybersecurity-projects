import tkinter as tk
import nltk
from textblob import TextBlob
from newspaper import Article

#import os
#import shutil
import pandas as pd
#import tensorflow as tf
#import tensorflow_hub as hub
#import tensorflow_text as text
#from official.nlp import optimization
#import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import confusion_matrix
import numpy as np
#import itertools
from joblib import load
import nltk
nltk.download('punkt')

from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("hamzab/roberta-fake-news-classification")

model = AutoModelForSequenceClassification.from_pretrained("hamzab/roberta-fake-news-classification")

print("got here")

import torch
def predict_fake(title,text):
    input_str = "<title>" + title + "<content>" +  text + "<end>"
    input_ids = tokenizer.encode_plus(input_str, max_length=512, padding="max_length", truncation=True, return_tensors="pt")
    device =  'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)
    with torch.no_grad():
        output = model(input_ids["input_ids"].to(device), attention_mask=input_ids["attention_mask"].to(device))
    return dict(zip(["Fake","Real"], [x.item() for x in list(torch.nn.Softmax()(output.logits)[0])] ))
    


#with open('C:/Users/17jcs9/Downloads/model.pkl', 'rb') as f:
    #loaded_model = pickle.load(f)

# Remove punctuation

import string

def punctuation_removal(text):
    all_list = [char for char in text if char not in string.punctuation]
    clean_str = ''.join(all_list)
    return clean_str

# Removing stopwords
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
stop = stopwords.words('english')

#nltk.download("punkt")
def summarize():
    #get article 
    url = utext.get("1.0", "end").strip()
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()

    #config GUI to update
    title.config(state = "normal")
    author.config(state = "normal")
    publication.config(state = "normal")
    summary.config(state = "normal")
    sentiment.config(state = "normal")
    fake.config(state = "normal")
    
    #update title
    title.delete("1.0", "end")
    title.insert("1.0",article.title)

    #update authors
    author.delete("1.0", "end")
    author.insert("1.0",article.authors)

    #update publication date
    publication.delete("1.0", "end")
    publication.insert("1.0",article.publish_date)

    #update summary
    summary.delete("1.0", "end")
    summary.insert("1.0",article.summary)

    #predict and update fake or real label
    #if article.title:
       # input = str(article.title + " " + article.text)
    #else:
    input = str(article.text)
    

    print(input)
    data = pd.DataFrame(data={'text': [input]})

    fake.delete("1.0", "end")
    #add model pred here
    pred = (predict_fake(article.title, article.text))
    print(pred)
    if pred["Fake"] < pred["Real"]:
        fake.insert("1.0", f"Real")
    else:
        fake.insert("1.0", f"Fake")

    #sentiment analysis on full text
    analysis = TextBlob(article.text)
    polarity = ""
    #build polarity string to show users
    if abs(analysis.polarity) > 0.5:
        polarity += "Very"
    if (analysis.polarity) > 0:
        polarity += "Positive"
    else:
        polarity += "Negative"
    if analysis.polarity > -0.1 and analysis.polarity < 0.1:
        polarity = "Neutral"
    
    #put subjectivity on a scale from 1-10, high is better
    subjectivity = round(abs(10-analysis.subjectivity*10), 1)

    sentiment.delete("1.0", "end")
    sentiment.insert("1.0", f"Polarity: {polarity}, Subjectivity: {subjectivity}")

    #set to original state
    title.config(state = "disabled")
    author.config(state = "disabled")
    publication.config(state = "disabled")
    summary.config(state = "disabled")
    sentiment.config(state = "disabled")
    fake.config(state = "disabled")


root = tk.Tk()
root.title("News Summary")
root.geometry("1200x800")

tlabel = tk.Label(root, text="Title")
tlabel.pack()

#title text box
title = tk.Text(root, height = 1, width = 140)
title.config(state="disabled", bg="#dddddd")
title.pack()

alabel = tk.Label(root, text="Author")
alabel.pack()

#author text box
author = tk.Text(root, height = 1, width = 140)
author.config(state="disabled", bg="#dddddd")
author.pack()

plabel = tk.Label(root, text="Publication Date")
plabel.pack()

#publication text box text box
publication = tk.Text(root, height = 1, width = 140)
publication.config(state="disabled", bg="#dddddd")
publication.pack()

slabel = tk.Label(root, text="Summary")
slabel.pack()

#publication text box text box
summary = tk.Text(root, height = 25, width = 140)
summary.config(state="disabled", bg="#dddddd")
summary.pack()

selabel = tk.Label(root, text="Sentiment Analysis")
selabel.pack()

#publication text box text box
sentiment = tk.Text(root, height = 1, width = 140)
sentiment.config(state="disabled", bg="#dddddd")
sentiment.pack()

fake_label = tk.Label(root, text="Fake news prediction")
fake_label.pack()

#publication text box text box
fake = tk.Text(root, height = 1, width = 140)
fake.config(state="disabled", bg="#dddddd")
fake.pack()

ulabel = tk.Label(root, text="URL")
ulabel.pack()

#publication text box text box
utext = tk.Text(root, height = 1, width = 140)
utext.pack()

run_button = tk.Button(root, text="Summarize", command=summarize)
run_button.pack()


root.mainloop()