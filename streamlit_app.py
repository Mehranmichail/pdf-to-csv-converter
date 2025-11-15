import streamlit as st
import pdfplumber
import pandas as pd
import csv
import io
import re
from typing import List, Tuple
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="PDF to CSV Converter",
    page_icon="📄",
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
        max-width: 800px;
        margin: 0 auto;
    }
    h1 {
        color: white;
        text-align: center;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: rgba(255,255,255,0.9);
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

class FinalSmartPDFConverter:
    """Smart PDF converter that sorts by DATE and calculates Paid In/Out from balance changes."""
    
    def parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime for sorting."""
        if not date_str:
            return datetime.min
        
        date_str = str(date_str).strip()
        
        # Try different date formats
        formats = [
            '%d-%b-%y',      # 29-Apr-25
            '%d %b %Y',      # 29 Apr 2025
            '%d/%m/%Y',      # 29/04/2025
            '%d/%m/%y',      # 29/04/25
            '%Y-%m-%d',      # 2025-04-29
            '%d-%m-%Y',      # 29-04-2025
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        return datetime.min
    
    def is_date(self, text: str) -> bool:
        """Check if text looks like a date."""
        if not text or not str(text).strip():
            return False
        
        text = str(text).strip()
        
        date_patterns = [
            r'^\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}$',
            r'^\d{1,2}/\d{1,2}/\d{2,4}$',
            r'^\d{4}-\d{2}-\d{2}$',
            r'^\d{1,2}-\d{1,2}-\d{2,4}$',
            r'^\d{1,2}-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{2}$',
        ]
        
        return any(re.match(pattern, text) for pattern in date_patterns)
    
    def has_amount(self, text: str) -> bool:
        """Check if text looks like a monetary amount."""
        if not text:
            return False
        text = str(text).strip()
        return bool(re.match(r'^[\d,]+\.?\d{0,2}$', text))
    
    def clean_amount(self, text: str) -> float:
        """Convert amount string to float."""
        if not text or not str(text).strip():
            return 0.0
        try:
            return float(str(text).replace(',', ''))
        except:
            return 0.0
    
    def is_transaction_row(self, row: List[str]) -> bool:
        """Determine if a row is a transaction."""
        if not row or len(row) < 3:
            return False
        
        clean_row = [cell for cell in row if cell and str(cell).strip()]
        
        if len(clean_row) < 3:
            return False
        
        if not self.is_date(clean_row[0]):
            return False
        
        has_money = any(self.has_amount(cell) for cell in clean_row[2:])
        
        return has_money
    
    def is_junk_row(self, row: List[str]) -> bool:
        """Determine if a row is junk."""
        if not row:
            return True
        
        row_text = ' '.join(str(cell).lower() for cell in row if cell).strip()
        
        if not row_text or len(row_text) < 5:
            return True
        
        junk_keywords = [
            'page', 'business owner', 'account number', 'sort code', 
            'statement for', 'total paid', 'transactions',
            'bank account legal', 'clearbank', 'tide', 'fscs',
            'to be billed', 'transaction fee', 'regulation',
            'your tide account', 'registered', 'authorised',
            'balance (£) on'
        ]
        
        return any(keyword in row_text for keyword in junk_keywords)
    
    def clean_cell(self, cell) -> str:
        """Clean individual cell content."""
        if cell is None:
            return ''
        text = str(cell).strip()
        text = ' '.join(text.split())
        return text
    
    def extract_transaction_data(self, row: List[str]) -> Tuple[str, str, str, str]:
        """Extract date, type, details, and balance from a row."""
        row = [self.clean_cell(cell) for cell in row]
        
        date = row[0] if len(row) > 0 else ''
        trans_type = row[1] if len(row) > 1 else ''
        details = row[2] if len(row) > 2 else ''
        
        # Find balance (last cell with an amount)
        balance = ''
        for i in range(len(row) - 1, 2, -1):
            if row[i] and self.has_amount(row[i]):
                balance = row[i]
                break
        
        return date, trans_type, details, balance
    
    def calculate_paid_in_out(self, transactions: List[Tuple[str, str, str, str]]) -> List[List[str]]:
        """Calculate Paid In/Out based on balance changes."""
        result = []
        prev_balance = None
        
        for date, trans_type, details, balance_str in transactions:
            balance = self.clean_amount(balance_str)
            
            paid_in = ''
            paid_out = ''
            
            if prev_balance is not None and balance_str:
                diff = balance - prev_balance
                
                if diff > 0:
                    # Balance increased = Money IN
                    paid_in = f"{diff:.2f}"
                elif diff < 0:
                    # Balance decreased = Money OUT
                    paid_out = f"{abs(diff):.2f}"
            
            result.append([date, trans_type, details, paid_in, paid_out, balance_str])
            
            if balance_str:
                prev_balance = balance
        
        return result
    
    def extract_smart_transactions(self, pdf_file) -> Tuple[List[str], List[List[str]]]:
        """Extract transactions and calculate Paid In/Out from balance changes."""
        raw_transactions = []
        header = ['Date', 'Transaction Type', 'Details', 'Paid In', 'Paid Out', 'Balance']
        
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                
                for table in tables:
                    if not table:
                        continue
                    
                    for row in table:
                        if not row:
                            continue
                        
                        clean_row = [self.clean_cell(cell) for cell in row]
                        
                        if self.is_junk_row(clean_row):
                            continue
                        
                        if self.is_transaction_row(clean_row):
                            date, trans_type, details, balance = self.extract_transaction_data(clean_row)
                            raw_transactions.append((date, trans_type, details, balance))
        
        # Sort by DATE (chronologically)
        raw_transactions.sort(key=lambda x: self.parse_date(x[0]))
        
        # Calculate Paid In/Out
        final_transactions = self.calculate_paid_in_out(raw_transactions)
        
        return header, final_transactions
    
    def convert_to_csv(self, pdf_file) -> str:
        """Convert PDF to clean CSV."""
        header, transactions = self.extract_smart_transactions(pdf_file)
        
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        writer.writerows(transactions)
        
        return output.getvalue()
    
    def convert_to_excel(self, pdf_file) -> bytes:
        """Convert PDF to clean Excel."""
        header, transactions = self.extract_smart_transactions(pdf_file)
        
        df = pd.DataFrame(transactions, columns=header)
        
        # Clean up amounts
        for col in df.columns:
            if 'paid' in col.lower() or 'balance' in col.lower():
                df[col] = df[col].str.replace(',', '')
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Transactions')
            
            worksheet = writer.sheets['Transactions']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
        return output.getvalue()

# Title and description
st.markdown("<h1>📄 PDF to CSV Converter</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Upload your PDF and get clean, ready-to-use data instantly</p>", unsafe_allow_html=True)

# Main container
with st.container():
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF file to convert (bank statements, invoices, etc.)"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        conversion_mode = st.selectbox(
            "Conversion Mode",
            options=['Smart (Transactions Only)', 'Standard (All Data)'],
            index=0,
            help="Smart mode extracts only transaction rows and removes junk"
        )
    
    with col2:
        output_format = st.selectbox(
            "Output Format",
            options=['CSV', 'Excel'],
            index=0,
            help="Choose your preferred output format"
        )
    
    if conversion_mode == 'Smart (Transactions Only)':
        st.info("🧠 **Smart Mode:** Sorts by date and calculates Paid In/Out from balance changes!")
    else:
        st.info("📋 **Standard Mode:** Extracts all tables and text from the PDF")
    
    if uploaded_file is not None:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🔄 Convert Now", type="primary", use_container_width=True):
                try:
                    with st.spinner('Converting your PDF...'):
                        converter = FinalSmartPDFConverter()
                        
                        if conversion_mode == 'Smart (Transactions Only)':
                            if output_format == 'Excel':
                                excel_data = converter.convert_to_excel(uploaded_file)
                                
                                st.success('✅ Conversion complete!')
                                
                                st.download_button(
                                    label="⬇️ Download Excel",
                                    data=excel_data,
                                    file_name=f"{uploaded_file.name.replace('.pdf', '')}_transactions.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    type="primary",
                                    use_container_width=True
                                )
                                
                                st.subheader("Preview")
                                header, transactions = converter.extract_smart_transactions(uploaded_file)
                                df_preview = pd.DataFrame(transactions[:10], columns=header)
                                st.dataframe(df_preview, use_container_width=True)
                                
                                st.metric("Total Transactions", len(transactions))
                                
                            else:  # CSV
                                csv_content = converter.convert_to_csv(uploaded_file)
                                
                                st.success('✅ Conversion complete!')
                                
                                st.download_button(
                                    label="⬇️ Download CSV",
                                    data=csv_content,
                                    file_name=f"{uploaded_file.name.replace('.pdf', '')}_transactions.csv",
                                    mime="text/csv",
                                    type="primary",
                                    use_container_width=True
                                )
                                
                                st.subheader("Preview (First 10 rows)")
                                preview_lines = csv_content.split('\n')[:11]
                                st.text('\n'.join(preview_lines))
                                
                                row_count = len(csv_content.split('\n')) - 1
                                st.metric("Total Transactions", row_count)
                        
                        else:  # Standard mode
                            all_rows = []
                            with pdfplumber.open(uploaded_file) as pdf:
                                for page in pdf.pages:
                                    tables = page.extract_tables()
                                    for table in tables:
                                        if table:
                                            all_rows.extend(table)
                            
                            if output_format == 'Excel':
                                df = pd.DataFrame(all_rows[1:], columns=all_rows[0] if all_rows else [])
                                output = io.BytesIO()
                                df.to_excel(output, index=False)
                                excel_data = output.getvalue()
                                
                                st.success('✅ Conversion complete!')
                                st.download_button(
                                    label="⬇️ Download Excel",
                                    data=excel_data,
                                    file_name=f"{uploaded_file.name.replace('.pdf', '')}_output.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    type="primary",
                                    use_container_width=True
                                )
                            else:
                                output = io.StringIO()
                                writer = csv.writer(output)
                                writer.writerows(all_rows)
                                csv_content = output.getvalue()
                                
                                st.success('✅ Conversion complete!')
                                st.download_button(
                                    label="⬇️ Download CSV",
                                    data=csv_content,
                                    file_name=f"{uploaded_file.name.replace('.pdf', '')}_output.csv",
                                    mime="text/csv",
                                    type="primary",
                                    use_container_width=True
                                )
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💡 Try switching to Standard mode or check if your PDF is valid")

# Features section
st.markdown("---")
st.markdown("### ✨ Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    - ✅ Smart date-based sorting
    - ✅ Auto-calculates Paid In/Out
    - ✅ Excel & CSV output
    - ✅ Ready-to-use data
    """)

with col2:
    st.markdown("""
    - ✅ Bank statement friendly
    - ✅ No manual cleanup needed
    - ✅ Perfect accuracy
    - ✅ Instant download
    """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: rgba(255,255,255,0.7); font-size: 0.9rem;'>"
    "Built with Streamlit • Smart extraction powered by pdfplumber"
    "</p>",
    unsafe_allow_html=True
)
