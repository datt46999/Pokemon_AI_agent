import asyncio
import random
import string
import traceback
import logging
import threading

from poke_env.player import Player, RandomPlayer
from poke_env import AccountConfiguration, LocalhostServerConfiguration
from agent import PokemonAgent

logger = logging.getLogger(__name__)

# Constants
DEFAULT_BATTLE_FORMAT = "gen9randombattle"

# Free Models Mapping. src: https://github.com/cheahjs/free-llm-api-resources
MODEL_MAP = {
    # OpenRouter
    "OpenRouter GLM 4.5 Air": "openrouter/z-ai/glm-4.5-air:free",

    # Cerebras
    "Cerebras Qwen 3 235B": "cerebras/qwen3-235b-a22b-instruct-2507",

    # Google AI Studio
    "Google Gemma 4 31B": "gemini/gemma-4-31b-it",
    "Google Gemma 3 27B": "gemini/gemma-3-27b-it",
    "Google Gemini 3.1 Flash-Lite": "gemini/gemini-3.1-flash-lite-preview",

    # Groq
    "Groq Qwen3 32B": "groq/qwen/qwen3-32b",
    "Groq OpenAI GPT-OSS 120B": "groq/openai/gpt-oss-120b",
    "Groq Compound": "groq/groq/compound",

    # Mistral
    "Mistral Codestral 2508": "mistral/codestral-2508",

    # HuggingFace
    "HuggingFace SynLogic-Mix-3-32B": "huggingface/MiniMaxAI/SynLogic-Mix-3-32B:featherless-ai",

}
AGENT_OPTIONS = ["Random Baseline Bot (Random moves (no LLM))"] + list(MODEL_MAP.keys())

async def create_agent_async(agent_type: str, username: str,
                             battle_format: str = DEFAULT_BATTLE_FORMAT) -> Player | str:
    """Create a Pokémon Showdown agent.

    A random suffix is appended to the username so that reusing the same base
    name across battles never triggers a stale-login assertion in poke-env.
    Password is None because the local server runs with --no-security; a
    non-None password causes poke-env to POST to play.pokemonshowdown.com,
    which fails with KeyError: 'assertion'.
    """
    # Append a short numeric suffix with underscore to avoid username collisions
    suffix = ''.join(random.choices(string.digits, k=4))
    session_username = f"{username}_{suffix}"
    logger.info("Attempting to create %s as '%s' (base: '%s')", agent_type, session_username, username)
    
    server_configuration = LocalhostServerConfiguration
    account_config = AccountConfiguration(session_username, None)
    try:
        if agent_type == "Random Baseline Bot (Random moves (no LLM))":
            player = RandomPlayer(
                account_configuration=account_config,
                server_configuration=server_configuration,
                battle_format=battle_format,
                start_listening=True,
            )
        elif agent_type in MODEL_MAP:
            player = PokemonAgent(
                model_name=MODEL_MAP[agent_type],
                account_configuration=account_config,
                server_configuration=server_configuration,
                battle_format=battle_format,
                start_listening=True,
            )
        else:
            return f"Error: Invalid agent type '{agent_type}' requested."

        logger.info("Agent '%s' created successfully on local server.", username)
        return player

    except Exception as e:
        error_message = f"Error creating agent {username}: {e}"
        logger.error(traceback.format_exc())
        return error_message

async def send_battle_invite_async(player: Player, opponent_username: str, battle_format: str) -> str:
    try:
        await player.send_challenges(opponent_username, n_challenges=1)
        return f"Invitation sent to {opponent_username}!"
    except Exception as e:
        logger.error(traceback.format_exc())
        raise e

# Background Threads

def start_invite_thread(agent_choice: str, opp_username: str, bot_username: str) -> str:
    if not opp_username.strip(): return "Please enter your Showdown username."
    if not bot_username.strip(): return "Please enter a bot username."

    def _bg_task():
        async def _run():
            agent_or_error = await create_agent_async(agent_choice, bot_username)
            if isinstance(agent_or_error, str): return
            try:
                await send_battle_invite_async(agent_or_error, opp_username.strip(), DEFAULT_BATTLE_FORMAT)
            except Exception:
                pass
            # Keep loop alive for the battle
            while list(agent_or_error.battles.values()) or list(agent_or_error._challenges.values()):
                await asyncio.sleep(1)
        asyncio.run(_run())

    threading.Thread(target=_bg_task, daemon=True).start()
    return f"'{bot_username}' is attempting to challenge '{opp_username}'. Keep your client open!"

def start_bot_vs_bot_thread(agent1_choice: str, bot1_username: str,
                            agent2_choice: str, bot2_username: str) -> str:
    if not bot1_username.strip() or not bot2_username.strip(): return "Both bots need a username."

    def _bg_task():
        async def _run():
            agent1 = await create_agent_async(agent1_choice, bot1_username)
            agent2 = await create_agent_async(agent2_choice, bot2_username)
            if isinstance(agent1, str) or isinstance(agent2, str): return
            await agent1.battle_against(agent2, n_battles=1)
            logger.info("Arena match finished.")
        asyncio.run(_run())

    threading.Thread(target=_bg_task, daemon=True).start()
    return f"Arena match started between {bot1_username} and {bot2_username}!"