# NLP Command Automation

A sophisticated Natural Language Processing system that converts natural language commands into shell commands with built-in safety mechanisms and comprehensive audit logging.

## Overview

This system processes natural language input through a multi-stage pipeline:

1. **Natural Language Understanding (NLU)** - Intent classification and entity extraction
2. **Command Mapping** - Converts intents + entities to platform-specific shell commands
3. **Safety Layer** - Risk assessment and confirmation requirements
4. **Audit Logging** - Complete interaction tracking

## Features

### Core Capabilities
- **Multi-Intent Support**: 17 different command intents (file operations, navigation, process management, etc.)
- **Cross-Platform**: Generates commands for both Windows (`nt`) and Unix-like (`posix`) systems
- **Safety-First**: Multi-level risk assessment (LOW, MEDIUM, HIGH, CRITICAL)
- **Rich Training Data**: 1400+ labeled training phrases with template-based generation
- **Real-time Web Interface**: Interactive dashboard for testing and demonstration
- **Comprehensive API**: RESTful endpoints for integration

### Supported Intents
- **File Operations**: delete, copy, move, list, read, create directories
- **Navigation**: change directory, show current directory
- **Process Management**: list processes, kill processes
- **System Information**: get system details
- **Search**: grep text search, find files
- **Network**: ping hosts
- **Environment**: show environment variables
- **Help**: assistance commands

## Architecture

```
NLP Project/
|
+-- app/                          # Main application code
|   +-- main.py                   # FastAPI application & API endpoints
|   +-- config.py                 # Configuration management
|   +-- logging_config.py         # Audit logging setup
|   |
|   +-- nlu/                      # Natural Language Understanding
|   |   +-- pipeline.py           # NLU processing pipeline
|   |   +-- classifier.py         # Intent classification
|   |   +-- entity_extractor.py   # Entity extraction
|   |   +-- intents.py            # Intent definitions
|   |   +-- training_corpus.py    # Training data generation
|   |
|   +-- command_mapping/          # Command generation
|   |   +-- mapper.py             # Intent to shell command mapping
|   |
|   +-- safety/                   # Safety & risk assessment
|       +-- layer.py              # Risk evaluation logic
|
+-- templates/
|   +-- dashboard.html            # Web interface (751 lines)
|
+-- static/
|   +-- styles.css                # Dashboard styling
|
+-- logs/                         # Audit logs (created at runtime)
+-- .venv/                        # Virtual environment
+-- requirements.txt              # Python dependencies
+-- run_server.bat               # Windows startup script
+-- README.md                     # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows or Unix-like operating system

### Setup Steps

1. **Clone or download the project** to `d:\NLP Project`

2. **Create and activate virtual environment**:
   ```bash
   cd "d:\NLP Project"
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Unix/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Dependencies
```
fastapi>=0.109.0          # Web framework
uvicorn[standard]>=0.27.0 # ASGI server
pydantic>=2.5.0           # Data validation
pydantic-settings>=2.1.0  # Configuration management
scikit-learn>=1.3.0       # Machine learning
numpy>=1.24.0             # Numerical computing
python-multipart>=0.0.6   # Form data handling
```

## Quick Start

### Option 1: Windows (Recommended)
Double-click `run_server.bat` - this handles everything automatically.

### Option 2: Manual Start
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

**Important**: Run from the project root (`d:\NLP Project`) so the dashboard template is found.

### Access the Application
- **Web Interface**: http://127.0.0.1:8765
- **API Documentation**: http://127.0.0.1:8765/docs
- **Health Check**: http://127.0.0.1:8765/api/health

## Usage Examples

### Web Interface
Try these natural language commands:
- `"delete file notes.txt"`
- `"list files in current directory"`
- `"show me all processes"`
- `"navigate to Documents folder"`
- `"copy report.pdf to backup folder"`

### API Usage

#### NLU Only
```bash
curl -X POST "http://127.0.0.1:8765/api/interpret" \
  -H "Content-Type: application/json" \
  -d '{"text": "list files in current directory"}'
```

#### Full Pipeline
```bash
curl -X POST "http://127.0.0.1:8765/api/command" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "delete file notes.txt",
    "target_os": "nt",
    "user_confirmed": false
  }'
```

## API Reference

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Web dashboard interface |
| POST | `/api/interpret` | NLU processing only (intent + entities) |
| POST | `/api/command` | Full pipeline (NLU + mapping + safety) |
| GET | `/api/health` | Health check |
| GET | `/api/debug-paths` | Debug file path resolution |

### Request/Response Models

#### InterpretRequest
```json
{
  "text": "list files in current directory"
}
```

#### CommandRequest
```json
{
  "text": "delete file notes.txt",
  "target_os": "nt",  // "nt" (Windows) or "posix" (Unix)
  "user_confirmed": false
}
```

#### CommandResponse
```json
{
  "intent": "file_list",
  "confidence": 0.95,
  "entities": {...},
  "command": "dir",
  "commands": ["dir"],
  "explanation": "List directory contents",
  "ambiguous": false,
  "risk_level": "low",
  "requires_confirmation": false,
  "approved_for_display": true
}
```

## Safety System

### Risk Levels
- **LOW**: Read-only operations (list, read, navigate)
- **MEDIUM**: Potentially impactful (move, system info)
- **HIGH**: Destructive operations (delete, kill process)
- **CRITICAL**: System-altering commands (rm -rf, sudo, format)

### Safety Patterns
The system automatically detects dangerous patterns:
- Recursive force deletes (`rm -rf`)
- Privilege escalation (`sudo`)
- Disk formatting operations
- System shutdown/reboot
- Device redirections

### Confirmation Flow
1. User submits natural language command
2. System assesses risk level
3. High-risk operations require explicit confirmation
4. Commands are never executed automatically - only generated for review

## Training and Customization

### Adding New Commands
Edit `app/nlu/training_corpus.py` to add training phrases:

```python
# Add new phrases for existing intents
def _corpus_file_list():
    v = [
        "list files",
        "show directory",  # Add your custom phrase
        # ... existing phrases
    ]
```

### Adding New Intents
1. Define intent in `app/nlu/intents.py`
2. Add training phrases in `app/nlu/training_corpus.py`
3. Create command mapping in `app/command_mapping/mapper.py`
4. Set safety level in `app/safety/layer.py`

### Model Retraining
The system automatically retrains when you:
- Edit training corpus
- Restart the server
- Modify intent definitions

## Configuration

### Environment Variables
Set these with `NCA_` prefix:

```bash
NCA_INTENT_CONFIDENCE_THRESHOLD=0.28
NCA_LOG_DIR=logs
NCA_LOG_FILE=audit.log
```

### Configuration File
Create `.env` file in project root:
```env
NCA_INTENT_CONFIDENCE_THRESHOLD=0.30
NCA_LOG_DIR=custom_logs
```

## Logging and Auditing

### Audit Logs
All interactions are logged to `logs/audit.log` in JSON format:
```json
{
  "ts": "2024-01-15T10:30:45.123Z",
  "endpoint": "/api/command",
  "input": "delete file notes.txt",
  "intent": "file_delete",
  "confidence": 0.89,
  "command": "del \"notes.txt\"",
  "risk": "high",
  "requires_confirmation": true
}
```

### Log Rotation
Logs append indefinitely - implement rotation as needed for production use.

## Troubleshooting

### Common Issues

#### Dashboard Not Loading
1. Check: http://127.0.0.1:8765/api/debug-paths
2. Ensure `dashboard_exists` is `true`
3. If `false`, restart from correct directory

#### Port Conflicts
- Port 8000 often blocked on Windows (Hyper-V)
- Default port 8765 chosen for compatibility
- Change port in `run_server.bat` or command line

#### Training Issues
- Verify training corpus syntax in `app/nlu/training_corpus.py`
- Check intent definitions match between files
- Restart server after modifications

#### Performance
- Initial startup may be slow (model training)
- Subsequent requests are fast (cached models)
- Memory usage: ~50-100MB for ML models

## Development

### Project Structure
- **Modular Design**: Clear separation of concerns
- **Type Safety**: Full type hints throughout
- **Testing Ready**: Structure supports unit testing
- **Extensible**: Easy to add new intents and platforms

### Code Quality
- **Documentation**: Comprehensive docstrings
- **Error Handling**: Graceful failure modes
- **Logging**: Structured audit trails
- **Configuration**: Environment-based settings

## Security Considerations

- **No Command Execution**: Server only generates commands
- **Input Validation**: All inputs validated via Pydantic
- **Risk Assessment**: Multi-layer safety checks
- **Audit Trail**: Complete interaction logging
- **Local Only**: Designed for localhost use

## License and Contributing

This is a demonstration project showcasing NLP-to-command conversion with safety mechanisms. Feel free to:
- Extend with new intents
- Add platform support
- Improve training data
- Enhance safety rules

## Version History

- **v1.0.0**: Initial release with core NLU pipeline, safety layer, and web interface
