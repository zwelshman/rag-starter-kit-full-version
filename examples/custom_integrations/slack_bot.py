"""
Slack Bot Integration for RAG Starter Kit Pro
Enables RAG queries via Slack messages.
"""

import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Import RAG components
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.retrieval_engine import create_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Slack app
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Initialize RAG pipeline
pipeline = None


def get_pipeline():
    """Get or create RAG pipeline."""
    global pipeline
    if pipeline is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        pipeline = create_pipeline(api_key=api_key)
    return pipeline


@app.event("app_mention")
def handle_mention(event, say):
    """Handle when bot is mentioned."""
    user = event["user"]
    text = event["text"]

    # Remove bot mention from text
    query = text.split(">", 1)[-1].strip()

    if not query:
        say(f"<@{user}> Please ask a question after mentioning me!")
        return

    try:
        say(f"<@{user}> Let me search for that... :mag:")

        # Query RAG pipeline
        rag = get_pipeline()
        response = ""
        for token in rag.query_stream(query):
            response += token

        # Format response
        say(f"<@{user}>\n\n{response}")

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        say(f"<@{user}> Sorry, I encountered an error: {str(e)}")


@app.command("/ask")
def handle_ask_command(ack, respond, command):
    """Handle /ask slash command."""
    ack()

    query = command["text"]
    if not query:
        respond("Please provide a question: `/ask your question here`")
        return

    try:
        respond("Searching... :mag:")

        rag = get_pipeline()
        response = ""
        for token in rag.query_stream(query):
            response += token

        respond(response)

    except Exception as e:
        logger.error(f"Error processing command: {e}")
        respond(f"Error: {str(e)}")


@app.command("/rag-status")
def handle_status_command(ack, respond, command):
    """Check RAG pipeline status."""
    ack()

    try:
        rag = get_pipeline()
        stats = rag.get_stats()

        status_message = f"""
:robot_face: *RAG Pipeline Status*
• Documents: {stats.get('document_count', 0)}
• Chunks: {stats.get('chunk_count', 0)}
• Vector Store: {stats.get('vector_store', 'Unknown')}
• LLM Provider: {stats.get('llm_provider', 'Unknown')}
        """
        respond(status_message)

    except Exception as e:
        respond(f"Error getting status: {str(e)}")


def main():
    """Run the Slack bot."""
    handler = SocketModeHandler(
        app,
        os.environ.get("SLACK_APP_TOKEN")
    )
    logger.info("Starting Slack bot...")
    handler.start()


if __name__ == "__main__":
    main()


"""
Setup Instructions:

1. Create a Slack App at api.slack.com/apps

2. Enable Socket Mode and get App Token

3. Add Bot Token Scopes:
   - app_mentions:read
   - chat:write
   - commands

4. Install the app to your workspace

5. Set environment variables:
   export SLACK_BOT_TOKEN="xoxb-..."
   export SLACK_APP_TOKEN="xapp-..."
   export ANTHROPIC_API_KEY="sk-ant-..."

6. Install dependencies:
   pip install slack-bolt

7. Run the bot:
   python slack_bot.py

8. Invite the bot to a channel and mention it!
"""
