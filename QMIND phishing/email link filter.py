import imaplib
import email
import yaml
import re
import tkinter as tk
from tkinter import ttk
import webbrowser

#model depandancies
import os
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
import pandas as pd
from official.nlp import optimization

# Path to the directory containing the saved model files
model_path = "C:/Users/17jcs9/Downloads/my_sigmoid_bert_model-20240219T185035Z-001/my_sigmoid_bert_model"

# Load the model
loaded_model = tf.keras.models.load_model(model_path, compile=False)



def extract_links(text):
    # Define the regular expression pattern to find URLs
    url_pattern = r'https?://\S+|www\.\S+'

    # Find all matches of the pattern in the text
    links = re.findall(url_pattern, text)

    return links

with open("C:/Users/17jcs9/Desktop/credentials.yml") as f:
    content = f.read()

#get username and password
my_cred = yaml.load(content, yaml.FullLoader)
username, password = my_cred["user"], my_cred["password"]

#imap url
imap_url = "imap.gmail.com"

#Connection to gmail
my_mail = imaplib.IMAP4_SSL(imap_url)

#login
my_mail.login(username, password)

#select the inbox to fetch messages
my_mail.select("Inbox")

#get all messages and run algo over them
_, msgnums = my_mail.search(None, "ALL")

def on_link_click(event):
    item = tree.selection()[0]
    url = tree.item(item, "values")[-2]
    if(tree.item(item, "values")[-1] == "Yes"):
        webbrowser.open_new(url)
    else:
        popup_window(url)

def popup_window(url):
    popup = tk.Toplevel()
    popup.title("Popup Window")
    
    # Add widgets to the popup window
    label = ttk.Label(popup, text="This link may be dangerous, do you want to proceed anyways?")
    label.pack(padx=20, pady=20)
    
    no_button = ttk.Button(popup, text="No", command=popup.destroy)
    no_button.pack(padx=20, pady=10)

    close_button = ttk.Button(popup, text="Yes", command=lambda: close_popup(popup, url))
    close_button.pack(padx=20, pady=10)

def close_popup(popup, url):
    # Close the popup window
    popup.destroy()
    # Do something after the popup is closed
    webbrowser.open_new(url)

def clear_table():
    for item in tree.get_children():
        tree.delete(item)

def check_all():
    clear_table()
    #get all messages and run algo over them
    try:
        _, msgnums = my_mail.search(None, "ALL")
        # Pack the treeview widget
        tree.grid(row=3, columnspan=4, sticky="ew")
        data = process_emails(msgnums)
        
        for row in data:
            tree.insert("", "end", values=row)
    except:
        print("no emails found")

def check_sender():
    try:
        clear_table()
        _, msgnums = my_mail.search(None, "FROM", sender_text.get("1.0", "end").strip())
        print(msgnums)
        tree.grid(row=3, columnspan=4, sticky="ew")
        data = process_emails(msgnums)
        
        for row in data:
            tree.insert("", "end", values=row)
    except:
        print("user has not send any emails")

def check_subject():
    try:
        clear_table()
        _, msgnums = my_mail.search(None, "SUBJECT", subject_text.get("1.0", "end").strip())
        tree.grid(row=3, columnspan=4, sticky="ew")
        data = process_emails(msgnums)
        for row in data:
            tree.insert("", "end", values=row)
    except:
        print("No email with desired subject")

def process_emails(msgnums):
    
    count = 0
    is_safe = []
    for msgnum in msgnums[0].split():
        print(count)
        #cap on the number of links we process so people do not need to wait forever when running dem0
        #remove if desired
        if count < 25:
            #get data
            _, data = my_mail.fetch(msgnum, "(RFC822)")
            #extract the message component of the email
            message = email.message_from_bytes(data[0][1])

            message_str = ""
            #extract message
            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    message_str += (part.as_string())
            

            #extract links from email
            links = extract_links(message_str)
            
            for link in links:
                count += 1
                #remove https from link
                if link.startswith("https://"):
                    # Remove "https://" from the link
                    link = link[len("https://"):]
                print(link)
                #pass link into model
                d = {'URL': [link]}
                df = pd.DataFrame(data=d)
                prediction = loaded_model.predict(df)[0][0]
                if prediction > 0.5:
                    safe = "no"
                else:
                    safe = "yes"
                
                is_safe.append([int(msgnum),str(message.get("Subject")),str(message.get("From")),link,safe])
                #save predicted output into array
                #print(links)
        
    print(is_safe)
    return is_safe

def clear_text():
    subject_text.delete(1.0, tk.END)
    sender_text.delete(1.0, tk.END)
    tree.grid_forget()


root = tk.Tk()
root.title("Email Filter")
root.geometry("1200x600")

slabel = tk.Label(root, text="Sender")
slabel.grid(row=0, column=0)
#publication text box text box
sender_text = tk.Text(root, height = 1, width = 140)
sender_text.grid(row=0, column=1, columnspan=3)

tlabel = tk.Label(root, text="Subject")
tlabel.grid(row=1, column=0)

#publication text box
subject_text = tk.Text(root, height = 1, width = 140)
subject_text.grid(row=1, column = 1, columnspan=3)

# Create a treeview widget (table)
tree = ttk.Treeview(root, columns=("Email Number", "Subject", "Sender", "Link", "Safe"), show="headings")

# Define column headings
tree.heading("Email Number", text="Email Number")
tree.heading("Subject", text="Subject")
tree.heading("Sender", text="Sender")
tree.heading("Link", text="Link")
tree.heading("Safe", text="Safe")

# Bind the link click event to the treeview widget
tree.bind("<Double-1>", on_link_click)  # Double-1 means double left click

#define buttons and the commands that run when clicked
run_button_1 = ttk.Button(root, text="Check all", command=check_all)
run_button_1.grid(row=2, column=0)

run_button_2 = ttk.Button(root, text="Check by Subject", command=check_subject)
run_button_2.grid(row=2, column=1)

run_button_3 = ttk.Button(root, text="Check by Sender", command=check_sender)
run_button_3.grid(row=2, column=2)

clear_button = ttk.Button(root, text="Reset", command=clear_text)
clear_button.grid(row=2, column=3)

root.mainloop()