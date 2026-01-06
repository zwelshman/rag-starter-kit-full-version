"""
Discord Bot Integration for RAG Starter Kit Pro
Enables RAG queries via Discord messages.
"""

import os
import sys
import logging
import discord
from discord import app_commands
from discord.ext import commands

# Add parent path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.retrieval_engine import create_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Global pipeline
pipeline = None


def get_pipeline():
    """Get or create RAG pipeline."""
    global pipeline
    if pipeline is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        pipeline = create_pipeline(api_key=api_key)
    return pipeline


@bot.event
async def on_ready():
    """Called when bot is ready."""
    logger.info(f"Bot is ready! Logged in as {bot.user}")

    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")


@bot.tree.command(name="ask", description="Ask a question to the RAG system")
@app_commands.describe(question="Your question")
async def ask(interaction: discord.Interaction, question: str):
    """Slash command to ask a question."""
    await interaction.response.defer(thinking=True)

    try:
        rag = get_pipeline()

        # Generate response
        response = ""
        for token in rag.query_stream(question):
            response += token

        # Truncate if too long for Discord
        if len(response) > 1900:
            response = response[:1900] + "..."

        await interaction.followup.send(f"**Question:** {question}\n\n**Answer:** {response}")

    except Exception as e:
        logger.error(f"Error: {e}")
        await interaction.followup.send(f"Error: {str(e)}")


@bot.tree.command(name="search", description="Search documents without generating a response")
@app_commands.describe(query="Your search query")
async def search(interaction: discord.Interaction, query: str):
    """Slash command to search documents."""
    await interaction.response.defer(thinking=True)

    try:
        rag = get_pipeline()
        results = rag.search(query, n_results=3)

        embed = discord.Embed(
            title=f"Search Results: {query}",
            color=discord.Color.blue()
        )

        for i, result in enumerate(results, 1):
            content = result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"]
            source = result["metadata"].get("source", "Unknown")
            embed.add_field(
                name=f"Result {i} - {source}",
                value=content,
                inline=False
            )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        logger.error(f"Error: {e}")
        await interaction.followup.send(f"Error: {str(e)}")


@bot.tree.command(name="rag-status", description="Check RAG system status")
async def status(interaction: discord.Interaction):
    """Slash command to check status."""
    try:
        rag = get_pipeline()
        stats = rag.get_stats()

        embed = discord.Embed(
            title="RAG System Status",
            color=discord.Color.green()
        )
        embed.add_field(name="Documents", value=stats.get("document_count", 0))
        embed.add_field(name="Chunks", value=stats.get("chunk_count", 0))
        embed.add_field(name="Vector Store", value=stats.get("vector_store", "Unknown"))
        embed.add_field(name="LLM Provider", value=stats.get("llm_provider", "Unknown"))

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        await interaction.response.send_message(f"Error: {str(e)}")


@bot.command(name="ask")
async def ask_command(ctx, *, question: str):
    """Legacy command for asking questions."""
    async with ctx.typing():
        try:
            rag = get_pipeline()
            response = ""
            for token in rag.query_stream(question):
                response += token

            if len(response) > 1900:
                response = response[:1900] + "..."

            await ctx.reply(response)

        except Exception as e:
            await ctx.reply(f"Error: {str(e)}")


def main():
    """Run the Discord bot."""
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        logger.error("DISCORD_BOT_TOKEN not set")
        return

    bot.run(token)


if __name__ == "__main__":
    main()


"""
Setup Instructions:

1. Create a Discord Application at discord.com/developers

2. Create a Bot and get the token

3. Enable required intents:
   - Message Content Intent
   - Server Members Intent (optional)

4. Generate invite URL with permissions:
   - Send Messages
   - Read Message History
   - Use Slash Commands

5. Set environment variables:
   export DISCORD_BOT_TOKEN="your-bot-token"
   export ANTHROPIC_API_KEY="sk-ant-..."

6. Install dependencies:
   pip install discord.py

7. Run the bot:
   python discord_bot.py

8. Commands:
   - /ask <question> - Ask a question
   - /search <query> - Search documents
   - /rag-status - Check system status
   - !ask <question> - Legacy prefix command
"""
