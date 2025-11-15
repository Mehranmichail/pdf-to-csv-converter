# OLD (WRONG) - Was guessing which column had what
# It would put everything in "Paid Out" by default

# NEW (CORRECT) - Uses ACTUAL column positions from PDF
# Column 0: Date
# Column 1: Transaction Type  
# Column 2: Details
# Column 3: Paid In (£)     ← ALWAYS column 3
# Column 4: Paid Out (£)    ← ALWAYS column 4
# Column 5: Balance (£)     ← ALWAYS column 5
```

---

## 📊 **Now It Works Perfectly:**

**Page 1, Row 7 from PDF:**
```
22 Apr 2025 | Internal Book Transfer | MDK OUTSOURCING... | 2,541.96 | [empty] | 19,292.37
```

**Result:**
```
Date: 22 Apr 2025
Type: Internal Book Transfer
Details: MDK OUTSOURCING...
Paid In: 2,541.96  ✅ CORRECT!
Paid Out: [empty]
Balance: 19,292.37
