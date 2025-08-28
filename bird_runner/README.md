# Bird Runner

## Usage

### Installation

``` sh
pip install git+https://github.com/bsbds/bird-txt2sql-tools.git#subdirectory=bird_runner
```

### Implement Agent Interface

You  will implements the `Agent` and `AgentFactory` class. 

An `Agent` should accept a state dict when invoked:
- "question": the sql question text. 
- "external_knowledge": the external knowledge evidence annotated by experts for assistance of models or SQL annotators.
- "db_id": the database name
- "table_descriptions": a description in markdown table format for the db tables
- "schema_info": schema DDL of the database
- "sql_dialect": the dialect (currently support only "SQLite")
- "db_config": a dict containing the database configurations (TODO: merge these duplicate fields with above)
    - "db_path": the path to the sqlite database file
    - "db_id": the database name (Duplicate)
    - "sql_dialect": the dialect (currently support only "SQLite") (Duplicate)


Example code:
``` python
from bird_sql_runner import Agent, AgentFactory, TextToSQLCLI

class CustomAgent(Agent):
    def __init__(self, config):
        self.config = config

    async def ainvoke(self, state: dict):
        # Process the state and return the final sql
        final_sql = await self.process(state)
        return final_sql


class CustomAgentFactory(AgentFactory):
    def create_agent(self, config_path, storage_root=None):
        config = load_config(config_path)
        return CustomAgent(config)


def main():
    cli = TextToSQLCLI()
    cli.register_agent("custom-agent", CustomAgentFactory())
    cli.run()


if __name__ == "__main__":
    main()
```

Check `examples/openai_agent` for a complete example.

### Run the agent

- Run single question
``` sh
python -m your_custom_agent --config your_agent_config --eval-path bird-txt2sql-tools/mini_dev_sqlite_subset.json --db-root-path bird-txt2sql-tools/dev_databases --json-file-path=bird-txt2sql-tools/database_description.json --output=bird-txt2sql-tools/output.json --max-concurrent 10 --question-index 18 --agent-type custom-agent
```

- Run all questions
``` sh
python -m your_custom_agent --config your_agent_config --eval-path bird-txt2sql-tools/mini_dev_sqlite_subset.json --db-root-path bird-txt2sql-tools/dev_databases --json-file-path=bird-txt2sql-tools/database_description.json --output=bird-txt2sql-tools/output.json --all --agent-type custom-agent
```

Note:
- Replace `your_custom_agent` with your agent module.
- Replace all `bird-txt2sql-tools/***` with the path to your cloned `bird-txt2sql-tools` project.
- Replace `custom-agent` with your registered agent name.


- Optional Arguments
- --config: Path to your custom agent configuration file
- --max-concurrent: Number of concurrent executions of questions (default: 5)

This will place an `output.json` file in the path to your cloned `bird-text2sql-tools` project. Then you can proceed to the evaluation section.
