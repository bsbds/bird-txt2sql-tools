"""CLI interface for text-to-SQL workflows."""

import argparse
import asyncio
import json
import logging
import sys
from typing import Dict, Optional

from .agent_interface import AgentFactory
from .runner import TextToSQLRunner


class TextToSQLCLI:
    """CLI interface for text-to-SQL workflows."""

    def __init__(self):
        self.agent_factories: Dict[str, AgentFactory] = {}

    def register_agent(self, name: str, factory: AgentFactory):
        """Register an agent factory."""
        self.agent_factories[name] = factory

    def run(self):
        """Run the CLI."""
        asyncio.run(self._async_main())

    async def _async_main(self):
        """Async main CLI entry point."""
        parser = argparse.ArgumentParser(description="Text-to-SQL Runner")

        # Required arguments
        parser.add_argument(
            "--config", required=False, help="Path to agent configuration file"
        )
        parser.add_argument(
            "--agent-type",
            required=True,
            choices=list(self.agent_factories.keys()),
            help="Type of agent to use",
        )
        parser.add_argument(
            "--eval-path", required=True, help="Path to evaluation JSON file"
        )
        parser.add_argument(
            "--question-index",
            type=int,
            help="Index of specific question to process (mutually exclusive with --all)",
        )
        parser.add_argument(
            "--max-concurrent",
            type=int,
            default=5,
            help="Max concurrent questions",
        )

        parser.add_argument(
            "--all",
            action="store_true",
            help="Process all questions in the evaluation file (mutually exclusive with --question-index)",
        )

        # Database configuration
        parser.add_argument(
            "--db-root-path", required=True, help="Root path for database files"
        )
        parser.add_argument(
            "--json-file-path",
            required=True,
            help="JSON file path for schema descriptions",
        )

        # Processing options
        parser.add_argument(
            "--sql-dialect",
            default="SQLite",
            choices=["SQLite", "MySQL", "PostgreSQL"],
            help="SQL dialect to use",
        )
        parser.add_argument("--output", help="Output file path for results")
        parser.add_argument("--storage-root", help="Storage root directory")

        # Logging
        parser.add_argument(
            "--log-level",
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            help="Logging level",
        )

        args = parser.parse_args()

        # Check for mutually exclusive arguments
        args_present = sum([args.question_index is not None, args.all])
        if args_present != 1:
            parser.error("Exactly one of --question-index or --all is required")

        # Set up logging
        logging.basicConfig(
            level=getattr(logging, args.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        try:
            # Get agent factory
            agent_factory = self.agent_factories[args.agent_type]

            # Initialize runner
            runner = TextToSQLRunner.from_config(
                agent_factory, args.config, args.storage_root
            )

            if args.all:
                logging.info("Running all questions")
                results = await runner.run(
                    args.eval_path,
                    args.db_root_path,
                    question_index=None,
                    sql_dialect=args.sql_dialect,
                    max_concurrent=args.max_concurrent,
                )

                results_json = json.dumps(results, indent=2)
                # Write results to output file if specified
                if args.output:
                    with open(args.output, "w") as f:
                        f.write(results_json)
                    logging.info(f"Results written to {args.output}")

                print(results_json)
            else:
                logging.info(f"Running single question {args.question_index}")
                final_sql = await runner.run(
                    args.eval_path,
                    args.db_root_path,
                    question_index=args.question_index,
                    sql_dialect=args.sql_dialect,
                    max_concurrent=args.max_concurrent,
                )

                print(f"final sql: {final_sql}")

        except Exception as e:
            logging.error(f"Error running text-to-SQL: {e}", exc_info=True)
            sys.exit(1)
