import json
import tkinter as tk
from tkinter import messagebox
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring
import requests

from src.base_application.utils import check_email
from src.base_application import api_server_ip


def member_registration():
    # create the main window
    window = tk.Tk()
    window.geometry("1200x900")
    window.title("Member Registration")

    window.resizable(False, False)

    def register_button_click(email, name):
        if check_email(email):
            if len(name) <= 0:
                messagebox.showinfo("Error", "Please enter a name")
                # POP up
                email_entry.delete(first=0, last=255) # will delete what is from position 0 to 255
                name_entry.delete(first=0, last=255)
            else:
                # Make an XML payload with input data
                root = Element('member')
                name_xml = SubElement(root, 'name')
                name_xml.text = str(name)
                email_xml = SubElement(root, 'email')
                email_xml.text = str(email)
                # xml_payload = tostring(root, encoding='unicode', method='xml')
                xml_string = tostring(root, encoding="utf-8")
                xml_pretty_string = minidom.parseString(xml_string).toprettyxml(indent="  ")

                # Insert to DB by sending the payload to an API
                url = api_server_ip + '/api/members'
                files = {'file': ('data.xml', xml_pretty_string)}
                response = requests.post(url, files=files)
                # headers = {'Content-Type': 'application/xml'}
                # response = requests.post(url, json=xml_payload, headers=headers)
                # CLean the fields
                email_entry.delete(first=0, last=255) # will delete what is from position 0 to 255
                name_entry.delete(first=0, last=255)
        else:
            # Make a pop-up
            messagebox.showinfo("Error", "Please enter a valid email")
            email_entry.delete(first=0, last=30)
            name_entry.delete(first=0, last=30)

    def back_button_click():
        window.destroy()
        from src.base_application.member.manageMembers import manage_members
        manage_members()

    # create two frames side by side
    frame1 = tk.Frame(window, width=600, height=900, bg="#D9D9D9")
    frame2 = tk.Frame(window, width=600, height=900, bg="#F0AFAF")

    frame1.pack(side="left")
    frame2.pack(side="right")

    # add a label to frame1 with the specified properties
    label = tk.Label(frame1, text="Admin Panel", font=("Inter", 24, "normal"), bg="#D9D9D9", fg="black", justify="left")
    label.place(x=20, y=20, width=190, height=50)

    # set the line height to 29 pixels and vertical alignment to top
    label.config(anchor="nw", pady=0, padx=0, wraplength=0, height=0, width=0)

    # add a label and text area to frame1 for Email
    email_label = tk.Label(frame1, text="Email", font=("Inter", 18, "normal"), bg="#D9D9D9", fg="black",
                           justify="left")
    email_label.place(x=20, y=300, width=123, height=24)
    email_entry = tk.Entry(frame1, font=("Inter", 18, "normal"), bg="white", fg="black", justify="left")
    email_entry.place(x=153, y=300, width=300, height=28)

    # add a label and text area to frame1 for Name
    name_label = tk.Label(frame1, text="Name", font=("Inter", 18, "normal"), bg="#D9D9D9", fg="black",
                          justify="left")
    name_label.place(x=20, y=350, width=123, height=24)
    name_entry = tk.Entry(frame1, font=("Inter", 18, "normal"), bg="white", fg="black", justify="left")
    name_entry.place(x=153, y=350, width=300, height=28)

    # add a login button to frame1
    register_button = tk.Button(frame1, text="Register", font=("Inter", 12), bg="white", fg="black",
                                bd=0, highlightthickness=0, activebackground="#B3B3B3",
                                command=lambda: register_button_click(email_entry.get(), name_entry.get()))
    register_button.place(x=200, y=450, width=82, height=24)

    # add a back button to frame1
    back_button = tk.Button(frame1, text="Back", font=("Inter", 12), bg="white", fg="black",
                            bd=0, highlightthickness=0, activebackground="#B3B3B3",
                            command=back_button_click)
    back_button.place(x=20, y=700, width=82, height=24)

    # run the main loop
    window.mainloop()