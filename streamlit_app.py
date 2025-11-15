import streamlit as st
import pdfplumber
import pandas as pd
import io

st.title("PDF to CSV Converter")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    if st.button("Convert to CSV"):
        # Extract tables from PDF
        with pdfplumber.open(uploaded_file) as pdf:
            all_tables = []
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    all_tables.extend(table)
        
        # Convert to DataFrame
        if all_tables:
            df = pd.DataFrame(all_tables[1:], columns=all_tables[0])
            
            # Convert to CSV
            csv = df.to_csv(index=False)
            
            # Download button
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="output.csv",
                mime="text/csv"
            )
            
            # Preview
            st.write("Preview:")
            st.dataframe(df.head())
        else:
            st.error("No tables found in PDF")
