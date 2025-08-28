"""
Text-to-SQL Runner - Core Logic
Provides the main runner functionality for text-to-SQL workflows.
"""

import asyncio
import json
import logging
from typing import Any

from .db_tools import (
    load_eval_data,
    run_load_db_info,
    extract_db_id_from_path,
)

from .agent_interface import Agent, AgentFactory

logger = logging.getLogger(__name__)


class TextToSQLRunner:
    """Library-agnostic runner for text-to-SQL workflows."""

    def __init__(self, agent: Agent):
        """Initialize the runner with an agent.

        Args:
            agent: The agent to use for processing
        """
        self.agent = agent

    @classmethod
    def from_config(
        cls,
        agent_factory: AgentFactory,
        config_path: str,
        storage_root: str | None = None,
    ) -> "TextToSQLRunner":
        """Create a runner from configuration using an agent factory.

        Args:
            agent_factory: Factory to create the agent
            config_path: Path to the configuration file
            storage_root: Optional storage root directory

        Returns:
            Configured TextToSQLRunner instance
        """
        agent = agent_factory.create_agent(config_path, storage_root)
        return cls(agent)

    async def run(
        self,
        eval_path: str,
        db_root_path: str,
        question_index: int | None,
        sql_dialect: str = "SQLite",
        max_concurrent: int = 5,
    ) -> Any:
        eval_data: dict = load_eval_data(eval_path, db_root_path, sql_dialect)
        if question_index is not None:
            return await self._run_one(eval_data, question_index, sql_dialect)
        else:
            return await self._run_all(eval_data, eval_path, sql_dialect, max_concurrent)

    async def _run_one(
        self, eval_data: dict, question_index: int, sql_dialect: str = "SQLite"
    ) -> dict:
        total_questions = len(eval_data["question_list"])
        if question_index >= total_questions:
            raise IndexError(
                f"Question index {question_index} out of range (0-{total_questions - 1})"
            )

        question = eval_data["question_list"][question_index]
        db_path = eval_data["db_path_list"][question_index]
        external_knowledge = eval_data["knowledge_list"][question_index]
        db_path_list = eval_data["db_path_list"]
        db_path = db_path_list[question_index]
        db_id = extract_db_id_from_path(db_path)
        db_info = run_load_db_info(db_path)
        schema_info = db_info["schema_info"]
        table_descriptions = db_info["table_descriptions"]
        db_config = {
            "db_path": db_path,
            "db_id": db_id,
            "sql_dialect": sql_dialect,
        }

        task_data = {
            "question": question,
            "external_knowledge": external_knowledge,
            "db_id": db_id,
            "table_descriptions": table_descriptions,
            "schema_info": schema_info,
            "sql_dialect": sql_dialect,
            "db_config": db_config,
        }

        try:
            result = await self.agent.ainvoke(task_data)
            return result
        except Exception as e:
            logger.error(f"Error running single question: {e}", exc_info=True)
            raise

    async def _run_all(
        self,
        eval_data: dict,
        eval_path: str,
        sql_dialect: str = "SQLite",
        max_concurrent: int = 5,
    ) -> dict:
        """Run text-to-SQL on all questions in the evaluation file concurrently.

        Args:
            eval_path: Path to evaluation JSON file
            db_root_path: Root path for database files
            sql_dialect: SQL dialect to use
            json_file_path: Path to JSON file for schema descriptions
            max_concurrent: Maximum number of concurrent tasks

        Returns:
            Dictionary containing results for all questions in the specified format
        """
        # Read all questions from the evaluation file
        try:
            with open(eval_path, "r") as f:
                questions = json.load(f)
        except Exception as e:
            logger.error(f"Error reading evaluation file: {e}", exc_info=True)
            raise

        async def process_question(i: int, question: dict) -> tuple[int, str]:
            try:
                logger.info(
                    f"Processing question {i}: {question.get('question', 'N/A')}"
                )
                final_sql = await self._run_one(eval_data, i, sql_dialect)
                return i, final_sql
            except Exception as e:
                logger.error(f"Error processing question {i}: {e}", exc_info=True)
                return i, "Error"

        # Create semaphore to limit concurrent tasks
        semaphore = asyncio.Semaphore(max_concurrent)

        async def bounded_process(i: int, question: dict) -> tuple[int, str]:
            async with semaphore:
                return await process_question(i, question)

        # Create tasks for all questions
        tasks = [bounded_process(i, question) for i, question in enumerate(questions)]

        # Execute all tasks concurrently and collect results
        results = {}
        for task in asyncio.as_completed(tasks):
            i, result = await task
            results[i] = result
            logger.info(f"Completed question {i}")

        return dict(sorted(results.items()))
