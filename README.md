 🌟 **Introduction**

This project connects state-of-the-art LLMs (Llama, Gemma, Qwen, Mistral, and more) to a local [Pokémon Showdown](https://pokemonshowdown.com/) server via [poke-env](https://github.com/hsahovic/poke-env). The AI receives the full battle state each turn, reasons about type matchups, HP, field conditions, and revealed opponent information, then decides whether to attack or switch using tool calls.

A [Gradio](https://gradio.app/) interface lets you:
- **Human vs. AI** - Play against any supported LLM yourself.
- **AI vs. AI** - Pick two models and watch them fight autonomously.

All LLM calls are routed through [LiteLLM](https://litellm.ai/) and traced via [Langfuse](https://langfuse.com/) for observability.

## Architecture

```
pokemon-ai-agent/
├── run.py              
├── app.py              
├── agent.py            # LLM-powered agent: formats battle state, queries LLM, parses tool calls
├── battle_runners.py   # Async battle orchestration: agent creation, matchmaking threads
├── tools.py            # Tool definitions (choose_move, choose_switch) sent to the LLM
├── .env                # Template for API keys
├── pyproject.toml      # Python dependencies

```
## How to start:

Requirement:
- [Python 3.14+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/) (for the Showdown server and client)


### 1. Clone and configure

```bash
git clone https://github.com/datt46999/Pokemon_AI_agent.git
cd Pokemon_AI_agent
```

Edit `.env` and paste your API keys. See [Getting API Keys](#getting-api-keys) below.

### 2. Create venv and install dependencies

```bash
uv venv
.venv/bin/activate
uv sync
```

### 3. Run

```bash
uv run python run.py
```
This single command will:
1. Clone the Showdown server and client repos (first run only).
2. Install their Node.js dependencies and build the client.
3. Start the local Showdown server on port `8000`.
4. Launch the Gradio control panel on port `7860`.


## Get API Key:
All models in this project use **free-tier API quotas** (as of April 2026, per [free-llm-api-resources](https://github.com/cheahjs/free-llm-api-resources)). Just create a free account on each provider's platform, generate an API key, and paste it into `.env`.

| Provider | Env Variable |
|----------|-------------|
| [OpenRouter](https://openrouter.ai/) | `OPENROUTER_API_KEY` |
| [Cerebras](https://cloud.cerebras.ai/) | `CEREBRAS_API_KEY` |
| [Google AI Studio](https://aistudio.google.com/) | `GEMINI_API_KEY` |
| [Groq](https://console.groq.com/) | `GROQ_API_KEY` |
| [Mistral](https://console.mistral.ai/) | `MISTRAL_API_KEY` |



You only need keys for the providers whose models you want to use. If you only want to try Cerebras models, only `CEREBRAS_API_KEY` is required.

### Using Paid Tiers for More Powerful Models

If you have a paid API key (e.g., Gemini Pro, OpenAI GPT-4, Anthropic Claude), you can add any model supported by [LiteLLM](https://docs.litellm.ai/docs/providers) to the `MODEL_MAP` dictionary in `battle_runners.py`:


### Exmaple like this:

```python


MODEL_MAP = {
    # OpenRouter
    "OpenRouter GLM 4.5 Air": "openrouter/z-ai/glm-4.5-air:free",

    # Cerebras
    "Cerebras Qwen 3 235B": "cerebras/qwen3-235b-a22b-instruct-2507",

    # Google AI Studio
    "Google Gemma 4 31B": "gemini/gemma-4-31b-it",
  

    # Groq
    "Groq Qwen3 32B": "groq/qwen/qwen3-32b",
    # Mistral
    "Mistral Codestral 2508": "mistral/codestral-2508",

    # HuggingFace
    "HuggingFace SynLogic-Mix-3-32B": "huggingface/MiniMaxAI/SynLogic-Mix-3-32B:featherless-ai",

}
```

Then add the corresponding API key to your `.env`:


All LLM calls are traced via [Langfuse](https://langfuse.com/). You can view the full decision-making trace for every turn: the battle state sent to the model, the model's tool call response, and any fallback actions.

**Live dashboard (free tier):** [Langfuse Cloud Dashboard](https://cloud.langfuse.com/project/cmoc2kqe300z6ad08cgab046t/traces?dateRange=30d)

> **Note:** This project uses the Langfuse free (Hobby) tier. Historical trace data older than 30 days is not retained, so the dashboard may appear empty if no recent battles have been run.

To set up your own Langfuse tracing, add your keys to `.env`:

```
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```



### [Demo results](https://drive.google.com/file/d/1A7keRRiTaEJNySbDXE_qsHJWaI0gyIe0/view?usp=sharing)

### Code in [hugging_face](https://huggingface.co/spaces/gugukaka/pokemon_agent)
## 🔗 **Resources**

- [Poke-env](https://github.com/hsahovic/poke-env)
- [Hugging Face Agents Course](https://huggingface.co/agents-course)
- [Pokémon Showdown](https://github.com/smogon/Pokemon-Showdown)
- [Langfuse](https://langfuse.com/)
