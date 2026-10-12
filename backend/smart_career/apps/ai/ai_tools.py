"""AI Tool definitions and handlers"""

AI_TOOLS = [
    {
        "name": "search_candidates",
        "description": "Search for candidates matching criteria",
        "requires_approval": False,
        "parameters": {
            "search_query": "Natural language search query",
            "filters": "Optional filters (age, experience, passport_valid, etc.)",
        }
    },
    {
        "name": "get_candidate",
        "description": "Get detailed candidate information",
        "requires_approval": False,
        "parameters": {
            "candidate_id": "Candidate ID",
        }
    },
    {
        "name": "search_jobs",
        "description": "Search for job openings",
        "requires_approval": False,
        "parameters": {
            "search_query": "Job search query",
            "country": "Optional country filter",
        }
    },
    {
        "name": "find_matching_candidates",
        "description": "Find candidates matching a specific job",
        "requires_approval": False,
        "parameters": {
            "job_id": "Job ID",
            "limit": "Number of results (default: 10)",
        }
    },
    {
        "name": "find_expiring_documents",
        "description": "Find candidates with expiring documents",
        "requires_approval": False,
        "parameters": {
            "document_type": "Type of document (passport, visa, medical, etc.)",
            "days": "Documents expiring within N days",
        }
    },
    {
        "name": "find_pending_visas",
        "description": "Find visas pending approval",
        "requires_approval": False,
        "parameters": {
            "days_pending": "Pending for more than N days",
        }
    },
    {
        "name": "get_candidate_financial_summary",
        "description": "Get financial summary for a candidate",
        "requires_approval": False,
        "parameters": {
            "candidate_id": "Candidate ID",
        }
    },
    {
        "name": "generate_cv",
        "description": "Generate CV for a candidate",
        "requires_approval": False,
        "parameters": {
            "candidate_id": "Candidate ID",
            "job_id": "Optional job to tailor CV to",
            "language": "Language (English, Bengali, etc.)",
        }
    },
    {
        "name": "create_task",
        "description": "Create a new task",
        "requires_approval": False,
        "parameters": {
            "title": "Task title",
            "description": "Task description",
            "candidate_id": "Optional candidate ID",
            "due_date": "Due date (YYYY-MM-DD)",
            "priority": "CRITICAL, HIGH, MEDIUM, LOW",
        }
    },
    {
        "name": "get_candidate_summary",
        "description": "Get AI-generated summary of candidate",
        "requires_approval": False,
        "parameters": {
            "candidate_id": "Candidate ID",
        }
    },
]


def get_tool_by_name(tool_name):
    """Get tool definition by name"""
    for tool in AI_TOOLS:
        if tool['name'] == tool_name:
            return tool
    return None


def is_sensitive_tool(tool_name):
    """Check if tool requires approval"""
    tool = get_tool_by_name(tool_name)
    return tool and tool.get('requires_approval', False) if tool else False