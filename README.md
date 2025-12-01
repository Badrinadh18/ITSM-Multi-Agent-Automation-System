# 🚀 AI-Driven ITSM Multi-Agent System (ServiceNow Simulation)
### End-to-End Automated Ticketing, Diagnostics, Knowledge Search, and IT Support Workflow  
Built using **Google ADK**, **Gemini 2.5**, **FAISS**, and a fully orchestrated **multi-agent architecture**

---

## 📌 **Project Summary**

This project is an **end-to-end ITSM automation system** built using **Google ADK**, **Gemini models**, and a full **multi-agent architecture** that simulates a ServiceNow-like environment.

It automates:

- Issue intake  
- Classification  
- Knowledge base lookup  
- Diagnostics  
- Ticket creation  
- Escalation  
- Status updates  
- Observability & event tracing  

The system is designed to behave like a real IT support agent that understands user problems, diagnoses them, searches internal/external knowledge, and generates structured incidents.

This project is my **Capstone Submission** for the Kaggle Gemini Agents course.

---

# 📘 **Table of Contents**

1. [Problem Statement](#-problem-statement)  
2. [Solution Overview](#-solution-overview)  
3. [Architecture](#-Architecture)  
4. [Multi-Agent Workflow](#-multi-agent-workflow)  
5. [Folder Structure](#-folder-structure)    
6. [Setup Instructions](#-setup-instructions)   
7. [Testing](#-testing)  
8. [Agent-workflow](#-Agent-workflow)   
9. [Future Enhancements](#-future-enhancements)  

---

# 🧩 **Problem Statement**

Enterprise IT teams receive thousands of support tickets daily:

- VPN issues  
- Password resets  
- Software failures  
- Network outages  
- Access requests  

Manually triaging and diagnosing every issue is slow, expensive, and error-prone.

**Goal:**  
Build an **autonomous ITSM assistant** that:

- Understands user messages  
- Classifies issues  
- Consults internal KB  
- Runs diagnostics  
- Creates and updates tickets  
- Escalates automatically  
- Tracks ticket lifecycle  

All without human intervention.

---

# 🚀 **Solution Overview**

This project implements a production-grade **Multi-Agent ITSM Pipeline** using:

### ✔ Google ADK (Agent Development Kit)  
For agent orchestration & fast prototyping.

### ✔ Gemini Models  
Used for:  
- Text classification  
- Diagnostics generation  
- KB search reasoning  
- Pipeline orchestration  

### ✔ Custom Tools  
Simulated ServiceNow tools:
- Create ticket  
- Update ticket  
- Check status  
- Vector Knowledge Base (FAISS)  
- Google Search  
- Code Executor  
- MCP file tools  

### ✔ Observability Plugin  
Tracks:
- Agent calls  
- LLM calls  
- Tools  
- Session IDs  
- Latency  
- Debug traces  

This results in a **self-contained, autonomous IT Service assistant**.

---

# 🏗️ **Architecture**

Below is the high-level architecture of your system:

```bash

                    ┌───────────────────────┐
                    │     User Message      │
                    └───────────┬───────────┘
                                │
                                ▼
                   ┌────────────────────────────┐
                   │     Orchestrator Agent     │
                   │ (Master Router + Memory)   │
                   └───────────┬────────────────┘
   ┌──────────────┬────────────┼───────────────┬───────────────┐
   ▼              ▼             ▼               ▼               ▼
┌────────────┐ ┌────────────┐ ┌──────────┐ ┌────────────┐ ┌───────────────┐
│ Intake │     │ Classifier │ │ KB Agent │ │ Diagnostics│ │ ServiceNow    │
│ Agent │      │ Agent      │ │ (FAISS)  │ │ Agent      │ │ Creator Agent │
└────────────┘ └────────────┘ └──────────┘ └────────────┘ └───────────────┘
│
▼
┌────────────────────────┐
│ Escalation + Status    │
│ Update Agents          │
└────────────────────────┘

```

---

# 🔄 **Multi-Agent Workflow**

Each user message triggers the following pipeline:

### **1️⃣ Intake Agent**
Extracts:
- Issue summary  
- Device  
- Description  
- Urgency  

### **2️⃣ Classifier Agent**
Outputs:
- Category  
- Subcategory  
- Impact  
- Priority  
- Recommended team  

### **3️⃣ Knowledge Base Agent**
- Searches FAISS + embeddings  
- Adds external reasoning  
- Returns troubleshooting steps  

### **4️⃣ Diagnostics Agent**
- Identifies commands needed  
- PowerShell / Windows checks  
- Requests missing user info  

### **5️⃣ ServiceNow Creator Agent**
Creates a simulated ServiceNow ticket:

INC0000001
Priority: P2
Category: Access → VPN

### **6️⃣ Escalation Agent**
Auto-escalates if needed (P1/P2).

### **7️⃣ Status Loop**
Tracks:  
`OPEN → IN_PROGRESS → RESOLVED`

---

# 📁 **Folder Structure**
```bash
servicenow-agent/
│
├── agents/
│ ├── app.py # All apps & runners
│ ├── setup.py # LLM factory, retry, logging
│ ├── orchestrator.py # Master router agent
│ ├── ticket_agents.py # All ITSM pipeline agents
│ ├── session_tools.py # User memory tools
│ └── session_helpers.py # Dev-only helpers
│
├── tools/
│ ├── custom_tools.py # Ticketing, logs, status
│ ├── builtin_tools.py # Google Search, executor
│ ├── vector_kb.py # FAISS store + embeddings
│ └── mcp_tools.py # MCP file tools
│
├── plugins/
│ └── observability_plugin.py
│
├── test/
│ └── test_system.py # Full integration test
│
├── logs/
│ ├── observability_trace.csv
│ ├── observability.jsonl
│ └── app.log
│
├── faiss_docstore.pkl
├── faiss_store.index
├── itsm_sessions.db
├── requirements.txt
├── .env (ignored)
└── README.md
```

---

# ⚙️ **Setup Instructions**

### **1. Clone the repo**
```bash
git clone https://github.com/Badrinadh18/ITSM-Multi-Agent-Automation-System.git
cd ITSM-Multi-Agent-Automation-System
```
### ** 2. Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```
### **3. Install dependencies**
```bash
pip install -r requirements.txt
```
### **4. Add .env file**
```bash
GOOGLE_API_KEY=your_key_here
```
### **5. Run full system test**
```bash
python test/test_system.py
```
---
## 📌 7. Running Your Multi-Agent System

### ▶️ Manual Interaction via Python REPL

You can manually test the orchestrator by running the following code in a Python REPL:

```python
from agents.app import orchestrator_app
from google.adk.runners import AgentRunner

runner = AgentRunner(app=orchestrator_app)

events = runner.run("My VPN is failing after Windows update.")

for e in events:
    print(e)
```
## 🧾 Output (End-to-End Pipeline Result)

Below is a sample full JSON output produced by the ITSM multi-agent pipeline:

```json
{
  "issue_summary": "Laptop cannot connect to VPN after Windows update.",
  "category": "Network",
  "priority": "P3",
  "kb_match_found": true,
  "external_insights": [
    "Recent Windows updates cause VPN authentication issues",
    "Ensure the VPN client is updated"
  ],
  "diagnostics_required": true,
  "commands": [
    "Get-Hotfix | Select-Object Description, InstalledOn",
    "Get-VPNConnection",
    "Test-NetConnection -TraceRoute"
  ],
  "ticket_id": "INC0000001",
  "final_status": "Pending"
}
```

---
## 🧠 **Agent-Workflow**

When a user sends a message like:

> "After last night's Windows update, my VPN keeps failing."

The system performs the following steps:

---

### **1. OrchestratorAgent**
- The **brain** of the system  
- First retrieves user identity via **session memory**  
- Decides **which agent** should handle the request next

---

### **2. IntakeAgent**
Extracts structured information:
- **Issue summary**
- **Full description**
- **Device**
- **Urgency**

---

### **3. ClassifierAgent**
Predicts:
- **Category → Network**
- **Subcategory → VPN**
- **Priority → P3**
- **Impact → Medium**

---

### **4. KBAgent (Knowledge Engine)**  
Performs enterprise knowledge retrieval:
- Searches **FAISS vector KB**
- Runs **Gemini embeddings**
- Performs **Google Search fallback**
- Returns **troubleshooting steps + insights**

---

### **5. DiagnosticsAgent**
Generates:
- **PowerShell diagnostic commands**
- **Initial troubleshooting steps**
- **Notes for L1/L2 IT team**

---

### **6. ServiceNowCreatorAgent**
Creates a simulated ticket:

> **INC0000001 – VPN authentication failure after Windows update**

This simulates full integration with an ITSM system.

---

### **7. EscalationAgent**
Determines whether escalation to:
- **L2 Team**
- **Network Engineers**
- **Security Team**

is required based on severity and classification.

---

### **8. StatusCheckerAgent & StatusUpdaterAgent**
Handles the ticket lifecycle:
- **In Progress**
- **Resolved**
- **Closed**

Simulates ServiceNow-style ticket state transitions.

---

### **9. Final Output**
The system returns a complete, human-friendly summary including:
- Extracted issue details  
- Classification (Category, Priority, Impact)  
- Knowledge Base insights  
- Diagnostics  
- Ticket ID and status  

**End-to-end automation from user message → full IT incident workflow.**


---
# 🚧 **Future Enhancements**

-	Real ServiceNow API integration
-	Web-based ADK interface
-	SLA-based escalation logic
-	Email + Slack connectors
-	Real PowerShell command execution
-	Live analytics dashboard



