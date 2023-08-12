import streamlit as st
import cv2
import torch
from utils.hubconf import custom
import numpy as np
import tempfile
import time
from collections import Counter
import json
import pandas as pd
from model_utils import get_yolo, color_picker_fn, get_system_stat
from ultralytics import YOLO

import streamlit_authenticator as stauth
import postgreData as db
import spreadsheetData as sprd

import streamlit.components.v1 as components

from streamlit_option_menu import option_menu

import twilioSMS as twil

import logTime

msgs = {'Pistol': 'Stay calm, comply with their demands, and avoid sudden movements that may escalate the situation.', 'Knife': 'Keep a safe distance, try to create barriers or find objects to defend yourself, and aim for vulnerable areas if self-defense is necessary.', 'Blunt weapon': 'Keep your distance, evade or block their strikes, and look for opportunities to escape or seek help.', 'Fire': 'Alert others, evacuate calmly following the established emergency exits, and avoid elevators while prioritizing your safety.', 'Smoke': ' Stay low to avoid inhaling smoke, cover your mouth with a cloth, and follow evacuation procedures while feeling surfaces for heat before touching them.', 
'Rifle': 'Take cover immediately, find a secure location out of the attacker\'s line of sight, and contact authorities while providing them with accurate information about the situation.'}


#------------------Authentication----------------------#
users = db.fetch_all_users()

usernames = [user["username"] for user in users]
names = [user["name"] for user in users]
hashed_passwords = [user["password"] for user in users]

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    "cctv_system", "abcdef", cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
#----------------------------MAIN PROGRAM-------------------------#   
    p_time = 0

    authenticator.logout("Logout", "sidebar")
    
    
    selected = option_menu(
        menu_title = "Main Menu",
        options = ["Home", "Log data"],
        default_index = 0,
        orientation = "horizontal",
    )
    if selected == "Home":
        
        st.sidebar.title('Settings')
        # Choose the model
        model_type = 'YOLOv8'

        st.title('Surveillance System')

        sample_img = cv2.imread('cam1.png')
        sample_img2 = cv2.imread('cam2.png')
        # sample_img3 = cv2.imread('cam3.png')
        # sample_img4 = cv2.imread('cam4.png')

        # placeholder = st.empty()

        FRAME_WINDOW = st.image(sample_img, channels='BGR')
        FRAME_WINDOW2 = st.image(sample_img2, channels='BGR')
        # FRAME_WINDOW3 = st.image(sample_img2, channels='BGR')
        # FRAME_WINDOW4 = st.image(sample_img2, channels='BGR')


        # # Create a list of images
        # images = [sample_img, sample_img2, sample_img3, sample_img4]

        # # Create a grid to display the images
        # col1, col2 = st.columns(2)

        # with col1:
        #     st.image(images[0], use_column_width=True, channels='BGR')

        # with col2:
        #     st.image(images[2], use_column_width=True, channels='BGR')      
        #     st.image(images[3], use_column_width=True, channels='BGR')
            

        cap = None
        cap2 = None


        path_model_file = 'yolov8.pt'

        model = YOLO(path_model_file)

        # Load Class names
        class_labels = model.names

        # Inference Mode
        options = 'Webcam'

        # Confidence
        confidence = st.sidebar.slider(
            'Detection Confidence', min_value=0.0, max_value=1.0, value=0.25)

        # Draw thickness
        draw_thick = 3

        color_pick_list = []
        for i in range(len(class_labels)):
            classname = class_labels[i]
            color = color_picker_fn(classname, i)
            color_pick_list.append(color)

        #Alert button
        st.sidebar.title('Alert')
        with st.sidebar:
            manualMode = st.checkbox('Manual mode')
            if manualMode:
                st.warning('Caution: Only use in case of Emergency', icon="⚠️")
                options2 = st.multiselect('What is the danger?',['Pistol', 'Knife', 'Fire', 'Smoke', 'Blunt weapon', 'Rifle'])
                options = ','.join(options2)
                alertButton = st.button("Alert")
                if alertButton:
                    for m in options2:
                        twil.sendSMS(f"Detected {m} in the area. {msgs[m]}")
                  
        # Web-cam
        # if options == 'Webcam':
        #     cam_options = st.sidebar.selectbox('Webcam Channel',
        #                                     ('Select Channel', '0', '1', '2', '3'))

            # if not cam_options == 'Select Channel':
        pred = st.checkbox('Run ')

        #OpenCV function to capture video
        cap = cv2.VideoCapture(int(0))

        cap2 = cv2.VideoCapture(int(1))



        # RTSP
        if options == 'RTSP':
            rtsp_url = st.sidebar.text_input(
                'RTSP URL:',
                'eg: rtsp://admin:name6666@198.162.1.58/cam/realmonitor?channel=0&subtype=0'
            )
            pred = st.checkbox('Predict Using Yolov8')
            cap = cv2.VideoCapture(rtsp_url)

        time_before = 0

        if pred:
            stframe1 = st.empty()
            stframe2 = st.empty()
            while True:
                success, img = cap.read()
                success, img2 = cap2.read()
                
                current_no_class = {'Camera No.': [],'Object': []}

                if not success:
                    st.error(
                        f"{options} NOT working\nCheck {options} properly!!",
                        icon="🚨"
                    )
                    break

                img, current_no_class = get_yolo(img, model_type, model, confidence, color_pick_list, class_labels, draw_thick, current_no_class, 'Camera 1')
                FRAME_WINDOW.image(img, channels='BGR')

                img2, current_no_class = get_yolo(img2, model_type, model, confidence, color_pick_list, class_labels, draw_thick, current_no_class, 'Camera 2')
                FRAME_WINDOW2.image(img2, channels='BGR')   
                    
                # FPS
                c_time = time.time()
                fps = 1 / (c_time - p_time)
                p_time = c_time
                
                # # Current number of classes
                # class_fq = Counter(i for sub in current_no_class for i in set(sub))
                # print(class_fq)
                # class_fq = json.dumps(class_fq, indent = 4)
                # class_fq = json.loads(class_fq)
                # #Current classes detected in the current frame
                # df_fq = pd.DataFrame(class_fq.items(), columns=['Class', 'Number'])
                class_fq = current_no_class
                df_fq = pd.DataFrame(class_fq)
                df_fq = df_fq.drop_duplicates()


                time_now = time.time() 

                # Updating Inference results (Display results)
                get_system_stat(stframe1, stframe2, fps, df_fq, img, img2, time_now, time_before, manualMode)
                time_before = logTime.time_before
        else:
            time_before = 0

    if selected == "Log data":
        #----------------- Create a dictionary of sample data-------------------#
        data = sprd.list_log()

        # Create a dataframe from the dictionary
        df = pd.DataFrame(data)
        # Display the dataframe using st.dataframe()
        st.dataframe(df, use_container_width=True)

        # Group the data by date and count the number of objects detected
        data = df.groupby('Date')['Detected'].count().reset_index()

        # Create the line chart
        st.line_chart(data.set_index('Date'))
        
        
        
        
        # chart_data = pd.DataFrame(np.random.randn(20, 3), columns=['Knife', 'Pistol', 'Blunt weapon'])
        # st.line_chart(chart_data)