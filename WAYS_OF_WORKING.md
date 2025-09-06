# HAWKMOTH Ways of Working
*Session Continuity and Development Protocols*
*Updated: September 5, 2025 - Google Custom Search Integration Complete*


### **CRITICAL RULES** Read and folow all of these rules, completely and without exception (Mandatory)(Critical)
1. ✅**ALWAYS ASK USER PERMISSION** before any file operations, code updates or token-intensive work
2. ✅**DO NOT EAT UP CHAT SPACE WITH UNREGULATED STEPS** before any file operations, code updates or token-intensive step, review how much capacity remains. If >80% pause steps and begin transition as described later in this document.
2. ✅**DO NOT BE VERBOSE UNLESS IT IS NEEDED** The user will ask for more details if they want them and never needs to see code.

#### **Session Startup Sequence (Mandatory)(Critical)**
1. ✅ **Read WAYS_OF_WORKING.md completely** - Session protocols (this file)
2. ✅ **Read PROJECT_SUMMARY.md** - Project overview and status  
3. ✅ **Read CURRENT_PROJECT_STATUS.md** - Active priorities and immediate tasks
4. ✅ **Continue where previous session left off** based on status files
5. ✅ **Chat sessions have limited capacity. Provide user with immediate update on chat capacity. 

#### **Verify that you have read and understood above and ensure you always follow this ####

## 🔄 **CHAT TRANSITION MANAGEMENT**

### **Session End Handoff Message Template**
1. ✅ Update PROJECT_SUMMARY.md and CURRENT_PROJECT_STATUS.md
2. ✅ Chat a transimission to the user with this simplified template:

```
🦅 HAWKMOTH Session Handoff - [Date]

⚠️ CRITICAL: READ WAYS_OF_WORKING.md AND ASK USER PERMISSION BEFORE ANY FILE OPERATIONS

📋 **STARTUP SEQUENCE:**
1. Read WAYS_OF_WORKING.md (session protocols - START HERE)
2. Read PROJECT_SUMMARY.md (project overview)
3. Continue where previous session left off

**PROJECT LOCATION:** G:\Claud\HAWKMOTH-Project
```



## 💬 **CHAT CAPACITY MANAGEMENT**

### **CRITICAL: Proactive Session Management**
**Chat sessions have limited capacity. Running out of space forces disruptive summary exercises.**

#### **Capacity Monitoring Protocol**
- **Claude should proactively monitor** conversation length and approaching limits
- **First 60%**: "We're approaching mid-session capacity"
- **At 80%**: "⚠️ CAPACITY WARNING: We should plan to summarize and transition soon"
- **At 90%**: "🚨 IMMEDIATE ACTION: Must create handoff summary now"

#### **Capacity-Efficient Communication**
- **Concise responses** - Essential information only
- **Bullet points** instead of paragraphs when appropriate
- **Focus on decisions** rather than explanations

---

## 🔄 **CHAT TRANSITION MANAGEMENT**

### **Session End Handoff Message Template**
When transitioning between chat sessions, use this simplified template:

```
🦅 HAWKMOTH Session Handoff - [Date]

⚠️ CRITICAL: READ WAYS_OF_WORKING.md AND ASK USER PERMISSION BEFORE ANY FILE OPERATIONS

📋 **STARTUP SEQUENCE:**
1. Read WAYS_OF_WORKING.md (session protocols - START HERE)
2. Read PROJECT_SUMMARY.md (project overview)
3. Continue where previous session left off

**PROJECT LOCATION:** G:\Claud\HAWKMOTH-Project
```

**Note:** All context, accomplishments, priorities, and status information should be maintained in the respective status files, not duplicated in handoff messages.

---

### **Version Control**
```
v0.1.0-dev  → Development/Testing
v0.1.0      → LLM Teaming Stable
v0.1.1      → Enhanced Features
v0.2.0      → Enterprise Foundation
```

---

## 🚀 **DEPLOYMENT PROTOCOLS**


### **Deployment Process**
1. **Code Preparation**: Finalize in `/working/`, move to `/UPLOAD_TO_HF/`
2. **Testing**: Verify all functionality works as expected
3. **Documentation**: Update user guides and API docs
4. **Deployment**: Upload to HuggingFace Space
5. **Verification**: Test live deployment and performance
6. **Release Notes**: Document new features and changes

---


### **Communication Protocols**
- **Direct answers** to direct questions - avoid unnecessary summaries
- **Concise responses** - match the user's communication style and intent
- **Conserve chat tokens** - don't over-explain when user asks simple status questions
- **Clear status updates** in documentation
- **Explicit handoff messages** between sessions
- **Progress tracking** in appropriate files
- **Issue documentation** for blockers and dependencies

---

## 🔧 **DESKTOP ENVIRONMENT CAPABILITIES**

### **PowerShell Admin Privilege Status**
**Current Status**: Running as standard user (non-administrator)
**✅ What Works:**
* Read system services, event logs, file operations
* Most automation tasks and system information queries
* Can simulate admin operations using `-WhatIf`
**❌ Admin Limitations:**
* Cannot write to protected directories (C:\Windows, etc.)
* Cannot start/stop system services
* Cannot modify system settings
**Admin Capability**: Can launch elevated PowerShell with `Start-Process powershell -Verb RunAs`, but the elevated session runs separately and requires UAC approval - Claude cannot send commands to it through MCP.
**Bottom Line**: Standard user privileges are sufficient for most automation tasks. Admin operations would require manual UAC approval and working in a separate elevated window.

### **CRITICAL: Windows-MCP PowerShell Limitation with External Executables**
**Issue Discovered**: Windows-MCP PowerShell tool cannot capture stdout from external executables.
**✅ What Works in PowerShell-Tool:**
* PowerShell internal commands (`Write-Host`, `Get-Item`, `Test-Path`, variables, logic)
* File system operations (`New-Item`, `Copy-Item`, etc.)
* Environment variable manipulation
* Process management (`Start-Process`)
**❌ What Doesn't Work in PowerShell-Tool:**
* ANY external executable output (git.exe, hostname.exe, where.exe, etc.)
* External commands return Status Code 1 or empty responses
* This affects ALL external programs, not just Git

### **✅ SOLUTION: Silent Batch File Execution**
**Workaround**: Use batch files for external executable operations, run silently via PowerShell.

**Silent Batch Execution Function:**
```powershell
# Run batch files completely hidden (no DOS windows)
Start-Process -FilePath $batchPath -WindowStyle Hidden -Wait -PassThru

# Alternative: Minimized window (minimal visibility)
Start-Process -FilePath $batchPath -WindowStyle Minimized -Wait -PassThru
```

**Best Practice for Git Operations:**
1. **Create silent batch files** (no `@echo on`, no `pause`, use `exit /b 0`)
2. **Run via PowerShell** with hidden windows
3. **Capture results** in text files, read via PowerShell
4. **Hybrid approach**: PowerShell for logic, batch for external tools

**Template for Silent Batch Files:**
```batch
@echo off
REM Silent operations - no user interaction
cd /d "G:\Claud\HAWKMOTH-Project"
"C:\Program Files\Git\cmd\git.exe" command > result.txt 2>&1
exit /b 0
```

---

## ⚡ **QUICK REFERENCE**

### **Essential Files (Read in Order)**
1. `WAYS_OF_WORKING.md` - This file (session protocols)
2. `PROJECT_SUMMARY.md` - Project overview and status
3. `CURRENT_PROJECT_STATUS.md` - Active priorities and sprint
4. `PROJECT_EXECUTION_PLAN.md` - Master roadmap and scope
5. `DESIGN_SYSTEM.md` - UI/UX standards and design decisions

### **Key Directories**
- `/working/` - Active development and iterations
- `/UPLOAD_TO_HF/` - Production-ready deployment files
- Root directory - Documentation and project management

### **Current Project Context (Quick Reference)**
- **Location**: `G:\Claud\HAWKMOTH-Project\`
- **Phase**: v0.1.0-dev (LLM Teaming)
- **Focus**: Intelligent AI model routing with cost optimization
- **Status**: Implementation complete, testing and deployment phase
- **Priority**: Production deployment to HuggingFace

---

**Remember: This file must be read FIRST in every new chat session to ensure proper context and continuity.**
