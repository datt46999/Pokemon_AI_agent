import gradio as gr



from battle_runners import AGENT_OPTIONS, start_invite_thread, start_bot_vs_bot_thread
from dotenv import load_dotenv

load_dotenv()



# Constants
DEFAULT_BATTLE_FORMAT = "gen9randombattle"

PIKACHU_GIF = "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExMWxlZ2J5d3N2Nm9oanRldTA3aGw4NHFrcW53ZGk1bWdzaWtlaGJwZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/xeuSulJ22SiTaZWBoD/giphy.gif"


def main_app():
    """Creates and returns the Gradio application interface."""

    # Load custom CSS from file
    css_path = "style.css"
    with open(css_path, "r", encoding="utf-8") as f:
        custom_css = f.read()

    elite_theme = gr.themes.Base(
        primary_hue="red",
        secondary_hue="amber",
        neutral_hue="slate",
        font=[
            gr.themes.GoogleFont("Inter"),
            "ui-sans-serif",
            "system-ui",
            "sans-serif",
        ],
        text_size=gr.themes.sizes.text_lg,
    ).set(
        body_background_fill="#0f0c29",
        body_background_fill_dark="#0f0c29",
        body_text_color="#e0e0e0",
        body_text_color_dark="#e0e0e0",
        body_text_color_subdued="#94a3b8",
        body_text_color_subdued_dark="#94a3b8",
        background_fill_primary="#1a1a2e",
        background_fill_primary_dark="#1a1a2e",
        background_fill_secondary="#16213e",
        background_fill_secondary_dark="#16213e",
        block_background_fill="#1a1a2e",
        block_background_fill_dark="#1a1a2e",
        block_border_color="rgba(255,255,255,0.08)",
        block_border_color_dark="rgba(255,255,255,0.08)",
        block_label_text_color="#cbd5e1",
        block_label_text_color_dark="#cbd5e1",
        block_title_text_color="#e0e0e0",
        block_title_text_color_dark="#e0e0e0",
        input_background_fill="#12122a",
        input_background_fill_dark="#12122a",
        input_border_color="rgba(255,255,255,0.12)",
        input_border_color_dark="rgba(255,255,255,0.12)",
        input_border_color_focus="#FFCB05",
        input_border_color_focus_dark="#FFCB05",
        input_placeholder_color="#64748b",
        input_placeholder_color_dark="#64748b",
        border_color_primary="rgba(255,255,255,0.08)",
        border_color_primary_dark="rgba(255,255,255,0.08)",
        panel_background_fill="#16213e",
        panel_background_fill_dark="#16213e",
        panel_border_color="rgba(255,255,255,0.06)",
        panel_border_color_dark="rgba(255,255,255,0.06)",
        button_primary_background_fill="#CC0000",
        button_primary_background_fill_dark="#CC0000",
        button_primary_background_fill_hover="#FF1A1A",
        button_primary_background_fill_hover_dark="#FF1A1A",
        button_primary_text_color="#ffffff",
        button_primary_text_color_dark="#ffffff",
        shadow_drop="none",
        shadow_drop_lg="none",
    )

    with gr.Blocks(title="Pokémon AI Agents") as demo:
        # --- Hero Section ---
        gr.HTML(
            f"""
            <div class="hero-section">
                <div class="hero-title">Pokémon AI Agents</div>
                <div class="hero-subtitle">
                    Watch Large Language Models battle each other in Pokémon Showdown or challenge them yourself.
                </div>
                <img src="{PIKACHU_GIF}" class="hero-gif" alt="Pikachu" />
            </div>
            """
        )

        # --- Spectate Button ---
        gr.HTML(
            """
            <div class="spectate-wrapper">
                <a href="http://localhost:8000" target="_blank" class="spectate-btn">
                    <span class="pulse-dot"></span>
                    Spectate Matches (Live Showdown Client)
                </a>
            </div>
            """
        )

        # --- Battle Controls ---
        with gr.Row():
            with gr.Column(scale=1, min_width=500):
                with gr.Tab("Human vs. AI") as tab_player:
                    gr.HTML(
                        '<div class="tab-explanation">You play against an AI agent. Log in to Showdown, then the bot challenges you.</div>'
                    )
                    with gr.Group():
                        agent_drop = gr.Dropdown(
                            choices=AGENT_OPTIONS,
                            label="AI Agent (LLM)",
                            value="Cerebras Llama 3.1 8B",
                        )
                        opp_user = gr.Textbox(
                            label="Your Showdown Username",
                            placeholder="The username you logged in with on the Showdown client",
                        )
                        bot_user = gr.Textbox(
                            label="Bot Username",
                            placeholder="Any unique name for the AI bot (e.g., pikabot99)",
                        )
                        challenge_btn = gr.Button("Send Challenge", variant="primary")
                    status_out = gr.Textbox(
                        label="Status",
                        interactive=False,
                        lines=2,
                        elem_classes=["status-box"],
                    )
                    challenge_btn.click(
                        fn=lambda a, o, b: start_invite_thread(a, o, b),
                        inputs=[agent_drop, opp_user, bot_user],
                        outputs=status_out,
                    )

                with gr.Tab("AI vs. AI") as tab_arena:
                    gr.HTML(
                        '<div class="tab-explanation">Two AI agents battle each other autonomously. Just pick models and watch.</div>'
                    )
                    with gr.Group():
                        with gr.Row():
                            with gr.Column():
                                a1_drop = gr.Dropdown(
                                    choices=AGENT_OPTIONS,
                                    label="Model 1",
                                    value="Cerebras Llama 3.1 8B",
                                )
                                b1_user = gr.Textbox(
                                    label="Bot 1 Username",
                                    placeholder="e.g., bot_llama",
                                )
                            with gr.Column():
                                a2_drop = gr.Dropdown(
                                    choices=AGENT_OPTIONS,
                                    label="Model 2",
                                    value="Mistral Codestral 2508",
                                )
                                b2_user = gr.Textbox(
                                    label="Bot 2 Username",
                                    placeholder="e.g., bot_gemma",
                                )
                        arena_btn = gr.Button(
                            "Start AI vs. AI Battle", variant="primary"
                        )
                    arena_status = gr.Textbox(
                        label="Status",
                        interactive=False,
                        lines=2,
                        elem_classes=["status-box"],
                    )
                    arena_btn.click(
                        fn=lambda a1, b1, a2, b2: start_bot_vs_bot_thread(
                            a1, b1, a2, b2
                        ),
                        inputs=[a1_drop, b1_user, a2_drop, b2_user],
                        outputs=arena_status,
                    )

    return demo, custom_css, elite_theme