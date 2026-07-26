import gradio as gr

from src.ui.callbacks import process_pipeline


def create_ui() -> gr.Blocks:
    with gr.Blocks(
        title="TikTok to YouTube Shorts",
    ) as demo:
        gr.Markdown(
            "# TikTok to YouTube Shorts"
        )

        with gr.Row():
            with gr.Column():
                url_input = gr.Textbox(
                    label="TikTok Video URL",
                    placeholder="https://www.tiktok.com/@user/video/123456...",
                )
                title_input = gr.Textbox(
                    label="Video Title",
                    placeholder="Enter YouTube video title",
                )
                desc_input = gr.Textbox(
                    label="Description",
                    placeholder="Video description (optional)",
                    lines=3,
                )
                tags_input = gr.Textbox(
                    label="Tags",
                    placeholder="tag1, tag2, tag3 (comma-separated, optional)",
                )
                privacy_input = gr.Dropdown(
                    label="Privacy",
                    choices=["public", "unlisted", "private"],
                    value="public",
                )
                submit_btn = gr.Button("Start", variant="primary", size="lg")

            with gr.Column():
                status_text = gr.Markdown("Ready")
                output_link = gr.Markdown("")
                error_box = gr.Textbox(
                    label="Error",
                    visible=False,
                    interactive=False,
                )

        submit_btn.click(
            fn=process_pipeline,
            inputs=[url_input, title_input, desc_input, tags_input, privacy_input],
            outputs=[output_link, error_box],
        ).then(
            fn=lambda link, err: (
                gr.update(value=f"[Watch on YouTube]({link})", visible=bool(link)),
                gr.update(value=err, visible=bool(err)),
            ),
            inputs=[output_link, error_box],
            outputs=[output_link, error_box],
        )

    return demo
