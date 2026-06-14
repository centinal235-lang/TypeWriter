#@title TypeWriter Minimal UI: input → output only

# Run this cell after the model/adapter is loaded and e2e_generate_one() is defined.

try:
    import gradio as gr
except Exception:
    !pip -q install gradio
    import gradio as gr

def typewriter_generate(user_input):
    user_input = (user_input or "").strip()

    if not user_input:
        return "입력을 넣어줘."

    try:
        result = e2e_generate_one(user_input)
        return result.get("final_text", "").strip() or "[EMPTY OUTPUT]"
    except Exception as e:
        return f"[ERROR]\n{repr(e)}"

with gr.Blocks(title="TypeWriter") as demo:
    gr.Markdown("## TypeWriter")

    user_input = gr.Textbox(
        label="입력",
        placeholder="예: 탑 17층 공략 뒤 협회 공시의 최고층 갱신 기한을 보고 루트를 바꾸는 장면",
        lines=4,
    )

    run_btn = gr.Button("생성")

    output = gr.Textbox(
        label="출력",
        lines=22,
        show_copy_button=True,
    )

    run_btn.click(
        fn=typewriter_generate,
        inputs=user_input,
        outputs=output,
    )

demo.queue()
demo.launch(share=True, debug=False)
