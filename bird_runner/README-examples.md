# Examples

This directory contains example implementations of agents for the Bird SQL Runner.

## OpenAI Agent Example

This example demonstrates how to create a Bird SQL agent using OpenAI's API.

### Setup

1. Install additional dependencies:
```bash
pip install -r requirements-example.txt
```

2. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_BASE_URL="your-custom-endpoint"
export OPENAI_MODEL="your-custom-model"
```

### Usage

Run a single question:
```sh
python -m examples.openai_agent \
    --config examples/openai_agent/config.yaml \
    --eval-path ../mini_dev_sqlite_subset.json \
    --db-root-path ../dev_databases \
    --json-file-path ../database_description.json \
    --output ../output.json \
    --question-index 0 \
    --agent-type openai-agent
```

Run all questions:
```sh
python -m examples.openai_agent \
    --config examples/openai_agent/config.yaml \
    --eval-path ../mini_dev_sqlite_subset.json \
    --db-root-path ../dev_databases \
    --json-file-path ../database_description.json \
    --output ../output.json \
    --all \
    --agent-type openai-agent
```

### Configuration

Modify `examples/openai_agent/config.yaml` to:
- Change the OpenAI model
- Adjust temperature and max_tokens
- Customize the system prompt
