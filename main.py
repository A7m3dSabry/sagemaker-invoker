import streamlit as st
import requests
import pandas as pd

lambda_endpoint = "https://8t4pyjhqx0.execute-api.us-west-2.amazonaws.com/default/DEBI_InvokingSageMaker"


def request_lambda(data):
    response = requests.post(lambda_endpoint, json={"text": data})
    return response.text


# Function to summarize text
def summarize_text(text):
    return request_lambda(text)


st.set_page_config(layout="wide")
st.title("Automatic Radiology Impression Report Generator")

# Section for text input
st.header("Finding")
input_text = st.text_area("Enter Finding", key="input_area")

# Button to trigger summarization for text input
if st.button("Generate Impressions", key="generate_btn"):
    if input_text.strip():
        summarized_text = summarize_text(input_text)
        st.text_area("Generated Impressions:", summarized_text)
    else:
        st.error("Please enter some text to generate impressions.")

# Section for CSV file upload
st.header("Upload CSV File")
csv_file = st.file_uploader("Choose a CSV file", type="csv")

if csv_file:
    # Read CSV file
    df = pd.read_csv(csv_file)

    # Add columns for status and results if they do not exist
    if 'Status' not in df.columns:
        df['Status'] = 'Pending'
    if 'Result' not in df.columns:
        df['Result'] = 'Pending'

    # Display the uploaded CSV file with status and results
    st.write("CSV File Preview:")
    st.write(df)

    # Option to select a column from the CSV
    column_name = st.selectbox("Select the column to process", df.columns)

    # Button to process the CSV file
    if st.button("Process CSV File"):
        if column_name:
            # Iterate over the rows of the DataFrame
            for index, row in df.iterrows():
                if df.at[index, 'Status'] == 'Pending':  # Process only pending rows
                    data = row[column_name]
                    df.at[index, 'Status'] = 'Processing'
                    # Update the DataFrame to reflect the processing status
                    st.write("Updating row status...")
                    result = summarize_text(data)
                    df.at[index, 'Result'] = result
                    df.at[index, 'Status'] = 'Completed'

            # Display the updated DataFrame
            st.write("Processed Results:")
            st.write(df)
        else:
            st.error("Please select a column to process.")

