# Simple Visual Architecture Diagram

## 🎨 For Visual Diagram Creation

You can use this simplified structure in tools like:
- **Draw.io (diagrams.net)** - Free online diagramming tool
- **Lucidchart** - Professional diagramming platform
- **Microsoft Visio** - Enterprise diagramming software
- **Canva** - Easy design tool with architecture templates

### Simple 4-Layer Architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    USER LAYER                               │
│  [Desktop Browser] [Mobile Browser] [API Clients]          │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/HTTPS
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 APPLICATION LAYER                           │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                Flask Web Server                         ││
│  │  [/] [/api/chat] [/api/status] [/api/new-conv]         ││
│  │                                                         ││
│  │  [Session Management] [Template Engine]                ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────┬───────────────────────────────────┘
                          │ Azure SDK
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   AZURE AI LAYER                           │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              Azure AI Foundry                           ││
│  │  [AI Project] [Agents] [Threads] [Messages]            ││
│  │                                                         ││
│  │  [Car Repair AI Agent] [Knowledge Base]                ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────┬───────────────────────────────────┘
                          │ Document Retrieval
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   STORAGE LAYER                             │
│  [Azure Data Lake] [Car Manuals] [Technical Docs]          │
│  [Search Indexes] [Knowledge Base] [Document Store]        │
└─────────────────────────────────────────────────────────────┘
```

### Component Relationships:

**Frontend to Backend:**
- User Interface ↔ Flask Routes ↔ Session Management

**Backend to Azure:**
- Flask App ↔ Azure Authentication ↔ AI Foundry Client

**AI Processing:**
- AI Agent ↔ Knowledge Base ↔ Document Storage

**Data Flow:**
- User Input → Flask → Azure AI → Knowledge Search → AI Response → User

### Key Technologies by Layer:

1. **User Layer:** HTML5, CSS3, JavaScript, Responsive Design
2. **Application Layer:** Python, Flask, Jinja2, Session Management
3. **Azure AI Layer:** AI Foundry, Agents API, Search Services
4. **Storage Layer:** Azure Data Lake, Document Indexing, Search Indexes

### Security Flow:

```
User Request → HTTPS → Flask (Session) → Azure Auth → AI Foundry → Secure Storage
```

### Deployment Options:

```
Development: Local Python + Flask Dev Server
Production:  Azure App Service | Docker Container | Kubernetes
```
