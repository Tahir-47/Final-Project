import string
from utils.plots import plot_one_box
from PIL import ImageColor
import subprocess
import streamlit as st
import psutil


#import database as db
from datetime import datetime
import spreadsheetData as sprd

import time

import twilioSMS as twil

import logTime

import pygame

from PIL import Image
import numpy as np
import cv2

pygame.mixer.init()
sound = pygame.mixer.Sound("alarm.mp3")


msgs = {'pistol': 'Stay calm, comply with their demands, and avoid sudden movements that may escalate the situation.', 'knife': 'Keep a safe distance, try to create barriers or find objects to defend yourself, and aim for vulnerable areas if self-defense is necessary.', 'blunt_weapon': 'Keep your distance, evade or block their strikes, and look for opportunities to escape or seek help.', 'fire': 'Alert others, evacuate calmly following the established emergency exits, and avoid elevators while prioritizing your safety.', 'smoke': ' Stay low to avoid inhaling smoke, cover your mouth with a cloth, and follow evacuation procedures while feeling surfaces for heat before touching them.', 
'rifle': 'Take cover immediately, find a secure location out of the attacker\'s line of sight, and contact authorities while providing them with accurate information about the situation.'}

camLocation = {'Camera 1': 'Floor 1', 'Camera 2': 'Floor2'}

def get_gpu_memory():
    result = subprocess.check_output(
        [
            'nvidia-smi', '--query-gpu=memory.used',
            '--format=csv,nounits,noheader'
        ], encoding='utf-8')
    gpu_memory = [int(x) for x in result.strip().split('\n')]
    return gpu_memory[0]

def color_picker_fn(classname, key):
    color_picke = st.sidebar.color_picker(f'{classname}:', '#ff0003', key=key)
    color_rgb_list = list(ImageColor.getcolor(str(color_picke), "RGB"))
    color = [color_rgb_list[2], color_rgb_list[1], color_rgb_list[0]]
    return color


def get_yolo(img, model_type, model, confidence, color_pick_list, class_list, draw_thick, current_no_class, camNo):
    # current_no_class = []
    results = model(img)

    if model_type == 'YOLOv8':
        for result in results:
            bboxs = result.boxes.xyxy
            conf = result.boxes.conf
            cls = result.boxes.cls
            for bbox, cnf, cs in zip(bboxs, conf, cls):
                xmin = int(bbox[0])
                ymin = int(bbox[1])
                xmax = int(bbox[2])
                ymax = int(bbox[3])
                if cnf > confidence:
                    plot_one_box([xmin, ymin, xmax, ymax], img, label=class_list[int(cs)],
                                    color=color_pick_list[int(cs)], line_thickness=draw_thick)
                    # current_no_class.append([class_list[int(cs)]])
                    current_no_class['Object'].append(class_list[int(cs)])
                    current_no_class['Camera No.'].append(camNo)
    return img, current_no_class


def get_system_stat(stframe1, stframe2, fps, df_fq, pic, pic2, time_now, time_before, manualMode: bool):
    # Updating Inference results (FPS, Title)
    with stframe1.container():
        st.markdown("<h2>Inference Statistics</h2>", unsafe_allow_html=True)
        if round(fps, 4)>1:
            st.markdown(f"<h4 style='color:green;'>Frame Rate: {round(fps, 4)}</h4>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h4 style='color:red;'>Frame Rate: {round(fps, 4)}</h4>", unsafe_allow_html=True)
    
    #Detected objects table
    with stframe2.container():
        st.markdown("<h3>Detected objects in current Frame</h3>", unsafe_allow_html=True)
        st.dataframe(df_fq, use_container_width=True)
        for ind in df_fq.index:
            # Get the current date and time
            current_datetime = datetime.now()

            # Extract the time components
            current_time = current_datetime.strftime("%H:%M:%S")

            # Extract the date components
            current_date = current_datetime.strftime("%Y-%m-%d")
    
                
            if df_fq['Object'][ind] == 'pistol' or df_fq['Object'][ind] == 'knife' or df_fq['Object'][ind] == 'blunt_weapon' or df_fq['Object'][ind] == 'fire' or df_fq['Object'][ind] == 'smoke' or df_fq['Object'][ind] == 'rifle':
                st.markdown(f"<h3 style='color:red;'>Detected a {df_fq['Object'][ind]} on {df_fq['Camera No.'][ind]} 🚨</h3>", unsafe_allow_html=True)
                if df_fq['Camera No.'][ind] == 'Camera 1':
                    st.image(pic, use_column_width=True, channels='BGR')
                else:
                    st.image(pic2, use_column_width=True, channels='BGR')  


                # Check if the time difference since the previous detection is greater than 10 seconds
                if time_now - time_before > 10:
                    sprd.insert_log(f"{df_fq['Object'][ind]}", f"{df_fq['Camera No.'][ind]}", current_time, current_date)
                    sound.play()
                    # if not manualMode:
                    #     twil.sendSMS(f"Detected {df_fq['Object'][ind]} on {camLocation[df_fq['Camera No.'][ind]]}. {msgs[df_fq['Object'][ind]]}")

                    time_before = time_now  # Update the previous detection time

                    # Update the value of my_variable
                    logTime.time_before = time_before

                    # Save the updated value back to file1.py
                    with open("logTime.py", "w") as file:
                        file.write(f"time_before = {logTime.time_before}")
                        
                
                    
                    if df_fq['Camera No.'][ind] == 'Camera 1':
                        image_array = np.array(pic)  # Replace `...` with your actual ndarray representing the image
                    else:
                        image_array = np.array(pic2)  # Replace `...` with your actual ndarray representing the image

                    image_array_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(image_array_rgb)
                    image.save(f"C:/Users/hamim/Documents/TahirProjects/YoloStreamlit/SavedImages/{df_fq['Object'][ind]}_{current_date}_{time.time()}.jpg")  # Replace with the desired save path and file name

            



    
