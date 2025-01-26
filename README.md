# Local AI Agent for Shortcut and Notion Integration

This project is a Python-based local AI agent designed to:
1. Fetch bug tickets from Shortcut.
2. Summarize ticket details and associated comments using a locally hosted AI model.
3. Extract potential solutions from comments.
4. Populate a Notion database with summarized information and solutions.

## Features
- Fully local AI processing for summarization and solution extraction.
- Integration with Shortcut API to fetch tickets and comments.
- Integration with Notion API to store summarized tickets in a database.
- Privacy-focused: No external API calls for AI.

---

## Prerequisites

### 0. **Python**
This project requires Python 3.8 or higher. You can download Python from the [official website](https://www.python.org/downloads/).
Poetry is used for dependency management. You can install it using pip:
```bash
pip install poetry
```

### 1. **API Keys**
Obtain the following API tokens:
- Shortcut API token: [Generate Shortcut API Token](https://app.shortcut.com/settings/api-tokens)
- Notion API token: [Get Notion API Key](https://www.notion.so/my-integrations)

### 2. **Environment Variables**
Create a `.env` file in the project root directory with the following variables:

```dotenv
# .env file for the AI agent

# Shortcut API token
SHORTCUT_API_KEY=<your-shortcut-api-key>

# Notion API token
NOTION_API_KEY=<your-notion-api-key>

# Optional: OpenAI API key (if using OpenAI for summarization)
OPENAI_API_KEY=<your-openai-api-key>

# Notion database ID for storing ticket data
NOTION_DATABASE_ID=<your-database-id>
```

---
## Build
Install poetry and dependencies:
```bash
poetry install
```

---
## Known Limitations

---

## Future Improvements
- Create a Dockerfile for easy deployment.
- Create a make file for easy setup and deployment.
---

## License
This project is open-source and available under the MIT License.

