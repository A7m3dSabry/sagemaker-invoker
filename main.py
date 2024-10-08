import streamlit as st
import requests
import pandas as pd
import time

lambda_endpoint = st.secrets["LAMBDA_ENDPOINT"]
api_key = st.secrets["API_KEY"]


def call_lambda_api(data):
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    try:
        # Make a POST request with the provided data
        response = requests.post(lambda_endpoint, headers=headers, json=data)

        # Raise an error for bad responses (4xx or 5xx)
        response.raise_for_status()

        return response.json().get("out")  # Assuming the response is in JSON format

    except requests.exceptions.RequestException as e:
        return f"Error: {e}"


def summarize_text(text, types):
    return call_lambda_api({"findings": text, "types": types})


st.set_page_config(layout="wide")
st.title("Automatic Radiology Impression Report Generator")

tab1, tab2 = st.tabs(["Text Generation", "Batch Generation"])

with tab1:
    # Section for text input
    st.header("Finding")
    input_text = st.text_area("Enter Finding", key="input_area")

    # Button to trigger summarization for text input
    selected = st.selectbox('Make a selection:', ('CT', 'MR', 'Xray'))
    if st.button("Generate Impressions", key="generate_btn"):
        if input_text.strip():
            summarized_text = summarize_text(input_text, types=selected)
            st.text_area("Generated Impressions:", summarized_text)
        else:
            st.error("Please enter some text to generate impressions.")

with tab2:
    # Section for CSV file upload
    st.header("Upload CSV File")
    csv_file = st.file_uploader("Choose a CSV file", type="csv")

    if csv_file:
        # Read CSV file
        df = pd.read_csv(csv_file)
        table_placeholder = st.empty()
        # Add columns for status and results if they do not exist
        if 'Status' not in df.columns:
            df['Status'] = 'Pending'
        if 'Result' not in df.columns:
            df['Result'] = ' '

        # Option to select a column from the CSV
        column_name = st.selectbox("Select the column to process", df.columns)

        # Define the maximum length for the Result column
        # MAX_RESULT_LENGTH = 10

        # Adjust the DataFrame display by truncating long results
        # Display the uploaded CSV file with status and results
        table_placeholder.write("CSV File Preview:")
        table_placeholder.dataframe(df, use_container_width=True)  # Use container width to fit the page width

        # Placeholder for displaying updates
        status_placeholder = st.empty()
        result_placeholder = st.empty()
        progress_bar = st.progress(0)

        # Button to process the CSV file
        if st.button("Process CSV File"):
            if column_name:
                total_rows = len(df)
                processed_rows = 0

                with st.spinner("Processing rows..."):
                    for index, row in df.iterrows():
                        if df.at[index, 'Status'] == 'Pending':  # Process only pending rows
                            data = row[column_name]
                            types = row["type"]
                            df.at[index, 'Status'] = 'Processing'

                            # Display the updated DataFrame
                            status_placeholder.write("Updating row status...")
                            result_placeholder.write(f"Processing row: {index + 1}")

                            # Simulate some processing time
                            time.sleep(1)  # Adjust as needed for actual processing time

                            result = summarize_text(data,types)
                            df.at[index, 'Result'] = result
                            df.at[index, 'Status'] = 'Completed'

                            # Truncate the Result column for better display
                            # df['Result'] = df['Result'].apply(lambda x: x[:MAX_RESULT_LENGTH] + '...' if len(x) > MAX_RESULT_LENGTH else x)

                            # Update the progress bar
                            processed_rows += 1
                            progress = processed_rows / total_rows
                            progress_bar.progress(progress)

                            # Clear and display the updated DataFrame
                            # table_placeholder.empty()
                            # table_placeholder.write("Updated CSV File:")
                            table_placeholder.dataframe(df, use_container_width=True)

                # Final update to DataFrame
                # st.write("Processed Results:")
                # st.dataframe(df, use_container_width=True)
            else:
                st.error("Please select a column to process.")
