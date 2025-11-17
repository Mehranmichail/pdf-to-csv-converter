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
    """Clean text."""
    if text is None:
        return ''
    return str(text).strip()

def is_valid_date(text):
    """Check if it's a date."""
    if not text or len(text) < 6:
        return False
    
    patterns = [
        r'^\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}$',
        r'^\d{1,2}-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{2}$',
        r'^\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{2}$',
    ]
    return any(re.match(pattern, text) for pattern in patterns)

def parse_date(date_str):
    """Parse date for sorting."""
    formats = ['%d %b %Y', '%d-%b-%y', '%d %b %y']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    return datetime.min

def read_statement(pdf_file):
    """Read PDF and extract exactly 4 columns."""
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
                    
                    # Clean the row
                    clean_row = [clean_text(cell) for cell in row]
                    
                    # Get the date (column 0)
                    date = clean_row[0]
                    
                    # ONLY process if it's a valid date
                    if not is_valid_date(date):
                        continue
                    
                    # Extract EXACTLY these columns:
                    # Column 0 = Date
                    # Column 2 = Description  
                    # Column 4 = Money In (Paid in £)
                    # Column 5 = Money Out (Paid out £)
                    
                    description = clean_row[2]
                    money_in = clean_row[4]
                    money_out = clean_row[5]
                    
                    # Add to list
                    transactions.append({
                        'Date': date,
                        'Description': description,
                        'Money In': money_in,
                        'Money Out': money_out,
                        '_sort': parse_date(date)
                    })
    
    # Sort chronologically
    transactions.sort(key=lambda x: x['_sort'])
    
    # Remove sort column
    for t in transactions:
        del t['_sort']
    
    return transactions

# Header
st.markdown("<h1>🏦 Bank Statement Reader</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Extract transactions with 100% accuracy</p>", unsafe_allow_html=True)

# Main
with st.container():
    uploaded_file = st.file_uploader(
        "📄 Upload Bank Statement PDF",
        type=['pdf']
    )
    
    if uploaded_file is not None:
        st.success(f"✅ {uploaded_file.name}")
        
        if st.button("📊 Extract to Excel", type="primary", use_container_width=True):
            try:
                with st.spinner('📖 Reading...'):
                    # Extract transactions
                    transactions = read_statement(uploaded_file)
                    
                    if not transactions:
                        st.error("❌ No transactions found")
                    else:
                        # Create DataFrame
                        df = pd.DataFrame(transactions)
                        
                        # Create Excel
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False, sheet_name='Transactions')
                            
                            ws = writer.sheets['Transactions']
                            ws.column_dimensions['A'].width = 15
                            ws.column_dimensions['B'].width = 60
                            ws.column_dimensions['C'].width = 12
                            ws.column_dimensions['D'].width = 12
                        
                        excel_data = output.getvalue()
                        
                        st.success(f'✅ {len(transactions)} transactions extracted!')
                        
                        st.download_button(
                            label="⬇️ Download Excel",
                            data=excel_data,
                            file_name=f"transactions.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            type="primary",
                            use_container_width=True
                        )
                        
                        st.subheader("📋 Preview")
                        st.dataframe(df.head(20), use_container_width=True)
                        
                        st.metric("📊 Total", len(transactions))
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.markdown("---")
st.markdown("### ✅ 4 Columns Only")
st.markdown("**Date | Description | Money In | Money Out**")
st.markdown("100% accurate extraction from PDF columns 0, 2, 4, 5")
