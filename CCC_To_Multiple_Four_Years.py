import streamlit as st
import pandas as pd
import requests, json

st.set_page_config(page_title="See articulations from a CCC to multiple four-years",
                   page_icon="📈",
                   layout="wide")

class School:
    def __init__(self, name):
        self.name = name
        self.code = None
        self.id = None
        self.category = None

    def fillData(self):
        for school in getCCDict():
            if school["name"] == self.name:
                self.code = school["code"]
                self.id = school["id"]
                self.category = school["category"]
        

    def __repr__(self):
        return f"School(name={self.name}, code={self.code}, id={self.id}, category={self.category})"
    
class Major:
    def __init__(self, name, key):
        self.name = name
        self.key = key

    def __repr__(self):
        return f"Major(name={self.name}, key={self.key}"


@st.cache_data
def getCCDict():
    CCDict = pd.read_csv("data/schoolData.csv", header=0)
    return CCDict.to_dict(orient='records')

@st.cache_data
def getCCNames():
    CCNames = []
    CCDict = getCCDict()
    for school in CCDict:
        if school['category']== 2:
            CCNames.append(school['name'])
    CCNames.sort()
    return CCNames

@st.cache_data
def getCCNamesAndCodes():
    CCNamesAndCodes = []
    CCDict = getCCDict()
    for row in CCDict:
        if row['category'] == 2:
            CCNamesAndCodes.append(f"{row['name']} ({row['code']})")
    CCNamesAndCodes.sort()
    return CCNamesAndCodes

@st.cache_data
def get4YNames():
    CCNames = []
    CCDict = getCCDict()
    for row in CCDict:
        if row['category'] != 2:
            CCNames.append(row['name'])
    CCNames.sort()
    return CCNames

@st.cache_data
def getFYNamesAndCodes():
    CCNamesAndCodes = []
    CCDict = getCCDict()
    for row in CCDict:
        if row['category'] != 2:
            CCNamesAndCodes.append(f"{row['name']} ({row['code']})")
    CCNamesAndCodes.sort()
    return CCNamesAndCodes

@st.cache_data
def getDictOfMajors(CCSchoolID, FYSchoolID, yearStart):
    if not st.session_state.selectedCCC:
        return None
    yearID = yearStart - 1949
    urlMajors = requests.get(f"https://assist.org/api/agreements?receivingInstitutionId={FYSchoolID}&sendingInstitutionId={CCSchoolID}&academicYearId={yearID}&categoryCode=major")
    if urlMajors.status_code == 200:
        majorsDict = urlMajors.json()["reports"]
        return majorsDict
    else:
        raise ValueError('URL did not load')
    
@st.cache_data
def getListOfMajors(majorDict):
    if majorDict == None:
        return None
    majorsList = []
    for major in majorDict:
        majorsList +=  [Major(major['label'], major['key'][-36:])]
    return majorsList

@st.cache_data
def getMajorNames(majorsList):
    majorsNamesList = []
    for major in majorsList:
        majorsNamesList += [major.name]
    majorsNamesList.sort()
    return majorsNamesList

@st.cache_data
def getArticulatingCourses(year, CCSchoolID, FYSchoolID, MajorID):
    yearID = year - 1949
    coursesURL = requests.get(f"https://assist.org/api/articulation/Agreements?Key={yearID}/{CCSchoolID}/to/{FYSchoolID}/Major/{MajorID}")
    coursesDict = json.loads(coursesURL.json()["result"]["articulations"])
    return coursesDict

@st.cache_data
def getFullNameOfReceivingCourse(articulatingCourse):
    if articulatingCourse["articulation"]["type"] == "Series":
        return articulatingCourse["articulation"]["series"]["name"]
    elif articulatingCourse["articulation"]["type"] == "Course":
        return articulatingCourse["articulation"]["course"]["prefix"] + " " + articulatingCourse["articulation"]["course"]["courseNumber"]
    elif articulatingCourse["articulation"]["type"] == "Requirement":
        return articulatingCourse["articulation"]["requirement"]["name"]
    else:
        print(articulatingCourse["articulation"]["type"])
        raise ValueError('Type of receiving course is not series or course.')

@st.cache_data
def getFullNameOfSendingCourse(articulatingCourse):
    sendingCoursesList = []
    if articulatingCourse["articulation"]["sendingArticulation"]["items"] != []:
        for subgroupOfCourses in articulatingCourse["articulation"]["sendingArticulation"]["items"]:
            subgroupCourseList = []
            for sendingCourse in subgroupOfCourses["items"]:
                subgroupCourseList += [sendingCourse["prefix"] + " " + sendingCourse["courseNumber"]]
            sendingCoursesList += [f' {subgroupOfCourses["courseConjunction"].lower()} '.join(subgroupCourseList)]

        return " or\n".join(sendingCoursesList)
    
@st.cache_data
def processArticulatingCourse(artCourse):
    receivingCourseName = getFullNameOfReceivingCourse(artCourse)
    sendingCourseName = getFullNameOfSendingCourse(artCourse)

st.title("One CCC to Many Four Year")
st.write(
    "Let's start building!."
)
# options = 

#st.cache_data.clear()

year = st.number_input("Enter start year", min_value=2023, value=2024, step=1)
CCCoption = st.selectbox("CCC",
                         getCCNames(),
                         index=None)

selectedCCC = School(CCCoption)
selectedCCC.fillData()
if selectedCCC not in st.session_state:
    st.session_state.selectedCCC = None
st.session_state.selectedCCC = selectedCCC

if "selectionFYandMajorID" not in st.session_state:
    st.session_state["selectionFYandMajorID"] = [0]
if "selectionFYandMajor" not in st.session_state:
    st.session_state["selectionFYandMajor"] = {}
    st.session_state["selectionFYandMajor"][0] = {"school": None, "major": None}

if "artCoursesDict" not in st.session_state:
    st.session_state["artCoursesDict"] = {}

def add_selectbox():
    new_id = st.session_state["selectionFYandMajorID"][-1] + 1
    st.session_state["selectionFYandMajorID"].append(new_id)
    st.session_state["selectionFYandMajor"][new_id] = {"school": None, "major": None}
    st.rerun()

#st.write(st.session_state)

for i, id in enumerate(st.session_state.selectionFYandMajorID):
    tile = st.container(border=False)
    fourYearCol, majorCol, delCol = tile.columns([5, 5, 1], vertical_alignment="bottom")

    with fourYearCol:

        def getSchoolIndex():
            if st.session_state.selectionFYandMajor[id]["school"] and f"{id}_four_year" in st.session_state:
                schoolName = st.session_state[f"{id}_four_year"]
                schoolIndex = get4YNames().index(schoolName)
                return schoolIndex
            else:
                return None
        
        def majorIsSelected():
            st.session_state.selectionFYandMajor[id]["major"] = None
            selected_school = School(
                name=st.session_state[f"{id}_four_year"])
            selected_school.fillData()
            st.session_state["selectionFYandMajor"][id]["school"] = selected_school

        fourYearSelection = st.selectbox(
            f"Four Year {id}",
            get4YNames(),
            key=f"{id}_four_year",
            index=getSchoolIndex(),
            placeholder="Select a school",
            disabled=not bool(selectedCCC.name)
        )
        if fourYearSelection:
            majorIsSelected()

    with majorCol:
        #st.write(st.session_state.selectedCCC.id, st.session_state["selectionFYandMajor"][id]["school"].id, year)
        if st.session_state["selectionFYandMajor"][id]["school"] is not None:
            majorsDict = getDictOfMajors(st.session_state.selectedCCC.id, st.session_state["selectionFYandMajor"][id]["school"].id, year)
            majorsList = getListOfMajors(majorsDict)
            majorsNamesList = getMajorNames(majorsList)
        else:
            majorsDict = {}
            majorsList = []
            majorsNamesList = []

        def getMajorIndex():
            if st.session_state.selectionFYandMajor[id]["major"]:
                majorName = st.session_state.selectionFYandMajor[id]["major"].name
                majorIndex = majorsNamesList.index(majorName)
                return majorIndex
            else:
                return None
            
        def getMajorKey(majorName):
            for major in majorsList:
                if majorName == major.name:
                    return major.key
            return None
            
        majorSelection = st.selectbox(
            f"Major",
            majorsNamesList,
            key=f"{id}_major",
            index=getMajorIndex(),
            placeholder="Select a major",
            disabled=not bool(st.session_state.selectionFYandMajor[id]["school"])
        )

        if majorSelection:
            majorKey = getMajorKey(majorSelection)
            selectedMajor = Major(
                name=majorSelection,
                key=majorKey)
            st.session_state["selectionFYandMajor"][id]["major"] = selectedMajor

    with delCol:
        if st.button("❌", key=f"{id}_remove") and len(st.session_state["selectionFYandMajorID"]) > 1:
            del st.session_state["selectionFYandMajor"][id]
            # Optional cleanup of old keys
            for k in [f"{id}_four_year", f"{id}_major", f"{id}_remove"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.session_state["selectionFYandMajorID"].pop(i)
            st.rerun()

addFourYearButton = st.button("➕ Add Four Year")
if addFourYearButton:
    add_selectbox()

st.write(st.session_state)

articulated = getArticulatingCourses(2024, 3, 117, "d0cae58f-3c0f-4bbe-cc3d-08dc9134ea85")
#st.write(articulated)

# testdict = getListOfMajors(137, 117, 2024)
# st.dataframe(
#     testdict,
#     use_container_width=True,
#     column_config={"year": st.column_config.TextColumn("Year")},
# )