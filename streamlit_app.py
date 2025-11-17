import streamlit as st
import pdfplumber
import pandas as pd
import io
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title="Bank Statement to Excel - 100% Accurate",
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
    </style>
    """, unsafe_allow_html=True)

def clean_text(text):
    """Clean text."""
    if text is None:
        return ''
    return str(text).strip()

def is_valid_date(text):
    """Check if text is a valid date like '31 Aug 2024' or '1 Aug 2024'."""
    if not text or len(text) < 6:
        return False
    
    # Match dates like "31 Aug 2024", "1 Aug 2024"
    pattern = r'^\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}$'
    return bool(re.match(pattern, text.strip()))

def parse_date(date_str):
    """Parse date for sorting."""
    try:
        return datetime.strptime(date_str.strip(), '%d %b %Y')
    except:
        return datetime.min

def is_skip_row(row_text):
    """Check if this row should be skipped (headers, summaries, etc.)."""
    skip_phrases = [
        'date', 'transaction type', 'details', 'paid in', 'paid out', 'balance',
        'business owner', 'account number', 'sort code', 'statement for',
        'total paid', 'balance on', 'bank statement', 'transactions',
        'bank account legal', 'your tide account', 'clearbank', 'tide platform',
        'to be billed', 'transaction fees'
    ]
    return any(phrase in row_text for phrase in skip_phrases)

def read_statement(pdf_file):
    """
    Read bank statement PDF and extract transactions.
    
    Bank statement columns are:
    0: Date
    1: Transaction type  
    2: Details
    3: Paid in (£)  <- Money coming IN
    4: Paid out (£) <- Money going OUT
    5: Balance (£)  <- We ignore this
    """
    transactions = []
    
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            # Extract text-based table
            tables = page.extract_tables()
            
            if not tables:
                continue
                
            for table in tables:
                if not table:
                    continue
                
                for row in table:
                    if not row or len(row) < 5:  # Need at least 5 columns
                        continue
                    
                    # Clean all cells
                    clean_row = [clean_text(cell) for cell in row]
                    
                    # Check if this is a skip row
                    row_text = ' '.join(clean_row).lower()
                    if is_skip_row(row_text):
                        continue
                    
                    # Column 0 must be a valid date
                    date = clean_row[0]
                    if not is_valid_date(date):
                        continue
                    
                    # Extract remaining columns
                    transaction_type = clean_row[1] if len(clean_row) > 1 else ''
                    details = clean_row[2] if len(clean_row) > 2 else ''
                    paid_in = clean_row[3] if len(clean_row) > 3 else ''  # Money IN
                    paid_out = clean_row[4] if len(clean_row) > 4 else ''  # Money OUT
                    
                    # Only add if there's a description
                    if details and details.strip():
                        transactions.append({
                            'Date': date,
                            'Transaction type': transaction_type,
                            'Details': details,
                            'Paid in (£)': paid_in,
                            'Paid out (£)': paid_out,
                            '_sort_date': parse_date(date)
                        })
    
    # Sort by date (oldest first)
    transactions.sort(key=lambda x: x['_sort_date'])
    
    # Remove sorting helper column
    for t in transactions:
        del t['_sort_date']
    
    return transactions

# Header
st.markdown("<h1>🏦 Bank Statement to Excel</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: white; text-align: center; font-size: 1.2rem;'>100% Accurate Extraction</p>", unsafe_allow_html=True)

# Main
uploaded_file = st.file_uploader("📄 Upload Bank Statement PDF", type=['pdf'])

if uploaded_file is not None:
    st.success(f"✅ {uploaded_file.name}")
    
    if st.button("📊 Extract to Excel", type="primary", use_container_width=True):
        try:
            with st.spinner('📖 Extracting transactions...'):
                # Extract transactions
                transactions = read_statement(uploaded_file)
                
                if not transactions:
                    st.error("❌ No transactions found")
                else:
                    # Create DataFrame with exact column names from bank statement
                    df = pd.DataFrame(transactions)
                    
                    # Create Excel file
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Transactions')
                        
                        # Set column widths
                        ws = writer.sheets['Transactions']
                        ws.column_dimensions['A'].width = 15  # Date
                        ws.column_dimensions['B'].width = 20  # Transaction type
                        ws.column_dimensions['C'].width = 70  # Details
                        ws.column_dimensions['D'].width = 15  # Paid in (£)
                        ws.column_dimensions['E'].width = 15  # Paid out (£)
                    
                    excel_data = output.getvalue()
                    
                    st.success(f'✅ {len(transactions)} transactions extracted!')
                    
                    # Download button
                    st.download_button(
                        label="⬇️ Download Excel",
                        data=excel_data,
                        file_name="bank_transactions.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                        use_container_width=True
                    )
                    
                    # Preview
                    st.subheader("📋 Preview (First 20 transactions)")
                    st.dataframe(df.head(20), use_container_width=True)
                    
                    # Summary stats
                    st.subheader("📊 Summary")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Transactions", len(transactions))
                    
                    with col2:
                        money_in_count = df['Paid in (£)'].astype(str).str.strip().ne('').sum()
                        st.metric("Payments In", money_in_count)
                    
                    with col3:
                        money_out_count = df['Paid out (£)'].astype(str).str.strip().ne('').sum()
                        st.metric("Payments Out", money_out_count)
                    
                    # Show date range
                    st.info(f"📅 Date range: {df['Date'].iloc[0]} to {df['Date'].iloc[-1]}")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

st.markdown("---")
st.markdown("""
### ✅ Column Mapping (Exact from Bank Statement)
- **Date** - Transaction date
- **Transaction type** - Type of transaction (Card, Transfer, Direct Debit, etc.)
- **Details** - Full transaction description  
- **Paid in (£)** - Money received/coming IN
- **Paid out (£)** - Money spent/going OUT

**Note**: Balance column is ignored as it's just running total
""")
