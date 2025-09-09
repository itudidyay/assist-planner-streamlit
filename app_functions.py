import streamlit as st
import pandas as pd
import requests, json

@st.cache_data
def get_school_dict():
    school_dict = pd.read_csv("data/schoolData.csv", header=0)
    return school_dict.to_dict(orient='records')

@st.cache_data
def get_CC_data():
    CC_data = []
    CC_dict = get_school_dict()
    for school in CC_dict:
        if school['category']== 2:
            CC_data.append(school)
    sorted_CC_data = sorted(CC_data, key=lambda d: d['name'])
    return sorted_CC_data

@st.cache_data
def get_four_year_data():
    fy_data = []
    fy_dict = get_school_dict()
    for school in fy_dict:
        if school['category'] != 2:
            fy_data.append(school)
    #sort the list by uc, csu, indie in that order, then alphabet
    school_sort = {1:0,0:1,5:2}
    sorted_fy_data = sorted(fy_data,
                            key=lambda d: (school_sort[d["category"]], d["name"]))
    return sorted_fy_data

def display_names_codes(option):
    return f'{option["name"]} ({option["code"]})'

@st.cache_data
def get_majors_data(cc_id, fy_id, year_id):
    majors_url = requests.get(f"https://assist.org/api/agreements?receivingInstitutionId=%s&sendingInstitutionId=%s&academicYearId=%s&categoryCode=major"
                             % (fy_id, cc_id, year_id))
    if majors_url.status_code == 200:
        majors_data = majors_url.json()["reports"]
        sorted_majors_data = sorted(majors_data, key=lambda d: d['label'])
        return sorted_majors_data
    else:
        raise ValueError('URL did not load')
    
@st.cache_data
def get_course_articulations(major_key):
    course_art_url = requests.get(f"https://assist.org/api/articulation/Agreements?Key=%s"
                             % major_key)
    if course_art_url.status_code == 200:
        course_art_json = course_art_url.json()
        course_art_dict = json.loads(course_art_json["result"]["articulations"])
        return course_art_dict
    else:
        raise ValueError('URL did not load')
    
def get_articulation_type(course_dict):
    return course_dict["articulation"]["type"]

def get_articulated_fy_course(course_dict):
    if course_dict["articulation"]["type"] == "Series":
        fy_course = course_dict["articulation"]["series"]["name"]
    elif course_dict["articulation"]["type"] == "Course":
        fy_course = course_dict["articulation"]["course"]["prefix"] + " " + course_dict["articulation"]["course"]["courseNumber"]
    elif course_dict["articulation"]["type"] == "Requirement":
        fy_course = course_dict["articulation"]["requirement"]["name"]
    elif course_dict["articulation"]["type"] == "GeneralEducation":
        fy_course = course_dict["articulation"]["generalEducationArea"]["name"] # this shouldn't happen
    else:
        print(course_dict["articulation"]["type"])
        raise ValueError('Type of receiving course is not series or course.')
    return fy_course
                        
def get_articulating_cc_courses(course_dict):
    cc_course_list = [] 
    articulating_group = course_dict["articulation"]["sendingArticulation"]["items"]
    if articulating_group != []:
        for subgroup in articulating_group:
            subgroup_list = {"attributions":[], "conjunction":None, "courses":[]}
            course_conjunction = subgroup["courseConjunction"]

            for attribute in subgroup["attributes"]: # group attribute
                content = attribute["content"]
                if content not in subgroup_list["attributions"]:
                    subgroup_list["attributions"] += [content]
                    
            for sending_course in subgroup["items"]:
                for attribute in sending_course["attributes"]: # individual course attribute
                    content = attribute["content"]
                    if content not in subgroup_list["attributions"]:
                        subgroup_list["attributions"] += [content]
                subgroup_list["courses"] += [sending_course["prefix"] + " " + sending_course["courseNumber"]]
            subgroup_list["conjunction"] = course_conjunction
            subgroup_list["courses"].sort()
            cc_course_list += [subgroup_list]
    return cc_course_list
    
def display_label_major(option):
    return option["label"]