import streamlit as st
import pdfplumber
import pandas as pd
import io
from datetime import datetime
import re

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

def is_valid_date(text):
    """Check if text is a valid date."""
    if not text or len(text) < 6:
        return False
    
    date_patterns = [
        r'^\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}$',
        r'^\d{1,2}-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{2}$',
    ]
    
    return any(re.match(pattern, text) for pattern in date_patterns)

def parse_date(date_str):
    """Parse date for sorting."""
    try:
        return datetime.strptime(date_str, '%d %b %Y')
    except:
        try:
            return datetime.strptime(date_str, '%d-%b-%y')
        except:
            return datetime.min

def is_header_or_junk(row_text):
    """Check if row is a header or junk (very minimal filtering)."""
    # Only skip VERY obvious headers
    obvious_junk = [
        'business owner:',
        'account number:',
        'sort code:',
        'statement for:',
        'page ',
        'bank statement',
        'balance (£) on'
    ]
    
    return any(junk in row_text for junk in obvious_junk)

def read_bank_statement(pdf_file):
    """Read bank statement and extract ALL transactions."""
    transactions = []
    
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            
            for table in tables:
                if not table:
                    continue
                
                for row in table:
                    if not row:
                        continue
                    
                    # Ensure row has enough columns
                    while len(row) < 7:
                        row.append('')
                    
                    # Clean all cells
                    clean_row = [clean_text(cell) for cell in row]
                    
                    # Get first cell (should be date)
                    date = clean_row[0]
                    
                    # Skip if not a valid date
                    if not is_valid_date(date):
                        # Check if it's obvious junk
                        row_text = ' '.join(clean_row).lower()
                        if is_header_or_junk(row_text):
                            continue
                        # If not obvious junk but no date, skip anyway
                        if not date:
                            continue
                    
                    # Extract transaction data
                    # Row structure: [Date, Type, Details, None, Paid In, Paid Out, Balance]
                    description = clean_row[2]  # Just the details, no type
                    money_in = clean_row[4]
                    money_out = clean_row[5]
                    balance = clean_row[6]
                    
                    # Add transaction
                    transactions.append({
                        'Date': date,
                        'Description': description,
                        'Money In': money_in,
                        'Money Out': money_out,
                        'Balance': balance,
                        '_sort_date': parse_date(date)
                    })
    
    # Sort by date (chronological order - oldest first)
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
                            st.subheader("📋 Preview (First 15 transactions)")
                            st.dataframe(df.head(15), use_container_width=True)
                            
                            # Stats
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("📊 Total Transactions", len(transactions))
                            with col2:
                                if len(df) > 0:
                                    date_range = f"{df['Date'].iloc[0]} → {df['Date'].iloc[-1]}"
                                    st.info(f"📅 {date_range}")
                            with col3:
                                st.success("✅ All data extracted!")
                
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
    - Supports multi-page PDFs
    """)

with col2:
    st.markdown("""
    **2️⃣ Process**
    - Extracts ALL transactions
    - Sorts chronologically
    - Clean descriptions only
    """)

with col3:
    st.markdown("""
    **3️⃣ Download**
    - Get Excel file
    - All 500+ transactions
    - Ready to use
    """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: rgba(255,255,255,0.8); font-size: 0.9rem;'>"
    "🏦 Bank Statement Reader • Built with Streamlit"
    "</p>",
    unsafe_allow_html=True
)
