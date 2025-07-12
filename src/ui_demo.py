import gradio as gr
import json
from typing import Dict, Any
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.smart_tagger import SmartTagger
from src.models.tags import TagRequest


# Initialize smart tagger
smart_tagger = SmartTagger(enable_ml=True)


def tag_text(
    text: str, 
    enable_rules: bool = True, 
    enable_ml: bool = True,
    show_confidence: bool = True
) -> str:
    """Tag text and return formatted results"""
    if not text.strip():
        return "Please enter some text to tag."
    
    try:
        # Create request
        request = TagRequest(
            content=text,
            enable_rules=enable_rules,
            enable_ml=enable_ml
        )
        
        # Get tags
        response = smart_tagger.tag(request)
        
        # Format output
        output = f"**Content ID:** {response.content_id}\n\n"
        output += f"**Processing Time:** {response.processing_time:.3f} seconds\n\n"
        
        tags = response.tags
        
        # Content Type
        if tags.content_type:
            output += f"**Content Type:** {tags.content_type.value}\n\n"
        
        # Domains
        if tags.domains:
            output += "**Domains:**\n"
            for domain in tags.domains:
                output += f"- {domain.value}\n"
            output += "\n"
        
        # Priority
        if tags.priority:
            output += f"**Priority:** {tags.priority.value}\n\n"
        
        # Stakeholders
        if tags.stakeholders:
            output += "**Stakeholders:**\n"
            for stakeholder in tags.stakeholders:
                output += f"- {stakeholder.value}\n"
            output += "\n"
        
        # Custom Tags and Confidence Scores
        if show_confidence and tags.custom_tags:
            output += "**Additional Tags & Confidence:**\n"
            for tag in tags.custom_tags:
                if tag.category == "ml_confidence":
                    output += f"- {tag.value} (source: {tag.source})\n"
                else:
                    output += f"- {tag.category}: {tag.value} (confidence: {tag.confidence:.2f}, source: {tag.source})\n"
        
        return output
        
    except Exception as e:
        return f"Error: {str(e)}"


def create_demo():
    """Create Gradio demo interface"""
    with gr.Blocks(title="Label Router - Intelligent Tagging Demo") as demo:
        gr.Markdown("""
        # Label Router - Intelligent Tagging System Demo
        
        This demo shows the intelligent tagging system for construction meeting content.
        Enter Japanese text related to construction meetings to see the automatic tagging in action.
        """)
        
        with gr.Row():
            with gr.Column():
                text_input = gr.Textbox(
                    label="Input Text",
                    placeholder="Enter construction meeting content in Japanese...",
                    lines=10
                )
                
                with gr.Row():
                    enable_rules = gr.Checkbox(
                        label="Enable Rule-based Tagging",
                        value=True
                    )
                    enable_ml = gr.Checkbox(
                        label="Enable ML-based Tagging",
                        value=True
                    )
                    show_confidence = gr.Checkbox(
                        label="Show Confidence Scores",
                        value=True
                    )
                
                tag_button = gr.Button("Tag Content", variant="primary")
            
            with gr.Column():
                output = gr.Markdown(label="Tagging Results")
        
        # Examples
        gr.Examples(
            examples=[
                ["本日の会議で基礎工事の工程について決定しました。施工者は来週月曜日までに詳細な工程表を提出してください。"],
                ["鉄筋コンクリート構造の品質検査で問題が発見されました。至急、設計者と施工者で対応を協議する必要があります。"],
                ["安全パトロールの結果、3階の作業エリアで危険箇所が確認されました。協力業者は直ちに是正措置を実施してください。"],
                ["設備工事の追加費用について、発注者の承認が必要です。見積金額は約500万円となります。"],
                ["今月の工程会議の日程調整について連絡します。参考資料を共有しますので、ご確認ください。"]
            ],
            inputs=text_input
        )
        
        # Event handler
        tag_button.click(
            fn=tag_text,
            inputs=[text_input, enable_rules, enable_ml, show_confidence],
            outputs=output
        )
    
    return demo


if __name__ == "__main__":
    demo = create_demo()
    demo.launch(server_name="0.0.0.0", server_port=7860)