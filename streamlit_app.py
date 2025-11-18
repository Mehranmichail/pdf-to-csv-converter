import streamlit as st
import streamlit.components.v1 as components

# Set page config
st.set_page_config(page_title="Bank Statement Converter", page_icon="🏦", layout="wide")

# HTML content with categorization feature
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bank Statement PDF to Excel Converter</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }

        .header p {
            opacity: 0.9;
            font-size: 14px;
        }

        .content {
            padding: 40px;
        }

        .upload-section {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            background: #f8f9ff;
            transition: all 0.3s;
            cursor: pointer;
        }

        .upload-section:hover {
            border-color: #764ba2;
            background: #f0f1ff;
        }

        .upload-section.dragover {
            border-color: #4CAF50;
            background: #e8f5e9;
        }

        .upload-icon {
            font-size: 48px;
            margin-bottom: 20px;
        }

        .upload-section h3 {
            color: #667eea;
            margin-bottom: 10px;
        }

        .upload-section p {
            color: #666;
            margin-bottom: 20px;
        }

        input[type="file"] {
            display: none;
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
            font-weight: 600;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }

        .progress-section {
            display: none;
            margin-top: 30px;
        }

        .progress-bar-container {
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            height: 30px;
            margin-bottom: 15px;
        }

        .progress-bar {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            width: 0%;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 14px;
        }

        .status-message {
            text-align: center;
            color: #666;
            font-size: 14px;
        }

        .result-section {
            display: none;
            margin-top: 30px;
        }

        .result-header {
            background: #f0f8ff;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            margin-bottom: 20px;
        }

        .result-header h3 {
            color: #667eea;
            margin-bottom: 15px;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .stat-card {
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .stat-card .label {
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }

        .stat-card .value {
            font-size: 24px;
            font-weight: 700;
            color: #667eea;
        }

        .category-summary {
            margin-top: 30px;
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .category-summary h3 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 20px;
        }

        .category-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }

        .category-tab {
            padding: 10px 20px;
            cursor: pointer;
            border: none;
            background: none;
            font-size: 16px;
            font-weight: 600;
            color: #666;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }

        .category-tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }

        .category-content {
            display: none;
        }

        .category-content.active {
            display: block;
        }

        .category-item {
            display: flex;
            justify-content: space-between;
            padding: 12px;
            border-bottom: 1px solid #f0f0f0;
            transition: background 0.2s;
        }

        .category-item:hover {
            background: #f8f9ff;
        }

        .category-name {
            font-weight: 500;
            color: #333;
        }

        .category-amount {
            font-weight: 700;
            color: #667eea;
        }

        .category-amount.income {
            color: #4CAF50;
        }

        .category-amount.expense {
            color: #f44336;
        }

        .error-message {
            display: none;
            margin-top: 20px;
            padding: 15px;
            background: #ffebee;
            border-left: 4px solid #f44336;
            border-radius: 5px;
            color: #c62828;
        }

        .preview-table {
            margin-top: 20px;
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }

        th {
            background: #667eea;
            color: white;
            font-weight: 600;
        }

        tr:hover {
            background: #f5f5f5;
        }

        .download-btn {
            margin-top: 20px;
            width: 100%;
        }

        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
            background: #f8f9fa;
        }

        .chart-container {
            margin-top: 20px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏦 Bank Statement Converter</h1>
            <p>Convert your bank PDF statements to Excel with automatic categorization</p>
        </div>

        <div class="content">
            <div class="upload-section" id="uploadSection">
                <div class="upload-icon">📄</div>
                <h3>Drop your PDF file here</h3>
                <p>or click to browse</p>
                <input type="file" id="fileInput" accept=".pdf">
                <button class="btn" onclick="document.getElementById('fileInput').click()">
                    Select PDF File
                </button>
            </div>

            <div class="progress-section" id="progressSection">
                <div class="progress-bar-container">
                    <div class="progress-bar" id="progressBar">0%</div>
                </div>
                <div class="status-message" id="statusMessage">Processing...</div>
            </div>

            <div class="error-message" id="errorMessage"></div>

            <div class="result-section" id="resultSection">
                <div class="result-header">
                    <h3>✅ Conversion Successful!</h3>
                    
                    <div class="stats">
                        <div class="stat-card">
                            <div class="label">Total Transactions</div>
                            <div class="value" id="totalTransactions">0</div>
                        </div>
                        <div class="stat-card">
                            <div class="label">Total Paid In</div>
                            <div class="value" style="color: #4CAF50;" id="totalPaidIn">£0.00</div>
                        </div>
                        <div class="stat-card">
                            <div class="label">Total Paid Out</div>
                            <div class="value" style="color: #f44336;" id="totalPaidOut">£0.00</div>
                        </div>
                        <div class="stat-card">
                            <div class="label">Categories Found</div>
                            <div class="value" id="totalCategories">0</div>
                        </div>
                        <div class="stat-card">
                            <div class="label">Net Profit/Loss</div>
                            <div class="value" id="netProfit">£0.00</div>
                        </div>
                    </div>

                    <button class="btn download-btn" id="downloadBtn">
                        📥 Download Excel File with Categories
                    </button>
                    
                    <div style="margin-top: 20px; padding: 15px; background: #f8f9ff; border-radius: 10px; border-left: 4px solid #667eea;">
                        <h4 style="color: #667eea; margin-bottom: 10px;">📅 Financial Statement Period</h4>
                        <p style="font-size: 12px; color: #666; margin-bottom: 10px;">Specify the period for your financial statements:</p>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 10px;">
                            <div>
                                <label style="display: block; font-size: 12px; color: #666; margin-bottom: 5px;">From Date:</label>
                                <input type="date" id="startDate" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                            </div>
                            <div>
                                <label style="display: block; font-size: 12px; color: #666; margin-bottom: 5px;">To Date:</label>
                                <input type="date" id="endDate" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                            </div>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 15px;">
                        <button class="btn" id="downloadTrialBalanceBtn" style="padding: 10px 20px; font-size: 14px;">
                            📊 Download Trial Balance
                        </button>
                        <button class="btn" id="downloadPLBtn" style="padding: 10px 20px; font-size: 14px;">
                            💰 Download Profit & Loss
                        </button>
                        <button class="btn" id="downloadBalanceSheetBtn" style="padding: 10px 20px; font-size: 14px;">
                            📋 Download Balance Sheet
                        </button>
                    </div>
                </div>

                <div class="category-summary">
                    <h3>📊 Receipts & Payments by Category</h3>
                    
                    <div class="category-tabs">
                        <button class="category-tab active" onclick="switchTab('income')">Money In (Receipts)</button>
                        <button class="category-tab" onclick="switchTab('expenses')">Money Out (Payments)</button>
                    </div>

                    <div id="incomeCategories" class="category-content active"></div>
                    <div id="expenseCategories" class="category-content"></div>
                </div>

                <div class="category-summary">
                    <h3>📑 Financial Statements Preview</h3>
                    
                    <div class="category-tabs">
                        <button class="category-tab active" onclick="switchFinancialTab('trialbalance')">Trial Balance</button>
                        <button class="category-tab" onclick="switchFinancialTab('profitloss')">Profit & Loss</button>
                        <button class="category-tab" onclick="switchFinancialTab('balancesheet')">Balance Sheet</button>
                    </div>

                    <div id="trialBalancePreview" class="category-content active"></div>
                    <div id="profitLossPreview" class="category-content"></div>
                    <div id="balanceSheetPreview" class="category-content"></div>
                </div>

                <div class="preview-table">
                    <h4 style="margin-bottom: 10px; color: #667eea;">Transaction Preview (First 10 rows)</h4>
                    <table id="previewTable"></table>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>Supports bank statement PDFs | Data processed locally in your browser | Automatic categorization included</p>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <script>
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

        let extractedData = [];
        let categoryStats = {
            income: {},
            expenses: {}
        };

        // Categorization rules
        const categories = {
            income: {
                'Card Payments': ['sumup', 'paymentsense', 'evo payments', 'dojo', 'american express', 'worldpay', 'stripe', 'square', 'paypal'],
                'Bank Transfers': ['transfer', 'payment received', 'bacs'],
                'Refunds': ['refund', 'reimbursement'],
                'Other Income': []
            },
            expenses: {
                'Advertising & Marketing': ['google ads', 'facebook ads', 'meta', 'instagram', 'linkedin', 'twitter', 'tiktok', 'advertising', 'marketing', 'mailchimp', 'hubspot'],
                'Bank Fees & Charges': ['bank charge', 'bank fee', 'overdraft', 'interest charge', 'account fee', 'transaction fee'],
                'Office Supplies': ['amazon', 'staples', 'office depot', 'ryman', 'viking', 'supplies'],
                'Professional Services': ['accountant', 'solicitor', 'lawyer', 'consultant', 'hmrc', 'companies house'],
                'Software & Subscriptions': ['microsoft', 'adobe', 'dropbox', 'zoom', 'slack', 'canva', 'notion', 'asana', 'trello', 'xero', 'quickbooks', 'sage', 'shopify', 'wix', 'squarespace'],
                'Utilities & Communications': ['bt', 'vodafone', 'o2', 'ee', 'three', 'virgin', 'sky', 'talk talk', 'plusnet', 'telephone', 'internet', 'broadband', 'mobile'],
                'Travel & Transport': ['uber', 'trainline', 'national rail', 'tfl', 'transport for london', 'parking', 'petrol', 'fuel', 'shell', 'bp', 'esso', 'tesco fuel'],
                'Meals & Entertainment': ['restaurant', 'cafe', 'coffee', 'starbucks', 'costa', 'pret', 'food', 'lunch', 'dinner', 'deliveroo', 'uber eats', 'just eat'],
                'Rent & Property': ['rent', 'lease', 'property', 'landlord', 'commercial rent'],
                'Equipment & Technology': ['currys', 'pc world', 'apple', 'dell', 'hp', 'lenovo', 'equipment'],
                'Insurance': ['insurance', 'policy', 'premium'],
                'Payment Processing Fees': ['sumup fee', 'stripe fee', 'paypal fee', 'merchant fee', 'card fee'],
                'Cost of Goods Sold': ['supplier', 'wholesale', 'inventory', 'stock', 'manufacturer'],
                'Payroll & Staff': ['salary', 'wage', 'payroll', 'hmrc paye', 'pension'],
                'Taxes': ['vat', 'tax', 'hmrc', 'corporation tax', 'self assessment'],
                'General Business Expenses': []
            }
        };

        function categorizeTransaction(details, transType, paidIn, paidOut) {
            const detailsLower = details.toLowerCase();
            
            // Determine if it's income or expense
            const isIncome = paidIn !== '';
            const categoryGroup = isIncome ? categories.income : categories.expenses;
            
            // Search through categories
            for (const [categoryName, keywords] of Object.entries(categoryGroup)) {
                for (const keyword of keywords) {
                    if (detailsLower.includes(keyword)) {
                        return categoryName;
                    }
                }
            }
            
            // Default categories based on transaction type
            if (isIncome) {
                if (transType === 'Card Transaction Refund') return 'Refunds';
                if (transType === 'Domestic Transfer') return 'Bank Transfers';
                return 'Other Income';
            } else {
                if (transType === 'Direct Debit') return 'Utilities & Communications';
                if (transType === 'Fee') return 'Bank Fees & Charges';
                return 'General Business Expenses';
            }
        }

        const fileInput = document.getElementById('fileInput');
        const uploadSection = document.getElementById('uploadSection');
        const progressSection = document.getElementById('progressSection');
        const resultSection = document.getElementById('resultSection');
        const errorMessage = document.getElementById('errorMessage');
        const progressBar = document.getElementById('progressBar');
        const statusMessage = document.getElementById('statusMessage');

        uploadSection.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadSection.classList.add('dragover');
        });

        uploadSection.addEventListener('dragleave', () => {
            uploadSection.classList.remove('dragover');
        });

        uploadSection.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadSection.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file && file.type === 'application/pdf') {
                processPDF(file);
            } else {
                showError('Please upload a valid PDF file');
            }
        });

        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                processPDF(file);
            }
        });

        async function processPDF(file) {
            try {
                hideError();
                resultSection.style.display = 'none';
                progressSection.style.display = 'block';
                updateProgress(10, 'Reading PDF file...');

                const arrayBuffer = await file.arrayBuffer();
                const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
                
                updateProgress(30, `Processing ${pdf.numPages} pages...`);

                extractedData = [];
                categoryStats = { income: {}, expenses: {} };

                for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                    const page = await pdf.getPage(pageNum);
                    const textContent = await page.getTextContent();
                    
                    const items = textContent.items.map(item => ({
                        text: item.str.trim(),
                        x: Math.round(item.transform[4]),
                        y: Math.round(item.transform[5]),
                        height: Math.round(item.height)
                    }));

                    const lines = groupIntoLines(items);
                    extractTableData(lines);
                    
                    const progress = 30 + (pageNum / pdf.numPages) * 50;
                    updateProgress(progress, `Processing page ${pageNum} of ${pdf.numPages}...`);
                }

                updateProgress(85, 'Categorizing transactions...');

                // Add categories to extracted data
                extractedData.forEach(row => {
                    const category = categorizeTransaction(
                        row['Details'],
                        row['Transaction type'],
                        row['Paid in (£)'],
                        row['Paid out (£)']
                    );
                    row['Category'] = category;
                    
                    // Update category stats
                    if (row['Paid in (£)']) {
                        const amount = parseFloat(row['Paid in (£)']);
                        categoryStats.income[category] = (categoryStats.income[category] || 0) + amount;
                    }
                    if (row['Paid out (£)']) {
                        const amount = parseFloat(row['Paid out (£)']);
                        categoryStats.expenses[category] = (categoryStats.expenses[category] || 0) + amount;
                    }
                });

                updateProgress(100, 'Complete!');
                displayResults();

            } catch (error) {
                console.error('Error:', error);
                showError('Error processing PDF: ' + error.message);
                progressSection.style.display = 'none';
            }
        }

        function groupIntoLines(items) {
            items.sort((a, b) => b.y - a.y);
            
            const lines = [];
            let currentLine = [];
            let currentY = null;
            const yThreshold = 5;
            
            items.forEach(item => {
                if (item.text === '') return;
                
                if (currentY === null || Math.abs(item.y - currentY) <= yThreshold) {
                    currentLine.push(item);
                    currentY = item.y;
                } else {
                    if (currentLine.length > 0) {
                        currentLine.sort((a, b) => a.x - b.x);
                        lines.push(currentLine);
                    }
                    currentLine = [item];
                    currentY = item.y;
                }
            });
            
            if (currentLine.length > 0) {
                currentLine.sort((a, b) => a.x - b.x);
                lines.push(currentLine);
            }
            
            return lines;
        }

        function extractTableData(lines) {
            for (let line of lines) {
                const lineText = line.map(item => item.text).join(' ');
                
                const dateMatch = lineText.match(/^(\\d{1,2}\\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\\s+\\d{4})/);
                
                if (dateMatch) {
                    const date = dateMatch[1];
                    const allText = line.map(item => item.text);
                    
                    let transType = '';
                    let transTypeIndex = -1;
                    const types = ['Card Transaction Refund', 'Card Transaction', 'Domestic Transfer', 'Direct Debit', 'Fee'];
                    
                    for (let type of types) {
                        const idx = allText.findIndex(t => t.includes(type.split(' ')[0]));
                        if (idx !== -1) {
                            const checkText = allText.slice(idx, idx + type.split(' ').length).join(' ');
                            if (checkText.includes(type)) {
                                transType = type;
                                transTypeIndex = idx;
                                break;
                            }
                        }
                    }
                    
                    if (!transType) continue;
                    
                    const numbers = [];
                    for (let i = 0; i < allText.length; i++) {
                        const text = allText[i].replace(/,/g, '');
                        if (/^\\d+\\.\\d{2}$/.test(text)) {
                            numbers.push({ value: text, index: i });
                        }
                    }
                    
                    if (numbers.length < 2) continue;
                    
                    const balance = numbers[numbers.length - 1].value;
                    
                    let paidIn = '';
                    let paidOut = '';
                    
                    if (numbers.length === 3) {
                        paidIn = numbers[0].value;
                        paidOut = numbers[1].value;
                    } else if (numbers.length === 2) {
                        const amount = numbers[0].value;
                        
                        const detailsText = allText.join(' ').toLowerCase();
                        const isIncome = transType === 'Card Transaction Refund' || 
                                       (transType === 'Domestic Transfer' && (
                                           detailsText.includes('sumup') ||
                                           detailsText.includes('paymentsense') ||
                                           detailsText.includes('evo payments') ||
                                           detailsText.includes('dojo') ||
                                           detailsText.includes('american express')
                                       ));
                        
                        if (isIncome) {
                            paidIn = amount;
                        } else {
                            paidOut = amount;
                        }
                    }
                    
                    let details = [];
                    for (let i = transTypeIndex + 1; i < numbers[0].index; i++) {
                        if (allText[i] && !allText[i].includes('Tide Card') && allText[i] !== '****') {
                            details.push(allText[i]);
                        }
                    }
                    const detailsStr = details.join(' ').replace(/\\s+/g, ' ').trim();
                    
                    extractedData.push({
                        'Date': date,
                        'Transaction type': transType,
                        'Details': detailsStr,
                        'Paid in (£)': paidIn,
                        'Paid out (£)': paidOut,
                        'Balance (£)': balance
                    });
                }
            }
        }

        function displayResults() {
            progressSection.style.display = 'none';
            resultSection.style.display = 'block';

            let totalPaidIn = 0;
            let totalPaidOut = 0;

            extractedData.forEach(row => {
                if (row['Paid in (£)']) {
                    totalPaidIn += parseFloat(row['Paid in (£)']);
                }
                if (row['Paid out (£)']) {
                    totalPaidOut += parseFloat(row['Paid out (£)']);
                }
            });

            const netProfit = totalPaidIn - totalPaidOut;
            const totalCategories = Object.keys(categoryStats.income).length + Object.keys(categoryStats.expenses).length;

            document.getElementById('totalTransactions').textContent = extractedData.length;
            document.getElementById('totalPaidIn').textContent = '£' + totalPaidIn.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            document.getElementById('totalPaidOut').textContent = '£' + totalPaidOut.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            document.getElementById('totalCategories').textContent = totalCategories;
            
            const netProfitElement = document.getElementById('netProfit');
            netProfitElement.textContent = '£' + netProfit.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            netProfitElement.style.color = netProfit >= 0 ? '#4CAF50' : '#f44336';

            // Set date range from transactions
            if (extractedData.length > 0) {
                const firstDate = parseStatementDate(extractedData[0]['Date']);
                const lastDate = parseStatementDate(extractedData[extractedData.length - 1]['Date']);
                document.getElementById('startDate').value = firstDate;
                document.getElementById('endDate').value = lastDate;
            }

            // Display category summaries
            displayCategorySummary('income', 'incomeCategories');
            displayCategorySummary('expenses', 'expenseCategories');
            
            // Display financial statements
            displayTrialBalance();
            displayProfitAndLoss();
            displayBalanceSheet();

            // Display preview table
            const previewTable = document.getElementById('previewTable');
            let tableHTML = '<thead><tr>';
            const headers = ['Date', 'Transaction type', 'Details', 'Category', 'Paid in (£)', 'Paid out (£)', 'Balance (£)'];
            headers.forEach(header => {
                tableHTML += `<th>${header}</th>`;
            });
            tableHTML += '</tr></thead><tbody>';

            extractedData.slice(0, 10).forEach(row => {
                tableHTML += '<tr>';
                headers.forEach(header => {
                    const value = row[header] || '';
                    tableHTML += `<td>${value}</td>`;
                });
                tableHTML += '</tr>';
            });
            tableHTML += '</tbody>';
            previewTable.innerHTML = tableHTML;
        }

        function displayCategorySummary(type, elementId) {
            const container = document.getElementById(elementId);
            const stats = categoryStats[type];
            
            // Sort categories by amount (descending)
            const sortedCategories = Object.entries(stats).sort((a, b) => b[1] - a[1]);
            
            let html = '';
            sortedCategories.forEach(([category, amount]) => {
                const formattedAmount = '£' + amount.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                const colorClass = type === 'income' ? 'income' : 'expense';
                html += `
                    <div class="category-item">
                        <span class="category-name">${category}</span>
                        <span class="category-amount ${colorClass}">${formattedAmount}</span>
                    </div>
                `;
            });
            
            if (sortedCategories.length === 0) {
                html = '<p style="color: #999; text-align: center; padding: 20px;">No transactions in this category</p>';
            }
            
            container.innerHTML = html;
        }

        function parseStatementDate(dateStr) {
            // Parse "1 Jan 2024" format to "2024-01-01"
            const months = {
                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            };
            const parts = dateStr.trim().split(/\\s+/);
            const day = parts[0].padStart(2, '0');
            const month = months[parts[1]];
            const year = parts[2];
            return `${year}-${month}-${day}`;
        }

        function switchTab(tab) {
            // Update tab buttons
            document.querySelectorAll('.category-tab').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Update content
            document.querySelectorAll('.category-content').forEach(content => {
                content.classList.remove('active');
            });
            
            if (tab === 'income') {
                document.getElementById('incomeCategories').classList.add('active');
            } else {
                document.getElementById('expenseCategories').classList.add('active');
            }
        }

        function switchFinancialTab(tab) {
            // Update tab buttons
            const parentTabs = event.target.parentElement;
            parentTabs.querySelectorAll('.category-tab').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Update content
            const parentContent = parentTabs.nextElementSibling.parentElement;
            parentContent.querySelectorAll('.category-content').forEach(content => {
                content.classList.remove('active');
            });
            
            if (tab === 'trialbalance') {
                document.getElementById('trialBalancePreview').classList.add('active');
            } else if (tab === 'profitloss') {
                document.getElementById('profitLossPreview').classList.add('active');
            } else if (tab === 'balancesheet') {
                document.getElementById('balanceSheetPreview').classList.add('active');
            }
        }

        function displayTrialBalance() {
            const container = document.getElementById('trialBalancePreview');
            
            let html = '<div style="overflow-x: auto;"><table style="width: 100%; margin-top: 10px;">';
            html += '<thead><tr><th>Account</th><th>Debit (£)</th><th>Credit (£)</th></tr></thead><tbody>';
            
            let totalDebit = 0;
            let totalCredit = 0;
            
            // Calculate opening and closing balance
            const openingBalance = extractedData.length > 0 ? 
                parseFloat(extractedData[0]['Balance (£)']) - 
                (parseFloat(extractedData[0]['Paid in (£)']) || 0) + 
                (parseFloat(extractedData[0]['Paid out (£)']) || 0) : 0;
            const closingBalance = extractedData.length > 0 ? 
                parseFloat(extractedData[extractedData.length - 1]['Balance (£)']) : 0;
            
            // Bank Account (Asset - Debit balance)
            html += `<tr>
                <td><strong>Bank Account</strong></td>
                <td style="text-align: right;">${closingBalance.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                <td>-</td>
            </tr>`;
            totalDebit += closingBalance;
            
            html += '<tr style="height: 10px;"><td colspan="3"></td></tr>';
            
            // Expense categories (Debits)
            const sortedExpenses = Object.entries(categoryStats.expenses).sort((a, b) => a[0].localeCompare(b[0]));
            sortedExpenses.forEach(([category, amount]) => {
                totalDebit += amount;
                html += `<tr>
                    <td>${category}</td>
                    <td style="text-align: right;">${amount.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                    <td>-</td>
                </tr>`;
            });
            
            html += '<tr style="height: 10px;"><td colspan="3"></td></tr>';
            
            // Income categories (Credits)
            const sortedIncome = Object.entries(categoryStats.income).sort((a, b) => a[0].localeCompare(b[0]));
            sortedIncome.forEach(([category, amount]) => {
                totalCredit += amount;
                html += `<tr>
                    <td>${category}</td>
                    <td>-</td>
                    <td style="text-align: right;">${amount.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                </tr>`;
            });
            
            // Capital/Equity (to balance the books)
            // Capital = Opening Balance + Net Profit
            const netProfit = totalCredit - totalDebit + closingBalance;
            const capital = openingBalance + netProfit;
            
            html += '<tr style="height: 10px;"><td colspan="3"></td></tr>';
            html += `<tr>
                <td><strong>Capital/Equity</strong></td>
                <td>-</td>
                <td style="text-align: right;">${capital.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
            </tr>`;
            totalCredit += capital;
            
            // Totals
            html += `<tr style="border-top: 2px solid #667eea; background: #f0f8ff;">
                <td><strong>TOTAL</strong></td>
                <td style="text-align: right;"><strong>${totalDebit.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</strong></td>
                <td style="text-align: right;"><strong>${totalCredit.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</strong></td>
            </tr>`;
            
            html += '</tbody></table></div>';
            
            // Check if balanced
            const difference = Math.abs(totalDebit - totalCredit);
            if (difference < 0.01) {
                html += `<p style="margin-top: 15px; padding: 10px; background: #e8f5e9; border-left: 4px solid #4CAF50; font-size: 12px; color: #2e7d32;">
                    ✅ <strong>Trial Balance is balanced!</strong> Debits equal Credits.
                </p>`;
            } else {
                html += `<p style="margin-top: 15px; padding: 10px; background: #ffebee; border-left: 4px solid #f44336; font-size: 12px; color: #c62828;">
                    ⚠️ <strong>Warning:</strong> Trial Balance difference of £${difference.toFixed(2)}
                </p>`;
            }
            
            container.innerHTML = html;
        }

        function displayProfitAndLoss() {
            const container = document.getElementById('profitLossPreview');
            
            let html = '<div style="overflow-x: auto;"><table style="width: 100%; margin-top: 10px;">';
            html += '<thead><tr><th style="text-align: left;">Description</th><th style="text-align: right;">Amount (£)</th></tr></thead><tbody>';
            
            // Income Section
            html += '<tr style="background: #f0f8ff;"><td colspan="2"><strong>INCOME (RECEIPTS)</strong></td></tr>';
            let totalIncome = 0;
            const sortedIncome = Object.entries(categoryStats.income).sort((a, b) => b[1] - a[1]);
            sortedIncome.forEach(([category, amount]) => {
                totalIncome += amount;
                html += `<tr>
                    <td style="padding-left: 20px;">${category}</td>
                    <td style="text-align: right;">${amount.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                </tr>`;
            });
            html += `<tr style="font-weight: bold; background: #e3f2fd;">
                <td>Total Income</td>
                <td style="text-align: right;">${totalIncome.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
            </tr>`;
            
            // Expenses Section
            html += '<tr style="background: #fff3e0; height: 10px;"><td colspan="2"></td></tr>';
            html += '<tr style="background: #fff3e0;"><td colspan="2"><strong>EXPENSES (PAYMENTS)</strong></td></tr>';
            let totalExpenses = 0;
            const sortedExpenses = Object.entries(categoryStats.expenses).sort((a, b) => b[1] - a[1]);
            sortedExpenses.forEach(([category, amount]) => {
                totalExpenses += amount;
                html += `<tr>
                    <td style="padding-left: 20px;">${category}</td>
                    <td style="text-align: right;">${amount.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                </tr>`;
            });
            html += `<tr style="font-weight: bold; background: #ffe0b2;">
                <td>Total Expenses</td>
                <td style="text-align: right;">${totalExpenses.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
            </tr>`;
            
            // Net Profit/Loss
            const netProfit = totalIncome - totalExpenses;
            const profitColor = netProfit >= 0 ? '#4CAF50' : '#f44336';
            html += `<tr style="font-weight: bold; font-size: 16px; background: #f5f5f5; border-top: 3px solid #667eea;">
                <td>NET ${netProfit >= 0 ? 'PROFIT' : 'LOSS'}</td>
                <td style="text-align: right; color: ${profitColor};">${Math.abs(netProfit).toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
            </tr>`;
            
            html += '</tbody></table></div>';
            
            container.innerHTML = html;
        }

        function displayBalanceSheet() {
            const container = document.getElementById('balanceSheetPreview');
            
            const closingBalance = extractedData.length > 0 ? parseFloat(extractedData[extractedData.length - 1]['Balance (£)']) : 0;
            const openingBalance = extractedData.length > 0 ? parseFloat(extractedData[0]['Balance (£)']) - (parseFloat(extractedData[0]['Paid in (£)']) || 0) + (parseFloat(extractedData[0]['Paid out (£)']) || 0) : 0;
            
            let totalIncome = 0;
            Object.values(categoryStats.income).forEach(amount => totalIncome += amount);
            
            let totalExpenses = 0;
            Object.values(categoryStats.expenses).forEach(amount => totalExpenses += amount);
            
            const netProfit = totalIncome - totalExpenses;
            const equity = openingBalance + netProfit;
            
            let html = '<div style="overflow-x: auto;"><table style="width: 100%; margin-top: 10px;">';
            html += '<thead><tr><th style="text-align: left;">Description</th><th style="text-align: right;">Amount (£)</th></tr></thead><tbody>';
            
            // Assets Section
            html += '<tr style="background: #e8f5e9;"><td colspan="2"><strong>ASSETS</strong></td></tr>';
            html += `<tr>
                <td style="padding-left: 20px;">Cash at Bank</td>
                <td style="text-align: right;">${closingBalance.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
            </tr>`;
            html += `<tr style="font-weight: bold; background: #c8e6c9;">
                <td>Total Assets</td>
                <td style="text-align: right;">${closingBalance.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
            </tr>`;
            
            // Equity Section
            html += '<tr style="background: #e3f2fd; height: 10px;"><td colspan="2"></td></tr>';
            html += '<tr style="background: #e3f2fd;"><td colspan="2"><strong>EQUITY</strong></td></tr>';
            html += `<tr>
                <td style="padding-left: 20px;">Opening Balance</td>
                <td style="text-align: right;">${openingBalance.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
            </tr>`;
            html += `<tr>
                <td style="padding-left: 20px;">Net Profit/(Loss)</td>
                <td style="text-align: right; color: ${netProfit >= 0 ? '#4CAF50' : '#f44336'};">${netProfit.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
            </tr>`;
            html += `<tr style="font-weight: bold; background: #bbdefb;">
                <td>Total Equity</td>
                <td style="text-align: right;">${equity.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
            </tr>`;
            
            html += '</tbody></table></div>';
            
            // Note about balance
            const difference = Math.abs(closingBalance - equity);
            if (difference > 0.01) {
                html += `<p style="margin-top: 15px; padding: 10px; background: #fff3cd; border-left: 4px solid #ffc107; font-size: 12px;">
                    <strong>Note:</strong> This is a simplified balance sheet based on bank transactions. 
                    Difference of £${difference.toFixed(2)} may exist due to non-cash items, assets, or liabilities not captured in bank statements.
                </p>`;
            }
            
            container.innerHTML = html;
        }

        document.getElementById('downloadBtn').addEventListener('click', () => {
            const ws = XLSX.utils.json_to_sheet(extractedData);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, 'Transactions');

            const colWidths = [
                { wch: 15 }, // Date
                { wch: 20 }, // Transaction type
                { wch: 50 }, // Details
                { wch: 25 }, // Category
                { wch: 15 }, // Paid in
                { wch: 15 }, // Paid out
                { wch: 15 }  // Balance
            ];
            ws['!cols'] = colWidths;

            const now = new Date();
            const filename = `bank_statement_categorized_${now.getFullYear()}_${(now.getMonth()+1).toString().padStart(2,'0')}_${now.getDate().toString().padStart(2,'0')}.xlsx`;

            XLSX.writeFile(wb, filename);
        });

        document.getElementById('downloadTrialBalanceBtn').addEventListener('click', () => {
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            const trialBalanceData = [];
            
            // Add header with period
            trialBalanceData.push({
                'Account': 'TRIAL BALANCE',
                'Debit (£)': '',
                'Credit (£)': ''
            });
            trialBalanceData.push({
                'Account': `Period: ${startDate} to ${endDate}`,
                'Debit (£)': '',
                'Credit (£)': ''
            });
            trialBalanceData.push({
                'Account': '',
                'Debit (£)': '',
                'Credit (£)': ''
            });
            
            let totalDebit = 0;
            let totalCredit = 0;
            
            // Calculate balances
            const openingBalance = extractedData.length > 0 ? 
                parseFloat(extractedData[0]['Balance (£)']) - 
                (parseFloat(extractedData[0]['Paid in (£)']) || 0) + 
                (parseFloat(extractedData[0]['Paid out (£)']) || 0) : 0;
            const closingBalance = extractedData.length > 0 ? 
                parseFloat(extractedData[extractedData.length - 1]['Balance (£)']) : 0;
            
            // Bank Account (Asset - Debit)
            trialBalanceData.push({
                'Account': 'Bank Account',
                'Debit (£)': closingBalance.toFixed(2),
                'Credit (£)': ''
            });
            totalDebit += closingBalance;
            
            trialBalanceData.push({
                'Account': '',
                'Debit (£)': '',
                'Credit (£)': ''
            });
            
            // Expenses (Debits)
            const sortedExpenses = Object.entries(categoryStats.expenses).sort((a, b) => a[0].localeCompare(b[0]));
            sortedExpenses.forEach(([category, amount]) => {
                totalDebit += amount;
                trialBalanceData.push({
                    'Account': category,
                    'Debit (£)': amount.toFixed(2),
                    'Credit (£)': ''
                });
            });
            
            trialBalanceData.push({
                'Account': '',
                'Debit (£)': '',
                'Credit (£)': ''
            });
            
            // Income (Credits)
            const sortedIncome = Object.entries(categoryStats.income).sort((a, b) => a[0].localeCompare(b[0]));
            sortedIncome.forEach(([category, amount]) => {
                totalCredit += amount;
                trialBalanceData.push({
                    'Account': category,
                    'Debit (£)': '',
                    'Credit (£)': amount.toFixed(2)
                });
            });
            
            trialBalanceData.push({
                'Account': '',
                'Debit (£)': '',
                'Credit (£)': ''
            });
            
            // Capital/Equity (to balance)
            const netProfit = totalCredit - totalDebit + closingBalance;
            const capital = openingBalance + netProfit;
            
            trialBalanceData.push({
                'Account': 'Capital/Equity',
                'Debit (£)': '',
                'Credit (£)': capital.toFixed(2)
            });
            totalCredit += capital;
            
            // Totals
            trialBalanceData.push({
                'Account': '',
                'Debit (£)': '',
                'Credit (£)': ''
            });
            trialBalanceData.push({
                'Account': 'TOTAL',
                'Debit (£)': totalDebit.toFixed(2),
                'Credit (£)': totalCredit.toFixed(2)
            });
            
            const ws = XLSX.utils.json_to_sheet(trialBalanceData);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, 'Trial Balance');
            
            ws['!cols'] = [{ wch: 40 }, { wch: 15 }, { wch: 15 }];
            
            const now = new Date();
            const filename = `trial_balance_${now.getFullYear()}_${(now.getMonth()+1).toString().padStart(2,'0')}_${now.getDate().toString().padStart(2,'0')}.xlsx`;
            
            XLSX.writeFile(wb, filename);
        });

        document.getElementById('downloadPLBtn').addEventListener('click', () => {
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            const plData = [];
            
            // Header with period
            plData.push({
                'Description': 'PROFIT & LOSS STATEMENT',
                'Amount (£)': ''
            });
            plData.push({
                'Description': `Period: ${startDate} to ${endDate}`,
                'Amount (£)': ''
            });
            plData.push({
                'Description': '',
                'Amount (£)': ''
            });
            
            // Income
            plData.push({
                'Description': 'INCOME (RECEIPTS)',
                'Amount (£)': ''
            });
            
            let totalIncome = 0;
            const sortedIncome = Object.entries(categoryStats.income).sort((a, b) => b[1] - a[1]);
            sortedIncome.forEach(([category, amount]) => {
                totalIncome += amount;
                plData.push({
                    'Description': '  ' + category,
                    'Amount (£)': amount.toFixed(2)
                });
            });
            
            plData.push({
                'Description': 'Total Income',
                'Amount (£)': totalIncome.toFixed(2)
            });
            
            plData.push({
                'Description': '',
                'Amount (£)': ''
            });
            
            // Expenses
            plData.push({
                'Description': 'EXPENSES (PAYMENTS)',
                'Amount (£)': ''
            });
            
            let totalExpenses = 0;
            const sortedExpenses = Object.entries(categoryStats.expenses).sort((a, b) => b[1] - a[1]);
            sortedExpenses.forEach(([category, amount]) => {
                totalExpenses += amount;
                plData.push({
                    'Description': '  ' + category,
                    'Amount (£)': amount.toFixed(2)
                });
            });
            
            plData.push({
                'Description': 'Total Expenses',
                'Amount (£)': totalExpenses.toFixed(2)
            });
            
            plData.push({
                'Description': '',
                'Amount (£)': ''
            });
            
            // Net Profit/Loss
            const netProfit = totalIncome - totalExpenses;
            plData.push({
                'Description': netProfit >= 0 ? 'NET PROFIT' : 'NET LOSS',
                'Amount (£)': Math.abs(netProfit).toFixed(2)
            });
            
            const ws = XLSX.utils.json_to_sheet(plData);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, 'Profit and Loss');
            
            ws['!cols'] = [{ wch: 50 }, { wch: 15 }];
            
            const now = new Date();
            const filename = `profit_loss_${now.getFullYear()}_${(now.getMonth()+1).toString().padStart(2,'0')}_${now.getDate().toString().padStart(2,'0')}.xlsx`;
            
            XLSX.writeFile(wb, filename);
        });

        document.getElementById('downloadBalanceSheetBtn').addEventListener('click', () => {
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            const bsData = [];
            
            const closingBalance = extractedData.length > 0 ? parseFloat(extractedData[extractedData.length - 1]['Balance (£)']) : 0;
            const openingBalance = extractedData.length > 0 ? parseFloat(extractedData[0]['Balance (£)']) - (parseFloat(extractedData[0]['Paid in (£)']) || 0) + (parseFloat(extractedData[0]['Paid out (£)']) || 0) : 0;
            
            let totalIncome = 0;
            Object.values(categoryStats.income).forEach(amount => totalIncome += amount);
            
            let totalExpenses = 0;
            Object.values(categoryStats.expenses).forEach(amount => totalExpenses += amount);
            
            const netProfit = totalIncome - totalExpenses;
            const equity = openingBalance + netProfit;
            
            // Header with date
            bsData.push({
                'Description': 'BALANCE SHEET',
                'Amount (£)': ''
            });
            bsData.push({
                'Description': `As at: ${endDate}`,
                'Amount (£)': ''
            });
            bsData.push({
                'Description': '',
                'Amount (£)': ''
            });
            
            // Assets
            bsData.push({
                'Description': 'ASSETS',
                'Amount (£)': ''
            });
            bsData.push({
                'Description': '  Cash at Bank',
                'Amount (£)': closingBalance.toFixed(2)
            });
            bsData.push({
                'Description': 'Total Assets',
                'Amount (£)': closingBalance.toFixed(2)
            });
            
            bsData.push({
                'Description': '',
                'Amount (£)': ''
            });
            
            // Equity
            bsData.push({
                'Description': 'EQUITY',
                'Amount (£)': ''
            });
            bsData.push({
                'Description': '  Opening Balance',
                'Amount (£)': openingBalance.toFixed(2)
            });
            bsData.push({
                'Description': '  Net Profit/(Loss)',
                'Amount (£)': netProfit.toFixed(2)
            });
            bsData.push({
                'Description': 'Total Equity',
                'Amount (£)': equity.toFixed(2)
            });
            
            const ws = XLSX.utils.json_to_sheet(bsData);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, 'Balance Sheet');
            
            ws['!cols'] = [{ wch: 50 }, { wch: 15 }];
            
            const now = new Date();
            const filename = `balance_sheet_${now.getFullYear()}_${(now.getMonth()+1).toString().padStart(2,'0')}_${now.getDate().toString().padStart(2,'0')}.xlsx`;
            
            XLSX.writeFile(wb, filename);
        });

        function updateProgress(percent, message) {
            progressBar.style.width = percent + '%';
            progressBar.textContent = Math.round(percent) + '%';
            statusMessage.textContent = message;
        }

        function showError(message) {
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
        }

        function hideError() {
            errorMessage.style.display = 'none';
        }
    </script>
</body>
</html>
"""

# Display the HTML component
components.html(html_content, height=1200, scrolling=True)
