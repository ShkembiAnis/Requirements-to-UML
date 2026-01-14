# Requirements-to-UML Prototype

**Automated Transformation of Natural-Language Requirements into UML Class Diagrams**

Bachelor Thesis Prototype - Anis Shkembi (FH Campus Wien)

---

## 📋 Overview

This prototype automatically transforms textual requirement documents (PDF, DOCX, TXT) into UML class diagrams using:
- **Rule-based NLP techniques** for entity and relationship extraction
- **Model Context Protocol (MCP)** for tool integration
- **Claude Desktop** as the user interface
- **Miro** for collaborative UML visualization

**Demo:** From a requirements PDF → Automatic UML class diagram with classes, attributes, and relationships in 30 seconds.

---

## ⚠️ Prerequisites

### **Required:**

1. **Claude Pro Subscription** ($20/month)
    - ❌ **Free tier does NOT support MCP servers**
    - ✅ Pro tier required for local tool integration

2. **Miro Account** (Free tier works)
    - Sign up at: https://miro.com/signup/
    - Create at least one board for diagrams

3. **Python 3.10+**
    - Download: https://www.python.org/downloads/
    - Verify: `python --version`


---

## 🚀 Installation

### **Step 1: Clone Repository**
```bash
git clone https://github.com/YOUR_USERNAME/requirements-to-uml.git
cd requirements-to-uml
```

### **Step 2: Create Virtual Environment**

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### **Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Required packages (requirements.txt):**
```
mcp==1.1.2
pydantic==2.12.5
uvicorn==0.40.0
python-dotenv==1.0.0
requests==2.31.0
pdfplumber==0.11.0
python-docx==1.1.0
```

### **Step 4: Verify Installation**
```bash
python -c "import pdfplumber, docx, requests, mcp; print('All dependencies installed successfully!')"
```

**Expected output:** `All dependencies installed successfully!`

---

## 🔑 Configuration

### **Step 1: Get Miro API Token**

1. Go to: https://miro.com/app/settings/user-profile/apps
2. Click **"Create new app"**
3. Fill in:
    - App name: `Requirements-UML`
    - Description: `Thesis prototype`
4. Click **"Create"**
5. Under **"Permissions"**, enable:
    - `boards:read`
    - `boards:write`
6. Click **"Install app and get OAuth token"**
7. Copy the **Access Token** (starts with `ey...`)

### **Step 2: Create .env File**

Create a file named `.env` in the project root:
```bash
# .env
MIRO_ACCESS_TOKEN=YOUR_TOKEN_HERE
```

**Example:**
```bash
MIRO_ACCESS_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **Step 3: Get Miro Board ID**

1. Open any Miro board in your browser
2. Copy the board ID from URL:
```
   https://miro.com/app/board/uXjVGRZh1IE=/
                                ^^^^^^^^^ This is your board ID
```

---

## 🔧 Claude Desktop Configuration

### **Step 1: Locate Config File**

1. Open **Claude Desktop**
2. Go to **Settings** (gear icon or menu)
3. Click **Developer** in the left sidebar
4. Click **"Edit Config"** button under "Local MCP servers"
5. This will open `claude_desktop_config.json` in your default text editor

### **Step 2: Create/Edit Config File**

**If file doesn't exist, create it. If it exists, add the `mcpServers` section.**

**Windows Configuration:**
```json
{
  "mcpServers": {
    "requirements-analyzer": {
      "command": "C:\\Users\\YOUR_USERNAME\\Documents\\requirements-to-uml\\venv\\Scripts\\python.exe",
      "args": ["-m", "app.mcp_server"],
      "cwd": "C:\\Users\\YOUR_USERNAME\\Documents\\requirements-to-uml",
      "env": {
        "PYTHONPATH": "C:\\Users\\YOUR_USERNAME\\Documents\\requirements-to-uml"
      }
    }
  }
}
```

**macOS/Linux Configuration:**
```json
{
  "mcpServers": {
    "requirements-analyzer": {
      "command": "/Users/YOUR_USERNAME/requirements-to-uml/venv/bin/python",
      "args": ["-m", "app.mcp_server"],
      "cwd": "/Users/YOUR_USERNAME/requirements-to-uml",
      "env": {
        "PYTHONPATH": "/Users/YOUR_USERNAME/requirements-to-uml"
      }
    }
  }
}
```

### **Step 3: Update Paths**

⚠️ **CRITICAL: Replace `YOUR_USERNAME` with your actual username!**

**Find your paths:**

**Windows:**
```bash
# In PowerShell (in project directory with venv activated):
(Get-Command python).Source
# Copy this path to "command"

# Current directory:
pwd
# Copy this path to "cwd" and "PYTHONPATH"
```

**macOS/Linux:**
```bash
# In terminal (in project directory with venv activated):
which python
# Copy this path to "command"

# Current directory:
pwd
# Copy this path to "cwd" and "PYTHONPATH"
```

### **Step 4: Verify Configuration**

Your final config should look like:
```json
{
  "mcpServers": {
    "requirements-analyzer": {
      "command": "/ABSOLUTE/PATH/TO/venv/bin/python",
      "args": ["-m", "app.mcp_server"],
      "cwd": "/ABSOLUTE/PATH/TO/requirements-to-uml",
      "env": {
        "PYTHONPATH": "/ABSOLUTE/PATH/TO/requirements-to-uml"
      }
    }
  }
}
```

**⚠️ Common Mistakes:**
- Using relative paths (won't work!)
- Forgetting double backslashes on Windows (`\\` not `\`)
- Wrong Python path (system Python instead of venv Python)
- Missing PYTHONPATH environment variable

---

## ▶️ Usage

### **Step 1: Start Claude Desktop**

1. **Close Claude Desktop completely** (including system tray)
2. Wait 5 seconds
3. **Open Claude Desktop**
4. Go to **Settings → Developer → Local MCP servers**
5. Verify **"requirements-analyzer"** shows status **"running"** ✅

### **Step 2: Verify Tools Available**

In Claude Desktop chat, type:
```
What tools do you have available?
```

**Expected response includes:**
```
Requirements Analysis & Visualization
* Requirements analyzer: Extract domain models from software requirements
* Miro integration: Create UML class diagrams in Miro boards
* File support: Analyze PDF, DOCX, and TXT requirement files
```

### **Step 3: Analyze Requirements**

**Example prompt:**
```
I have a requirements PDF at: C:\YOUR_PATH\requirements-to-uml\data\input\requirements.pdf

Please analyze it and create a UML diagram in my Miro board: uXjVGRZh1IE=
```

**Replace with your paths:**
- File path: absolute path to your requirements document
- Board ID: your Miro board ID (from URL)

**What happens:**
1. Claude calls `analyze_and_visualize` tool
2. System extracts text from PDF
3. NLP pipeline identifies classes, attributes, relations
4. Domain model is constructed
5. UML diagram is created in Miro
6. Claude provides link to board

---

## 📁 Project Structure
```
requirements-to-uml/
├── app/
│   ├── mcp_server.py           # MCP server implementation
│   ├── file_processor.py       # PDF/DOCX/TXT text extraction
│   ├── extract.py              # NLP entity extraction (rule-based)
│   ├── filter.py               # Requirement classification
│   ├── model_builder.py        # Domain model construction
│   ├── miro_client.py          # Miro API wrapper
│   └── miro_visualizer.py      # UML diagram generation
├── data/
│   ├── input/                  # Test requirement documents
│   └── output/                 # Generated outputs (optional)
├── tests/                      # Unit tests
├── .env                        # API keys (DO NOT COMMIT)
├── .env.example                # Template for .env
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🧪 Testing the Setup

### **Test 1: Verify MCP Server Runs**
```bash
# In project directory with venv activated:
python -m app.mcp_server
```

**Expected:** Process hangs (waiting for MCP messages) - this is correct!
**Press Ctrl+C to stop**

If you see errors here, the MCP server won't work in Claude Desktop.

### **Test 2: Verify File Processing**
```bash
python -c "from app.file_processor import extract_text; print(extract_text('data/input/requirements.pdf')[:200])"
```

**Expected:** Prints first 200 characters of extracted text from PDF

### **Test 3: Verify Miro Connection**
```bash
python -c "from app.miro_client import get_headers; print('Token configured' if get_headers()['Authorization'] else 'Token missing')"
```

**Expected:** `Token configured`

### **Test 4: End-to-End Test in Claude Desktop**

Use the provided example requirements:
```
Analyze the file: C:\YOUR_PATH\requirements-to-uml\data\input\requirements.pdf
And create a UML diagram in board: YOUR_BOARD_ID
```

## 📊 Example Output

**Input:** `requirements.pdf` describing E-Commerce Order Management System

**Extracted Domain Model:**
- **9 classes:** Customer, Order, Product, Payment, ShoppingCart, Address, Review, OrderItem, Administrator
- **11 relationships:**
    - Customer → ShoppingCart (1:1)
    - Customer → Order (1:1..*)
    - Order → OrderItem (1:1..*)
    - OrderItem → Product (1:1)
    - Order → Payment (1:1)
    - Customer → Review (1:0..*)
    - Product → Review (1:0..*)
    - Customer → Address (1:0..*)
    - Order → Address (1:1)
    - And more...

**Generated UML Diagram:**
- All classes with attributes
- Association lines with cardinalities
- Relationship labels
- Professional layout

**Time:** ~30 seconds (vs. 30-60 minutes manual creation)

**Miro Link:** https://miro.com/app/board/uXjVGRZh1IE=

---

### Document Format Recommendations

**Best Results:** DOCX format
- Cleaner text extraction
- No page break artifacts
- All content preserved

**Acceptable:** PDF format
- Generally works well
- May lose content at page boundaries
- Occasional word splitting issues

**Recommendation:** For critical requirements, use DOCX format or verify PDF extraction results.

## 🎓 Academic Context

**Thesis:** Automatisierte Transformation natürlichsprachlicher Anforderungen in UML-Klassendiagramme zur Reduzierung des Entwickleraufwands

**English:** Automated Transformation of Natural-Language Requirements into UML Class Diagrams for Reducing Developer Workload

**Student:** Anis Shkembi  
**Matriculation:** 2410838018, 51917465  
**Institution:** FH Campus Wien  
**Supervisor:** Thomas Berger BSc. MSc.  
**Semester:** Winter 2024/2025

**Research Question:**  
How effectively can natural-language requirement documents be automatically transformed into UML class diagrams in terms of time saved while using NLP techniques and the Model Context Protocol (MCP)?

---

## 🔬 Technical Approach

### **NLP Extraction (Rule-Based)**

No machine learning models required. Uses:
- **Pattern matching** for entity detection (DEF, REQ, CON keywords)
- **Keyword extraction** for class names and attributes
- **Heuristic rules** for relationship detection
- **Text segmentation** for requirement classification

**Advantages:**
- Fast (no model loading)
- Deterministic (reproducible results)
- Easy to understand and extend
- No training data required

### **MCP Integration**

Model Context Protocol provides:
- Standardized tool interface
- Integration with Claude Desktop
- Conversational interaction
- Error handling and logging

### **Miro Visualization**

Automatic diagram generation with:
- Grid-based layout algorithm
- Class boxes with attributes
- Association connectors with cardinalities
- Professional styling

---

## 📝 Known Limitations

1. **Best with structured requirements** - Works optimally with formal requirement documents (IEEE 830 style)
2. **Association relationships only** - Inheritance and composition detection planned for future work
3. **English language only** - Pattern matching tuned for English requirements
4. **Requires Claude Pro** - MCP not available on free tier ($20/month)
5. **Heuristic attribute types** - Type inference based on naming conventions
6. **Manual Miro board setup** - User must create board and provide ID
7. **Limited error recovery** - Some malformed requirements may cause extraction failures

---

## 🔮 Future Work

### **Quantitative Evaluation:**
- Test on diverse requirement documents
- Compare with manually created reference diagrams
- Measure time savings, precision, recall
- Statistical analysis

### **Expert Evaluation:**
- Domain experts review generated diagrams
- Structured evaluation forms
- Assess correctness, completeness, domain validity

### **Practitioner Survey:**
- Software engineers use the tool
- Survey on usefulness, usability, time savings
- Real-world workflow integration feedback

### **Technical Enhancements:**
- Support for inheritance and composition relationships
- Multi-language support (German)
- Improved attribute type detection
- Export to PlantUML, GraphViz formats
- Web-based UI (no Claude Pro required)

---

## 🎉 Success Indicators

You know it's working when:

1. ✅ Claude Desktop Settings shows "requirements-analyzer: running"
2. ✅ Claude lists "Requirements Analysis & Visualization" tools
3. ✅ Prompt triggers tool execution (you see "analyzing..." message)
4. ✅ Miro board updates with class diagram
5. ✅ Claude provides summary: "9 classes, 11 relationships created"

---

## 📚 Additional Resources

- **MCP Documentation:** https://modelcontextprotocol.io/
- **Miro API Docs:** https://developers.miro.com/docs
- **Claude API Docs:** https://docs.anthropic.com/
- **Python dotenv:** https://pypi.org/project/python-dotenv/
- **pdfplumber:** https://github.com/jsvine/pdfplumber
- **python-docx:** https://python-docx.readthedocs.io/



**Last Updated:** January 2025  
**README Version:** 1.0  
**Prototype Version:** 1.0 (Semester 3 - Implementation Phase)

---

## 📧 Contact

**Student:** Anis Shkembi  
**Email:** anis.shkembi@stud.hcw.ac.at 
**Institution:** FH Campus Wien  
**Program:** Software Design and Engineering

