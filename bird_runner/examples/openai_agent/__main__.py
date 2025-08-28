from bird_runner import TextToSQLCLI
from .factory import OpenAIAgentFactory


def main():
    cli = TextToSQLCLI()
    cli.register_agent("openai-agent", OpenAIAgentFactory())
    cli.run()


if __name__ == "__main__":
    main()