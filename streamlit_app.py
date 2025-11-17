import streamlit as st
import pdfplumber
import pandas as pd
import io
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Bank Statement to Excel",
    page_icon="🏦",
    layout="centered"
)

# Custom CSS
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
    </style>
    """, unsafe_allow_html=True)

def clean_text(text):
    """Clean text content."""
    if text is None:
        return ''
    return str(text).strip()

def parse_date(date_str):
    """Parse date for sorting."""
    try:
        # Try format: 29 Apr 2025
        return datetime.strptime(date_str, '%d %b %Y')
    except:
        try:
            # Try format: 29-Apr-25
            return datetime.strptime(date_str, '%d-%b-%y')
        except:
            return datetime.min

def read_bank_statement(pdf_file):
    """Read bank statement and extract transactions."""
    transactions = []
    
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            
            for table in tables:
                if not table:
                    continue
                
                for row in table:
                    if not row or len(row) < 7:
                        continue
                    
                    # Clean all cells
                    clean_row = [clean_text(cell) for cell in row]
                    
                    # Skip empty rows
                    if not any(clean_row):
                        continue
                    
                    # Skip header/junk rows
                    row_text = ' '.join(clean_row).lower()
                    junk_keywords = [
                        'business owner', 'account number', 'sort code', 
                        'statement for', 'total paid', 'transactions',
                        'page', 'date', 'transaction type', 'paid in', 'paid out',
                        'balance (£)', 'clearbank', 'tide'
                    ]
                    
                    if any(keyword in row_text for keyword in junk_keywords):
                        continue
                    
                    # Extract transaction data
                    # Row structure: [Date, Type, Details, None, Paid In, Paid Out, Balance]
                    date = clean_row[0]
                    trans_type = clean_row[1]
                    details = clean_row[2]
                    money_in = clean_row[4] if len(clean_row) > 4 else ''
                    money_out = clean_row[5] if len(clean_row) > 5 else ''
                    balance = clean_row[6] if len(clean_row) > 6 else ''
                    
                    # Only add if we have a date
                    if date and len(date) > 5:
                        # Combine type and details for full description
                        description = f"{trans_type} - {details}".strip(' -')
                        
                        transactions.append({
                            'Date': date,
                            'Description': description,
                            'Money In': money_in,
                            'Money Out': money_out,
                            'Balance': balance,
                            '_sort_date': parse_date(date)
                        })
    
    # Sort by date (chronological order)
    transactions.sort(key=lambda x: x['_sort_date'])
    
    # Remove the sort helper column
    for t in transactions:
        del t['_sort_date']
    
    return transactions

# Header
st.markdown("<h1>🏦 Bank Statement Reader</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Convert your bank statement PDF into a clean Excel spreadsheet</p>", unsafe_allow_html=True)

# Main container
with st.container():
    uploaded_file = st.file_uploader(
        "📄 Upload your bank statement (PDF)",
        type=['pdf'],
        help="Upload your bank statement PDF file"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("📊 Read & Convert to Excel", type="primary", use_container_width=True):
                try:
                    with st.spinner('📖 Reading your bank statement...'):
                        # Read transactions
                        transactions = read_bank_statement(uploaded_file)
                        
                        if not transactions:
                            st.error("❌ No transactions found in the PDF")
                        else:
                            # Create DataFrame
                            df = pd.DataFrame(transactions)
                            
                            # Create Excel file
                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                df.to_excel(writer, index=False, sheet_name='Transactions')
                                
                                # Auto-adjust column widths
                                worksheet = writer.sheets['Transactions']
                                for idx, col in enumerate(df.columns):
                                    max_length = max(
                                        df[col].astype(str).apply(len).max(),
                                        len(col)
                                    ) + 2
                                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 60)
                            
                            excel_data = output.getvalue()
                            
                            st.success('✅ Conversion complete!')
                            
                            # Download button
                            st.download_button(
                                label="⬇️ Download Excel File",
                                data=excel_data,
                                file_name=f"{uploaded_file.name.replace('.pdf', '')}_transactions.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                type="primary",
                                use_container_width=True
                            )
                            
                            # Preview
                            st.subheader("📋 Preview (First 10 transactions)")
                            st.dataframe(df.head(10), use_container_width=True)
                            
                            # Stats
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("📊 Total Transactions", len(transactions))
                            with col2:
                                date_range = f"{df['Date'].iloc[0]} to {df['Date'].iloc[-1]}"
                                st.info(f"📅 Date Range: {date_range}")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💡 Please check if your PDF is a valid bank statement")

# Info section
st.markdown("---")
st.markdown("### 📌 How it works")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **1️⃣ Upload**
    - Upload your bank statement PDF
    - Supports most UK bank formats
    """)

with col2:
    st.markdown("""
    **2️⃣ Process**
    - Reads all transactions
    - Sorts chronologically
    - Organizes data
    """)

with col3:
    st.markdown("""
    **3️⃣ Download**
    - Get Excel file
    - Ready to use
    - Clean & organized
    """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: rgba(255,255,255,0.8); font-size: 0.9rem;'>"
    "🏦 Bank Statement Reader • Built with Streamlit"
    "</p>",
    unsafe_allow_html=True
)
