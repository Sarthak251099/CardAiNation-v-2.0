from flask import url_for
from flask_mail import Message
from cardination import mail
import random
import re
import math
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

line_num = -1
flag = False
all_symptom = ['itching','skin_rash','nodal_skin_eruptions','sneezing','shivering','chills','joint_pain','stomach_pain','acidity','ulcers_on_tongue','muscle_wasting','vomiting','burning_micturition','spotting_ urination','fatigue','weight_gain','anxiety','cold_hands_and_feets','mood_swings','weight_loss','restlessness','lethargy','patches_in_throat','irregular_sugar_level','cough','fever','sunken_eyes','breathlessness','sweating','dehydration','indigestion','headache','yellowish_skin','dark_urine','nausea','loss_of_appetite','pain_behind_the_eyes','back_pain','constipation','abdominal_pain','diarrhoea','mild_fever','yellow_urine','yellowing_of_eyes','acute_liver_failure','fluid_overload','swelling_of_stomach','swelled_lymph_nodes','malaise','blurred_and_distorted_vision','phlegm','throat_irritation','redness_of_eyes','sinus_pressure','runny_nose','congestion','chest_pain','weakness_in_limbs','fast_heart_rate','pain_during_bowel_movements','pain_in_anal_region','bloody_stool','irritation_in_anus','neck_pain','dizziness','cramps','bruising','obesity','swollen_legs','swollen_blood_vessels','puffy_face_and_eyes','enlarged_thyroid','brittle_nails','swollen_extremeties','excessive_hunger','extra_marital_contacts','drying_and_tingling_lips','slurred_speech','knee_pain','hip_joint_pain','muscle_weakness','stiff_neck','swelling_joints','movement_stiffness','spinning_movements','loss_of_balance','unsteadiness','weakness_of_one_body_side','loss_of_smell','bladder_discomfort','foul_smell_of urine','continuous_feel_of_urine','passage_of_gases','internal_itching','toxic_look_(typhos)','depression','irritability','muscle_pain','altered_sensorium','red_spots_over_body','belly_pain','abnormal_menstruation','dischromic _patches','watering_from_eyes','increased_appetite','polyuria','family_history','mucoid_sputum','rusty_sputum','lack_of_concentration','visual_disturbances','receiving_blood_transfusion','receiving_unsterile_injections','coma','stomach_bleeding','distention_of_abdomen','history_of_alcohol_consumption','fluid_overload','blood_in_sputum','prominent_veins_on_calf','palpitations','painful_walking','pus_filled_pimples','blackheads','scurring','skin_peeling','silver_like_dusting','small_dents_in_nails','inflammatory_nails','blister','red_sore_around_nose','yellow_crust_ooze']
diagnosis = False

df = pd.read_csv('Training.csv')
df.head()
X = df.iloc[:, :-1]
y = df['prognosis']
rf_clf = RandomForestClassifier()
rf_clf.fit(X, y)


def send_reset_email(patient):
    token = patient.get_reset_token()
    msg = Message('Password Reset Request', sender = 'noreply@demo.com', recipients = [patient.email])
    msg.body = f'''To reset the password, visit the following link:
{url_for('patient.reset_token',token = token,_external = True)}

If you did not make this request then simply ignore this message and no changes will be made.'''
    mail.send(msg)

def worker(mesg):
    f = open("response.txt","r")
    lines = f.readlines()
    num_of_lines = len(lines)
    num = 0
    line_to_print = -1
    counter = -1

    for i in range(num_of_lines):
        wordset = lines[i].strip()
        a = checkMaxOccurence(wordset.split("|"),mesg)
        if num<a:
            num = a
            line_to_print = counter+1
        counter+=1

    if line_to_print is not -1:
        return lines[line_to_print].strip().split("|")[1]
    else:
        return "I am not trained to answer this."

def checkMaxOccurence(wordset,message):
    count = 0
    message_arr = message.split(" ")
    wordset_arr = wordset[0].split(".")
    for i in range(len(message_arr)):
        search_list = wordset_arr.count(message_arr[i].lower())
        count = count + search_list
    return count


def predict(sym):
    global rf_clf,X,Y
    symptoms_dict = {}
    for index, symptom in enumerate(X):
        symptoms_dict[symptom] = index
    input_vector = np.zeros(len(symptoms_dict))
    for i in sym:
        input_vector[[symptoms_dict[i]]] = 1
    rf_clf.predict_proba([input_vector])
    pred = rf_clf.predict([input_vector])
    return str(pred[0])

def searching(mes):
    global flag, fillform, all_symptom
    global line_num, counter, diagnosis
    h= open("sentences.txt","r")
    line = h.readlines()
    num_of_line = len(line)
    mes = mes.lower()
    if mes.find("order")!=-1:
        med = mes.split("order")[1].strip()
        browser = webdriver.Chrome("C:\\Users\\sarth\\Desktop\\chromedriver.exe")
        browser.maximize_window()
        browser.get("https://www.netmeds.com/")
        search_bar = browser.find_element_by_xpath("//*[@id='search']")
        search_bar.send_keys(med)
        search = browser.find_element_by_xpath("//*[@id='search_form']/button")
        search.click()
        browser.implicitly_wait(30)
        return "Processing order request from netmeds"
        
    if mes == "run diagnosis":
        diagnosis = True
        return "Give comma separated symptoms which you are facing."
    if diagnosis==True:
        symptoms = mes.split(",")
        simp = []
        for i in range(len(symptoms)):
            symptoms[i] = (symptoms[i].strip()).replace(" ", "_")
            if symptoms[i] in all_symptom:
                simp.append(symptoms[i])
        result = predict(simp)
        diagnosis = False
        return f'You are mostly suffering from {result}'
        
    if flag==True:
        x = line[line_num].split("|")
        y = x[0].split("{")
        matchfrom = y[0].split(",")
        matchfromnext = []
        for i in range(1,len(y)):
            matchfromnext.append(y[i].split("*")[0])
        responsenext = []
        for i in range(1,len(y)):
            responsenext.append(y[i].split("*")[1])
        for i in range(len(matchfromnext)):
            if mes==matchfromnext[i]:
                flag=False
                return responsenext[i]

        if flag==True:
            flag = False
            for i in range(num_of_line):
                res = line[i].split("|")
                z = res[0].split("{")
                if len(z)<2:
                    sentences = res[0].split(",")
                    if sentences.count(mes)>0:
                        choices=res[1].split("@")
                        a=random.choice(choices)
                        line_num = i
                        return a
                else:
                    matchfrom = z[0].split(",")
                    if matchfrom.count(mes)>0:
                        line_num = i
                        flag = True
                        some = res[1].split("@")
                        return random.choice
                    else:
                        flag = False 

    elif flag==False:
        for i in range(num_of_line):
            res = line[i].split("|")
            z = res[0].split("{")
            if len(z)<2:
                sentences = res[0].split(",")
                if sentences.count(mes)>0:
                    choices=res[1].split("@")
                    a=random.choice(choices)
                    h.close()
                    line_num = i
                    return a
            else:
                matchfrom = z[0].split(",")
                if matchfrom.count(mes)>0:
                    line_num = i
                    flag = True
                    some = res[1].split("@")
                    return random.choice(some)
                else:
                    flag = False 