import asyncio
from typing import Dict, Any
import openai
from bird_runner import Agent
from .utils import build_prompt


class OpenAIAgent(Agent):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = openai.AsyncOpenAI(
            api_key=config["openai"]["api_key"]
        )
        
    async def ainvoke(self, state: Dict[str, Any]) -> str:
        """
        Process the state and return the final SQL query.
        
        Args:
            state: Dictionary containing:
                - question: SQL question text
                - external_knowledge: Expert annotations
                - db_id: database name
                - table_descriptions: markdown table descriptions
                - schema_info: database DDL
                - sql_dialect: SQL dialect (e.g., "SQLite")
                - db_config: database configuration
        
        Returns:
            str: Generated SQL query
        """
        try:
            # Build the prompt from state
            system_message = self.config["prompt"]["system_message"]
            user_message = build_prompt(state)
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.config["openai"]["model"],
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=self.config["openai"]["temperature"],
                max_tokens=self.config["openai"]["max_tokens"]
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up the SQL (remove markdown formatting if present)
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.startswith("```"):
                sql_query = sql_query[3:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
                
            return sql_query.strip()
            
        except Exception as e:
            print(f"Error generating SQL: {e}")
            return "SELECT 1;"  # Fallback query