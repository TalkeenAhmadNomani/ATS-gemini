import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(prompt):
    """Get response from Gemini AI with strict JSON format."""
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    
    print("Raw Response from API:", response.text)  # Debugging: Check what API returns
    return response.text.strip()

def extract_text_from_pdf(uploaded_file):
    """Extract text from an uploaded PDF file."""
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""  # Handle NoneType errors
    print("Extracted Resume Text:", text[:500])  # Debugging: Print first 500 chars
    return text.strip()

# Streamlit UI
st.title("Smart ATS - Resume Evaluator")
st.text("Enhance Your Resume for ATS Compatibility")

# Job Description Input
jd = st.text_area("Paste the Job Description Here")

# Resume File Upload
uploaded_file = st.file_uploader("Upload Your Resume (PDF Only)", type="pdf")

# Buttons for Actions
submit = st.button("Evaluate Resume")
match_percentage = st.button("Get Match Percentage")

if submit or match_percentage:
    if uploaded_file and jd.strip():
        resume_text = extract_text_from_pdf(uploaded_file)

        if submit:
            input_prompt = f"""
            You are an advanced ATS scanner trained in resume evaluation. 
            
            Your task is to evaluate the resume against the job description and return:
            - **Match Percentage**
            - **Missing Keywords**
            - **Profile Summary**

            Resume:
            {resume_text}

            Job Description:
            {jd}

            Respond ONLY in **valid JSON format**:
            {{
              "Match Percentage": "XX%",
              "Missing Keywords": ["keyword1", "keyword2"],
              "Profile Summary": "Brief summary of strengths and weaknesses"
            }}
            """

        elif match_percentage:
            input_prompt = f"""
            You are an ATS resume analyzer. 

            Compare the resume with the job description and return ONLY:
            {{
              "Match Percentage": "XX%",
              "Missing Keywords": ["keyword1", "keyword2"]
            }}
            """

        # Get response
        response_text = get_gemini_response(input_prompt)

        try:
            # Extract valid JSON from response
            start_index = response_text.find("{")
            end_index = response_text.rfind("}") + 1
            json_response = response_text[start_index:end_index]
            
            print("Extracted JSON:", json_response)  # Debugging: Check JSON output
            
            response_json = json.loads(json_response)  # Convert to dictionary

            # Display results
            st.subheader("JD Match: {}".format(response_json.get("Match Percentage", "N/A")))
            st.subheader("Missing Keywords:")
            missing_keywords = response_json.get("Missing Keywords", [])
            if missing_keywords:
                st.write("\n".join(f"- {keyword}" for keyword in missing_keywords))
            else:
                st.write("No missing keywords.")

            if submit:
                st.subheader("Profile Summary:")
                st.write(response_json.get("Profile Summary", "No profile summary available."))

        except json.JSONDecodeError:
            st.error("Error: Invalid response format. Try again.")
            print("Invalid JSON Response:", response_text)  # Debugging: Check error

    else:
        st.warning("Please upload a resume and provide a job description before proceeding!")
