# HAWKMOTH Ways of Working
*Session Continuity and Development Protocols*
*Updated: September 5, 2025*

## 🔄 **SESSION CONTINUITY PROTOCOL**

### **CRITICAL: Every Chat Session Must Start Here**
**This file is the FIRST file to read in any new chat session.**

#### **Session Startup Sequence (Mandatory)**
1. ✅ **Read WAYS_OF_WORKING.md completely** - Session protocols (this file)
2. ✅ **Read PROJECT_SUMMARY.md** - Project overview and status  
3. ✅ **Read CURRENT_PROJECT_STATUS.md** - Active priorities and immediate tasks
4. 🚨 **ASK USER PERMISSION** before any file operations or token-intensive work
5. ✅ **Continue where previous session left off** based on status files

#### **Context Establishment Checklist**
Every session must establish:
- [ ] **Project Phase**: Current version and development stage
- [ ] **Active Sprint**: What work is currently in progress
- [ ] **Immediate Priority**: Next critical task to complete
- [ ] **Recent Achievements**: What was just completed
- [ ] **Known Blockers**: Any impediments or dependencies
- [ ] **Session Goal**: What this session aims to accomplish

---

## 📋 **DEVELOPMENT PROTOCOLS**

### **Core Development Process**
**Research → Design → Implement → Test → Deploy**

#### **1. Research Phase**
- Analyze requirements and technical approach
- Investigate solutions and alternatives
- Document findings and recommendations

#### **2. Design Phase**
- Create architecture and implementation plan
- Define interfaces and data structures
- Plan testing and validation approach

#### **3. Implementation Phase**
- Code in `/working/` directory using iteration approach
- Follow naming: `filename_iter1.py`, `filename_iter2.py`, etc.
- Regular documentation updates during development

#### **4. Testing Phase**
- Unit testing and integration testing
- Performance validation
- User experience verification

#### **5. Deployment Phase**
- Move production-ready files to `/UPLOAD_TO_HF/`
- Update version tracking
- Deploy to HuggingFace Spaces

### **Working Directory Structure**
```
/working/           # Iteration-based development
├── *_iter1.py     # First iteration files
├── *_iter2.py     # Refined implementations  
└── *_final.py     # Production-ready versions

/UPLOAD_TO_HF/      # Production deployment files
├── app.py         # Main application
├── frontend.html  # User interface
└── *.py          # Supporting modules
```

---

## 🎯 **SESSION MANAGEMENT**

### **Session Types**
- **Development**: Feature implementation and coding
- **Testing**: API integration and performance validation
- **Deployment**: Production deployment and verification
- **Planning**: Architecture design and roadmap planning
- **Documentation**: User guides and technical documentation

### **Session Documentation Requirements**
- **Start**: Document session goals and context
- **Progress**: Update status documents during work
- **End**: Summary of accomplishments and next steps
- **Handoff**: Clear instructions for next session
- **CRITICAL**: Update PROJECT_SUMMARY.md when major milestones completed
- **Version Sync**: Ensure all status files reflect same version/phase

### **File Update Protocol**
When working on the project, always update:
1. **CURRENT_PROJECT_STATUS.md** - Reflect current progress
2. **PROJECT_SUMMARY.md** - Update when major milestones achieved
3. **version.json** - Update version information
4. **Relevant documentation** - Keep docs current with code
5. **Session tracking** - Document major accomplishments
6. **MANDATORY**: Ensure version consistency across all status files

---

## 💬 **CHAT CAPACITY MANAGEMENT**

### **CRITICAL: Proactive Session Management**
**Chat sessions have limited capacity. Running out of space forces disruptive summary exercises.**

#### **Capacity Monitoring Protocol**
- **Claude should proactively monitor** conversation length and approaching limits
- **80% Warning**: Suggest summary and transition BEFORE hitting capacity limits
- **60% Checkpoint**: Begin planning natural transition points
- **90% Emergency**: Immediate summary and handoff required

#### **Capacity Warning Signals**
**Claude should announce when:**
- **First 60%**: "We're approaching mid-session capacity"
- **At 80%**: "⚠️ CAPACITY WARNING: We should plan to summarize and transition soon"
- **At 90%**: "🚨 IMMEDIATE ACTION: Must create handoff summary now"

#### **Proactive Session Management**
**When capacity warnings trigger:**
1. **Pause current work** at next natural breakpoint
2. **Create comprehensive handoff summary** while space remains
3. **Commit critical files** to git before transition
4. **Document session accomplishments** and next priorities
5. **Generate transition message** for next session

#### **Capacity-Efficient Communication**
**During high-capacity periods:**
- **Concise responses** - Essential information only
- **Bullet points** instead of paragraphs when appropriate
- **Focus on decisions** rather than explanations
- **Defer documentation** updates to next session if needed

#### **Natural Transition Points**
**Good times to transition:**
- ✅ **After code completion** - Files ready for next phase
- ✅ **Before testing phase** - Clean break between development stages
- ✅ **After git commits** - Work is saved and documented
- ✅ **End of sprint tasks** - Logical development boundaries
- ✅ **Before major architecture changes** - Fresh session for complex work

#### **Emergency Capacity Protocol**
**If approaching 95% capacity:**
1. **STOP all non-essential work immediately**
2. **Create minimal handoff summary** (essential facts only)
3. **List critical next steps** (3-5 bullet points maximum)
4. **Note current file states** and any uncommitted work
5. **End session** with clear transition instructions

### **Why This Matters for HAWKMOTH**
**Chat limitations highlight HAWKMOTH's value:**
- **Persistent development context** without artificial conversation limits
- **Continuous project state** maintained across sessions
- **No forced interruptions** for technical limitations
- **Self-contained development environment** for extended work

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
3. Read CURRENT_PROJECT_STATUS.md (current priorities)
4. Continue where previous session left off

**PROJECT LOCATION:** G:\Claud\HAWKMOTH-Project
```

**Note:** All context, accomplishments, priorities, and status information should be maintained in the respective status files, not duplicated in handoff messages.

### **Emergency Context Recovery**
If project context is completely lost:
1. **Start here**: `G:\Claud\HAWKMOTH-Project\WAYS_OF_WORKING.md`
2. **Read next**: `PROJECT_SUMMARY.md` 
3. **Then read**: `CURRENT_PROJECT_STATUS.md`
4. **Check code**: `/UPLOAD_TO_HF/` directory for latest production files
5. **Review work**: `/working/` directory for development files

---

## 📊 **PROGRESS TRACKING**

### **Status Monitoring**
- **Per Session**: Update progress and priorities
- **Per Sprint**: Review sprint goals and completion
- **Per Milestone**: Comprehensive status documentation
- **Pre-Deployment**: Complete deployment readiness checklist

### **Quality Gates**
- **Code Reviews**: All production code reviewed before `/UPLOAD_TO_HF/`
- **Testing**: Functional testing before deployment
- **Documentation**: User guides and technical docs updated
- **Performance**: Response time and cost optimization verified

### **Version Control**
```
v0.1.0-dev  → Development/Testing (Current)
v0.1.0      → LLM Teaming Stable
v0.1.1      → Enhanced Features
v0.2.0      → Enterprise Foundation
```

---

## 🚀 **DEPLOYMENT PROTOCOLS**

### **Deployment Readiness Checklist**
- [ ] Code completed and tested in `/working/`
- [ ] Production files updated in `/UPLOAD_TO_HF/`
- [ ] Documentation updated
- [ ] Version tracking updated
- [ ] Performance validated
- [ ] Error handling verified

### **Deployment Process**
1. **Code Preparation**: Finalize in `/working/`, move to `/UPLOAD_TO_HF/`
2. **Testing**: Verify all functionality works as expected
3. **Documentation**: Update user guides and API docs
4. **Deployment**: Upload to HuggingFace Space
5. **Verification**: Test live deployment and performance
6. **Release Notes**: Document new features and changes

---

## 🔗 **CRITICAL SUCCESS FACTORS**

### **Session Continuity Requirements**
1. **Always start with WAYS_OF_WORKING.md** (this file)
2. **Establish full context** before proceeding with work
3. **Update status documents** during development
4. **Document handoff information** for next session
5. **Maintain project location awareness**
6. 🚨 **MANDATORY:** Always ask user permission before any file operations or token-intensive work

### **Communication Protocols**
- **Direct answers** to direct questions - avoid unnecessary summaries
- **Concise responses** - match the user's communication style and intent
- **Save chat tokens** - don't over-explain when user asks simple status questions
- **Clear status updates** in documentation
- **Explicit handoff messages** between sessions
- **Progress tracking** in appropriate files
- **Issue documentation** for blockers and dependencies

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

*HAWKMOTH Ways of Working - Ensuring consistent development protocols and session continuity*