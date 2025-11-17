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

def is_junk_row(row_list):
    """Identify and skip junk rows completely."""
    row_text = ' '.join(row_list).lower()
    
    # Skip rows containing these phrases
    junk_phrases = [
        'business owner',
        'account number',
        'sort code',
        'statement for',
        'balance (£) on',
        'total paid in',
        'total paid out',
        'page ',
        'bank statement',
        'clearbank',
        'tide',
        'fscs',
        'registered',
        'authorised',
        'transaction type',  # This is a header
        'paid in (£)',       # This is a header
        'paid out (£)',      # This is a header
        'details',           # This is a header
        'date\t'             # Tab-separated header
    ]
    
    # If any junk phrase is found, skip
    if any(phrase in row_text for phrase in junk_phrases):
        return True
    
    # If row has "date" and "transaction" and "balance" together = header row
    if 'date' in row_text and 'transaction' in row_text and 'balance' in row_text:
        return True
    
    return False

def read_bank_statement(pdf_file):
    """Read bank statement and extract ONLY transactions."""
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
                    
                    # Skip junk rows FIRST
                    if is_junk_row(clean_row):
                        continue
                    
                    # Get date (first column)
                    date = clean_row[0]
                    
                    # Skip if not a valid date
                    if not is_valid_date(date):
                        continue
                    
                    # Extract transaction data
                    # Row structure: [Date, Type, Details, None, Paid In, Paid Out, Balance]
                    description = clean_row[2]  # Just the transaction details
                    money_in = clean_row[4]
                    money_out = clean_row[5]
                    balance = clean_row[6]
                    
                    # Only add if description is not empty
                    if description:
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
                            # Create DataFrame with ONLY ONE header
                            df = pd.DataFrame(transactions)
                            
                            # Create Excel file
                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                # Write with header=True (default) - this creates ONE header row
                                df.to_excel(writer, index=False, sheet_name='Transactions')
                                
                                # Auto-adjust column widths
                                worksheet = writer.sheets['Transactions']
                                
                                # Set column widths
                                worksheet.column_dimensions['A'].width = 15  # Date
                                worksheet.column_dimensions['B'].width = 50  # Description
                                worksheet.column_dimensions['C'].width = 12  # Money In
                                worksheet.column_dimensions['D'].width = 12  # Money Out
                                worksheet.column_dimensions['E'].width = 15  # Balance
                            
                            excel_data = output.getvalue()
                            
                            st.success(f'✅ Extracted {len(transactions)} transactions!')
                            
                            # Download button
                            st.download_button(
                                label="⬇️ Download Excel File",
                                data=excel_data,
                                file_name=f"transactions_{uploaded_file.name.replace('.pdf', '')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                type="primary",
                                use_container_width=True
                            )
                            
                            # Preview
                            st.subheader("📋 Preview (First 15 transactions)")
                            st.dataframe(df.head(15), use_container_width=True)
                            
                            # Stats
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("📊 Total Transactions", len(transactions))
                            with col2:
                                if len(df) > 0:
                                    st.info(f"📅 {df['Date'].iloc[0]} → {df['Date'].iloc[-1]}")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.exception(e)

# Info section
st.markdown("---")
st.markdown("### ✅ What you get")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Clean Data**
    - ONE header row only
    - No duplicate headers
    - No junk rows
    """)

with col2:
    st.markdown("""
    **Complete Transactions**
    - All 500+ transactions
    - Chronological order
    - Clean descriptions
    """)

with col3:
    st.markdown("""
    **Ready to Use**
    - Excel format
    - Proper columns
    - Easy to analyze
    """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: rgba(255,255,255,0.8); font-size: 0.9rem;'>"
    "🏦 Bank Statement Reader • Built with Streamlit"
    "</p>",
    unsafe_allow_html=True
)
