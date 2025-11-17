import streamlit as st
import pdfplumber
import pandas as pd
import io
from datetime import datetime
import re

st.set_page_config(page_title="Bank Statement to Excel", page_icon="🏦", layout="centered")

st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; }
    h1 { color: white; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

def is_valid_date(text):
    """Check if text is a date like '31 Aug 2024'"""
    if not text:
        return False
    pattern = r'^\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}$'
    return bool(re.match(pattern, str(text).strip()))

def parse_date(date_str):
    """Parse date for sorting"""
    try:
        return datetime.strptime(str(date_str).strip(), '%d %b %Y')
    except:
        return datetime.min

def read_pdf_statement(pdf_file):
    """Read PDF and extract all transaction rows"""
    transactions = []
    
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            # Extract table from page
            table = page.extract_table()
            
            if not table:
                continue
            
            for row in table:
                if not row or len(row) < 6:
                    continue
                
                # Get first column
                col0 = str(row[0]).strip() if row[0] else ''
                
                # Only process if first column is a valid date
                if is_valid_date(col0):
                    # Extract all 6 columns as-is
                    date = col0
                    transaction_type = str(row[1]).strip() if row[1] else ''
                    details = str(row[2]).strip() if row[2] else ''
                    paid_in = str(row[3]).strip() if row[3] else ''
                    paid_out = str(row[4]).strip() if row[4] else ''
                    balance = str(row[5]).strip() if row[5] else ''
                    
                    # Add transaction
                    transactions.append({
                        'Date': date,
                        'Transaction type': transaction_type,
                        'Details': details,
                        'Paid in (£)': paid_in,
                        'Paid out (£)': paid_out,
                        'Balance (£)': balance,
                        '_sort': parse_date(date)
                    })
    
    # Sort by date (oldest first)
    transactions.sort(key=lambda x: x['_sort'])
    
    # Remove sort helper
    for t in transactions:
        del t['_sort']
    
    return transactions

# UI
st.markdown("<h1>🏦 Bank Statement to Excel</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📄 Upload PDF", type=['pdf'])

if uploaded_file:
    st.success(f"✅ {uploaded_file.name}")
    
    if st.button("📊 Extract to Excel", type="primary", use_container_width=True):
        with st.spinner('Reading PDF...'):
            try:
                # Extract transactions
                transactions = read_pdf_statement(uploaded_file)
                
                if not transactions:
                    st.error("❌ No transactions found")
                else:
                    # Create DataFrame
                    df = pd.DataFrame(transactions)
                    
                    # Create Excel file
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Transactions')
                        
                        ws = writer.sheets['Transactions']
                        ws.column_dimensions['A'].width = 15  # Date
                        ws.column_dimensions['B'].width = 20  # Transaction type
                        ws.column_dimensions['C'].width = 70  # Details
                        ws.column_dimensions['D'].width = 15  # Paid in
                        ws.column_dimensions['E'].width = 15  # Paid out
                        ws.column_dimensions['F'].width = 15  # Balance
                    
                    excel_data = output.getvalue()
                    
                    st.success(f'✅ Extracted {len(transactions)} transactions')
                    
                    # Download button
                    st.download_button(
                        label="⬇️ Download Excel",
                        data=excel_data,
                        file_name="transactions.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                        use_container_width=True
                    )
                    
                    # Preview
                    st.subheader("📋 Preview (first 30 rows)")
                    st.dataframe(df.head(30), use_container_width=True)
                    
                    st.metric("📊 Total Transactions", len(transactions))
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

st.markdown("---")
st.markdown("""
### 📝 Columns Extracted:
- Date
- Transaction type
- Details
- Paid in (£)
- Paid out (£)
- Balance (£)
""")
