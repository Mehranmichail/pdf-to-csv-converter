import streamlit as st
import pdfplumber
import pandas as pd
import csv
import io
import re
from typing import List, Tuple

# Page configuration
st.set_page_config(
    page_title="PDF to CSV Converter",
    page_icon="📄",
    layout="centered"
)

# Custom CSS for professional look
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    .stApp {
        max-width: 900px;
        margin: 0 auto;
    }
    h1 {
        color: white;
        text-align: center;
        font-size: 3rem;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .subtitle {
        color: rgba(255,255,255,0.95);
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

def clean_cell(cell):
    """Clean individual cell content."""
    if cell is None:
        return ''
    text = str(cell).strip()
    text = ' '.join(text.split())
    return text

def extract_all_data(pdf_file):
    """Extract ALL data from PDF including headers."""
    all_rows = []
    
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            
            for table in tables:
                if not table:
                    continue
                
                for row in table:
                    if not row:
                        continue
                    
                    # Clean the row but keep everything
                    clean_row = [clean_cell(cell) for cell in row]
                    
                    # Only skip completely empty rows
                    if any(clean_row):
                        all_rows.append(clean_row)
    
    return all_rows

def extract_to_standard_format(rows):
    """Convert rows to standard 6-column format."""
    formatted_rows = []
    
    for row in rows:
        # Ensure we have at least 7 columns
        while len(row) < 7:
            row.append('')
        
        # Extract based on actual column positions
        # Col 0: Date
        # Col 1: Transaction type
        # Col 2: Details
        # Col 3: Empty/None
        # Col 4: Paid in (£)
        # Col 5: Paid out (£)
        # Col 6: Balance (£)
        
        formatted_row = [
            row[0],  # Date
            row[1],  # Transaction type
            row[2],  # Details
            row[4] if len(row) > 4 else '',  # Paid in
            row[5] if len(row) > 5 else '',  # Paid out
            row[6] if len(row) > 6 else ''   # Balance
        ]
        
        formatted_rows.append(formatted_row)
    
    return formatted_rows

# Header
st.markdown("<h1>📄 PDF to CSV Converter</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Transform your bank statements into clean, ready-to-use spreadsheets</p>", unsafe_allow_html=True)

# Main container
with st.container():
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a bank statement or transaction PDF"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        extraction_mode = st.selectbox(
            "📊 Extraction Mode",
            options=['All Data (with headers)', 'Clean Data (no headers)'],
            index=0
        )
    
    with col2:
        output_format = st.selectbox(
            "📁 Output Format",
            options=['CSV', 'Excel'],
            index=0
        )
    
    if extraction_mode == 'All Data (with headers)':
        st.info("📋 **All Data Mode:** Extracts everything including headers and footers - you can clean it manually later")
    else:
        st.info("🧠 **Clean Mode:** Removes headers and junk - gives you only transaction data")
    
    if uploaded_file is not None:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🚀 Convert Now", type="primary", use_container_width=True):
                try:
                    with st.spinner('⚡ Converting your PDF...'):
                        # Extract all rows
                        all_rows = extract_all_data(uploaded_file)
                        
                        # Format to standard 6 columns
                        formatted_rows = extract_to_standard_format(all_rows)
                        
                        # Create header
                        header = ['Date', 'Transaction Type', 'Details', 'Paid In', 'Paid Out', 'Balance']
                        
                        if extraction_mode == 'Clean Data (no headers)':
                            # Filter out junk rows
                            clean_rows = []
                            for row in formatted_rows:
                                row_text = ' '.join(str(cell).lower() for cell in row).strip()
                                
                                # Skip junk
                                junk_keywords = [
                                    'page', 'business owner', 'account number', 'sort code', 
                                    'statement for', 'total paid', 'transactions', 'date',
                                    'bank account legal', 'clearbank', 'tide', 'fscs',
                                    'balance (£) on', 'transaction type', 'paid in', 'paid out'
                                ]
                                
                                if not any(keyword in row_text for keyword in junk_keywords):
                                    if any(row):  # Not empty
                                        clean_rows.append(row)
                            
                            final_rows = clean_rows
                        else:
                            final_rows = formatted_rows
                        
                        if output_format == 'Excel':
                            df = pd.DataFrame(final_rows, columns=header)
                            
                            # Clean amounts
                            for col in df.columns:
                                if 'paid' in col.lower() or 'balance' in col.lower():
                                    df[col] = df[col].str.replace(',', '')
                            
                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                df.to_excel(writer, index=False, sheet_name='Transactions')
                                
                                worksheet = writer.sheets['Transactions']
                                for idx, col in enumerate(df.columns):
                                    max_length = max(df[col].astype(str).apply(len).max(), len(col))
                                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
                            
                            excel_data = output.getvalue()
                            
                            st.success('✅ Conversion complete!')
                            
                            st.download_button(
                                label="⬇️ Download Excel",
                                data=excel_data,
                                file_name=f"{uploaded_file.name.replace('.pdf', '')}_transactions.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                type="primary",
                                use_container_width=True
                            )
                            
                            st.subheader("📋 Preview")
                            df_preview = df.head(10)
                            st.dataframe(df_preview, use_container_width=True)
                            
                            st.metric("📊 Total Rows", len(df))
                        
                        else:  # CSV
                            output = io.StringIO()
                            writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
                            writer.writerow(header)
                            writer.writerows(final_rows)
                            csv_content = output.getvalue()
                            
                            st.success('✅ Conversion complete!')
                            
                            st.download_button(
                                label="⬇️ Download CSV",
                                data=csv_content,
                                file_name=f"{uploaded_file.name.replace('.pdf', '')}_transactions.csv",
                                mime="text/csv",
                                type="primary",
                                use_container_width=True
                            )
                            
                            st.subheader("📋 Preview (First 10 rows)")
                            preview_lines = csv_content.split('\n')[:11]
                            st.text('\n'.join(preview_lines))
                            
                            row_count = len(csv_content.split('\n')) - 1
                            st.metric("📊 Total Rows", row_count)
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💡 Please check if your PDF is valid")

# Features section
st.markdown("---")
st.markdown("### ✨ Key Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **🎯 Accurate Extraction**
    - Reads actual PDF columns
    - Correct Paid In/Out
    - No calculation errors
    """)

with col2:
    st.markdown("""
    **⚡ Fast & Easy**
    - Upload PDF
    - Choose mode
    - Download instantly
    """)

with col3:
    st.markdown("""
    **📊 Multiple Formats**
    - CSV export
    - Excel export
    - Clean data ready to use
    """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: rgba(255,255,255,0.8); font-size: 0.9rem;'>"
    "Built with ❤️ using Streamlit • Powered by pdfplumber"
    "</p>",
    unsafe_allow_html=True
)
