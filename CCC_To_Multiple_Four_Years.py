import streamlit as st
import pandas as pd
import requests, json
import app_functions

st.set_page_config(page_title="See articulations from a CCC to multiple four-years",
                   page_icon="📈",
                   layout="wide")

st.title("Assist Planner")
st.header("Which classes should I take for transfer?")

st.markdown(
        """
        <style>
        .stMultiSelect [data-baseweb=select] span{
            max-width: 400px;
        }""",
        unsafe_allow_html=True,
    )

cc_to_fy_dict = {}
# {"English 101": {"UCB":[{course:"ENG 01A", attributes:""}]}

year = st.number_input("Enter start year", min_value=2023, value=2024, step=1)
year_id = year - 1949

cc_option = st.selectbox("My CCC",
                         app_functions.get_CC_data(),
                         format_func=app_functions.display_names_codes,
                         index=None)
if cc_option:
    cc_code = cc_option["code"]
    cc_id = cc_option["id"]

with st.form("four_year_selection"):

    four_year_selection = st.multiselect(
    "Select four year universities",
    app_functions.get_four_year_data(),
    format_func=app_functions.display_names_codes,
    disabled=not (bool(year) and bool(cc_option)))

    st.form_submit_button("Select majors")


with st.form("major_selection"):
    for fy_school in four_year_selection:
        st.multiselect(fy_school['name'],
                    app_functions.get_majors_data(cc_option['id'],fy_school['id'],year_id),
                    key=fy_school['code'],
                    format_func=app_functions.display_label_major)

    major_submit = st.form_submit_button("Submit")


if major_submit:
    #Create cc_to_fy_dict

    for fy_school in four_year_selection:
        fy_code = fy_school["code"]
        major_selection = st.session_state[fy_code]
        for major in major_selection:
            major_label = major['label']
            major_key = major['key']
            course_articulations = app_functions.get_course_articulations(major_key)
            for course_articulation in course_articulations:
                if app_functions.get_articulation_type(course_articulation) not in ["Series", "Course", "Requirements"]:
                    continue
                articulated_fy_course = app_functions.get_articulated_fy_course(course_articulation)
                articulating_cc_courses = app_functions.get_articulating_cc_courses(course_articulation)

                #st.write(course_articulation)
                #st.write(articulated_fy_course)
                #st.write(articulating_cc_courses)

                for articulating_cc_course in articulating_cc_courses:

                    cc_course_names = []
                    course_conjunction = articulating_cc_course["conjunction"]
                    if course_conjunction == "Or":
                        for course in articulating_cc_course["courses"]:
                            cc_course_names += [course]
                    else:
                        cc_course_name = ", ".join(articulating_cc_course["courses"])
                        cc_course_names += [cc_course_name]

                    attributions = articulating_cc_course["attributions"]

                    for cc_course_name in cc_course_names:
                        if cc_course_name not in cc_to_fy_dict:
                            cc_to_fy_dict[cc_course_name] = {}

                        if fy_code not in cc_to_fy_dict[cc_course_name]:
                            cc_to_fy_dict[cc_course_name][fy_code] = {}
                        
                        if major_label not in cc_to_fy_dict[cc_course_name][fy_code]:
                            cc_to_fy_dict[cc_course_name][fy_code][major_label] = {"course":[], "attributions": []}
                        
                        if cc_course_name not in cc_to_fy_dict[cc_course_name][fy_code][major_label]["course"]:
                            cc_to_fy_dict[cc_course_name][fy_code][major_label]["course"] += [articulated_fy_course]
                            cc_to_fy_dict[cc_course_name][fy_code][major_label]["course"].sort()
                        for attribution in attributions:
                            if attribution not in cc_to_fy_dict[cc_course_name][fy_code][major_label]["attributions"]:
                                cc_to_fy_dict[cc_course_name][fy_code][major_label]["attributions"] += [attribution]
                                                                                                        
    rows = []

    for cc_course, fys in cc_to_fy_dict.items():
        row = {cc_code: cc_course}
        for fy, majors_dict in fys.items():
            for major, details in majors_dict.items():
                row[(fy, major, "Course")] = ", ".join(details["course"])
                row[(fy, major, "Notes")] = ". ".join(details["attributions"])
        rows.append(row)

    df = pd.DataFrame(rows)

    first_col = df.pop(cc_code)

    multi_cols = pd.MultiIndex.from_tuples(
        [c for c in df.columns if isinstance(c, tuple)],
        names=["FY", "Major", "Type"]
    )

    df.columns = multi_cols
    df.insert(0, cc_code, first_col)

    st.dataframe(df)

    # Download button

    st.download_button(
        label="Download CSV",
        data=df.to_csv().encode("utf-8"),
        file_name=f"%s.csv" % (cc_code),
        mime="text/csv",
        icon=":material/download:",
    )


    st.write("For more details, click the following to see your college's articulation for your school and major on Assist:") 

    # Button to Assist URL
    for fy_school in four_year_selection:
        fy_code = fy_school["code"]
        fy_id = fy_school["id"]
        major_selection = st.session_state[fy_code]
        for major in major_selection:
            major_label = major['label']
            major_key = major['key']
            st.link_button(f"%s %s" % (fy_code, major_label),
                        f"https://assist.org/transfer/results?year=%s&institution=%d&agreement=%d&agreementType=to&viewAgreementsOptions=false&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=%s"
                        % (year_id, cc_id,fy_id,major_key))

