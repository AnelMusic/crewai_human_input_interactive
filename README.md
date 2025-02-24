
# Interactive Human-AI Chat with CrewAI

## Overview

This script creates a conversational AI assistant that collects personal information through natural dialogue. Using CrewAI's agent framework and Chainlit's user interface, it demonstrates how to build interactive AI systems that gather specific information while maintaining a natural conversation flow.

## How It Works

When a user sends a message, two specialized AI agents work together:

- **Information Collector**: Asks follow-up questions to gather name and location details
- **Information Summarizer**: Transforms collected data into a natural, friendly summary

## Key Features

- Natural back-and-forth conversation with AI
- Dynamic follow-up questions when more context is needed
- Friendly web interface using Chainlit
- Structured information collection in a conversational format

## Requirements

- OpenAI API key (add to .env file)
- Python packages: crewai, chainlit, pydantic

## Running the Demo

```bash
chainlit run ./crewai_chainlit_human_input.py
```

This example demonstrates how AI systems can be made more interactive by combining structured task workflows with natural human conversation.
