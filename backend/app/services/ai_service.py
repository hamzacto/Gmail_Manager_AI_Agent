from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import StructuredTool
from typing import Dict, Any, List
from pydantic import BaseModel
from ..core.config import settings

class SendEmailSchema(BaseModel):
    to: str
    subject: str
    body: str

class FetchEmailsSchema(BaseModel):
    limit: int

class AIService:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL_NAME,
            temperature=settings.GROQ_TEMPERATURE,
            max_tokens=settings.GROQ_MAX_TOKENS
        )
        
    def _create_send_email_tool(self, gmail_service) -> StructuredTool:
        async def send_email(to: str, subject: str, body: str) -> str:
            result = await gmail_service.send_email(to=to, subject=subject, body=body)
            return f"Email sent successfully: {result}"
            
        return StructuredTool.from_function(
            name="send_email",
            description="Use this tool to send an email. Requires recipient email address (to), subject line, and email body.",
            func=send_email,
            args_schema=SendEmailSchema,
            coroutine=send_email
        )
        
    def _create_fetch_emails_tool(self, gmail_service) -> StructuredTool:
        async def fetch_emails(limit: int) -> str:
            emails = await gmail_service.get_recent_emails(limit)
            email_list = []
            for i, email in enumerate(emails, 1):
                email = email or {}
                if 'payload' in email:
                    headers = email.get("payload", {}).get("headers", [])
                    subject = next(
                        (h.get("value") for h in headers if isinstance(h, dict) and h.get("name", "").lower() == "subject"),
                        email.get("subject", "No Subject")
                    )
                    sender = next(
                        (h.get("value") for h in headers if isinstance(h, dict) and h.get("name", "").lower() == "from"),
                        email.get("sender", "Unknown")
                    )
                else:
                    subject = email.get("subject", "No Subject")
                    sender = email.get("sender", "Unknown")
                snippet = email.get("snippet", "No preview available")
                
                email_list.append(
                    f"\n{i}. From: {sender}\n"
                    f"   Subject: {subject}\n"
                    f"   Snippet: {snippet}\n"
                )
            
            return f"Here are your {len(emails)} most recent emails:\n{''.join(email_list)}"
            
        return StructuredTool.from_function(
            name="fetch_emails",
            description="Use this tool to fetch recent emails. Requires a number limit of emails to fetch.",
            func=fetch_emails,
            args_schema=FetchEmailsSchema,
            coroutine=fetch_emails
        )
        
    async def interpret_command(self, command: str, gmail_service) -> Dict[str, Any]:
        tools = [
            self._create_send_email_tool(gmail_service),
            self._create_fetch_emails_tool(gmail_service)
        ]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI email assistant that helps users manage their emails.
You have access to two tools:
1. send_email - For sending emails (requires 'to' email address, subject, and body)
2. fetch_emails - For fetching recent emails (requires a number limit)

When sending emails, make sure to write a complete and appropriate message based on the user's request."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_tools_agent(self.llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        try:
            result = await agent_executor.ainvoke(
                {
                    "input": command,
                    "chat_history": []
                }
            )
            return result
        except Exception as e:
            raise ValueError(f"Failed to execute command: {str(e)}")
        
    async def generate_draft(self, context: str, recipient: str = None) -> Dict[str, str]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an email assistant. Generate a professional email based on the context.
            Format your response exactly like this:
            SUBJECT: <subject line>
            ---
            <email body>
            
            Do not include any other metadata like 'To:', 'From:', or 'Send to:' in the response."""),
            ("user", "{context}")
        ])
        
        chain = prompt | self.llm
        result = await chain.ainvoke({"context": context})
        
        content = result.content
        # Split on the first occurrence of "---"
        parts = content.split("---", 1)
        
        if len(parts) != 2:
            raise ValueError("Invalid email format from AI")
        
        subject = parts[0].replace("SUBJECT:", "").strip()
        body = parts[1].strip()
        
        return {
            "subject": subject,
            "body": body
        }
        
    def _parse_command_result(self, result: str) -> Dict[str, Any]:
        """Parse the LLM output into structured action data."""
        try:
            # Basic parsing of common commands
            result = result.lower().strip()
            
            if "fetch" in result or "get" in result:
                return {
                    "type": "fetch_emails",
                    "params": {
                        "limit": 10  # default limit
                    }
                }
            elif "send" in result:
                # Extract recipient, subject, and body from the result
                # This is a simplified version - you might want to use more sophisticated parsing
                return {
                    "type": "send_email",
                    "params": {
                        "recipient": "",  # Extract from result
                        "subject": "",    # Extract from result
                        "body": ""        # Extract from result
                    }
                }
            else:
                return {
                    "type": "unknown",
                    "params": {}
                }
        except Exception as e:
            return {
                "type": "error",
                "params": {"error": str(e)}
            } 