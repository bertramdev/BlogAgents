#!/usr/bin/env python3
"""
Streamlit app for Topic Idea Generation using TopicIdeaAgent.
"""
import streamlit as st
import os
import json
import logging
import time
from dotenv import load_dotenv

load_dotenv()


class Config:
    """App configuration."""
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# Logging setup
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def generate_topics(
    api_key: str,
    model: str,
    reference_blog: str,
    target_keywords: list,
    product_target: str,
    existing_topics: list,
    num_topics: int,
    status_placeholder,
    progress_bar
) -> dict:
    """
    Generate topic ideas using TopicIdeaAgent.

    Args:
        api_key: OpenAI API key
        model: Model to use
        reference_blog: Blog URL to analyze
        target_keywords: List of keywords to incorporate
        product_target: Product/service to promote
        existing_topics: Topics to avoid duplicating
        num_topics: Number of topics to generate
        status_placeholder: Streamlit placeholder for status
        progress_bar: Streamlit progress bar

    Returns:
        dict with success status and data/error
    """
    os.environ["OPENAI_API_KEY"] = api_key

    logger.info(f"Generating topics for {reference_blog}")

    try:
        from custom_agents import TopicIdeaAgent

        agent = TopicIdeaAgent(model=model)

        def status_callback(message: str, progress: int):
            status_placeholder.info(message)
            progress_bar.progress(progress)

        status_callback("Initializing TopicIdeaAgent...", 10)

        topics = agent.generate(
            reference_blog=reference_blog,
            target_keywords=target_keywords if target_keywords else None,
            product_target=product_target if product_target else None,
            existing_topics=existing_topics if existing_topics else None,
            num_topics=num_topics,
            status_callback=status_callback
        )

        logger.info(f"Generated {len(topics)} topics")
        return {"success": True, "data": topics}

    except Exception as e:
        logger.error(f"Topic generation failed: {str(e)}")
        return {"success": False, "error": str(e)}


def main():
    """Streamlit app entry point."""
    st.set_page_config(
        page_title="Topic Idea Generator",
        layout="wide"
    )

    st.title("Topic Idea Generator")
    st.markdown("Generate blog topic ideas using AI-powered analysis")

    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")

        # API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            value=Config.OPENAI_API_KEY or "",
            type="password",
            help="Your OpenAI API key"
        )

        # Model selection
        model = st.selectbox(
            "Model",
            options=[
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4.1",
                "gpt-4.1-mini",
            ],
            index=0,
            help="OpenAI model to use for topic generation"
        )

        st.markdown("---")

        # Clear results button
        if st.button("Clear Results"):
            if 'generated_topics' in st.session_state:
                del st.session_state.generated_topics
            st.rerun()

    # Main content - single column layout
    st.header("Input Parameters")

    # Reference blog URL (required)
    reference_blog = st.text_input(
        "Reference Blog URL (required)",
        placeholder="https://blog.example.com/",
        help="The blog to analyze for style and content strategy"
    )

    # Target keywords (optional)
    keywords_input = st.text_area(
        "Target Keywords (optional)",
        placeholder="Enter keywords separated by commas:\nsafety knives, utility knives, box cutter safety",
        height=100,
        help="Keywords to incorporate into topic ideas for SEO"
    )

    # Parse keywords into list
    target_keywords = []
    if keywords_input.strip():
        target_keywords = [kw.strip() for kw in keywords_input.split(',') if kw.strip()]

    # Product target (optional)
    product_target = st.text_area(
        "Product/Service Target (optional)",
        placeholder="Enter product URL or description:\nhttps://example.com/products/my-product\nOr describe the product/service to promote...",
        height=100,
        help="Product or service to naturally promote in topic ideas"
    )

    # Existing topics to avoid (optional)
    existing_topics_input = st.text_area(
        "Existing Topics to Avoid (optional)",
        placeholder="Enter existing blog post titles, one per line:\nHow to Choose the Right Safety Knife\n10 Tips for Warehouse Safety",
        height=150,
        help="Existing blog posts to avoid duplicating"
    )

    # Parse existing topics into list
    existing_topics = []
    if existing_topics_input.strip():
        existing_topics = [t.strip() for t in existing_topics_input.split('\n') if t.strip()]

    # Number of topics
    num_topics_input = st.text_input(
        "Number of Topics",
        value="5",
        help="How many topic ideas to generate"
    )

    # Parse num_topics as integer
    try:
        num_topics = int(num_topics_input)
        if num_topics < 1:
            num_topics = 1
        elif num_topics > 20:
            num_topics = 20
    except ValueError:
        num_topics = 5

    # Generate button
    generate_disabled = not api_key or not reference_blog.strip()
    if st.button("Generate Topic Ideas", type="primary", disabled=generate_disabled):
        st.session_state.run_generation = True

    st.markdown("---")
    st.header("Output")

    # Run generation if triggered
    if st.session_state.get('run_generation'):
        st.session_state.run_generation = False

        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        status_placeholder.info("Initializing...")

        start_time = time.time()
        result = generate_topics(
            api_key=api_key,
            model=model,
            reference_blog=reference_blog,
            target_keywords=target_keywords,
            product_target=product_target,
            existing_topics=existing_topics,
            num_topics=num_topics,
            status_placeholder=status_placeholder,
            progress_bar=progress_bar
        )
        elapsed_seconds = int(time.time() - start_time)

        # Format elapsed time as HH:MM:SS
        hours, remainder = divmod(elapsed_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        elapsed_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        if result["success"]:
            progress_bar.progress(100)
            status_placeholder.success(f"Generated {len(result['data'])} topic ideas! Time elapsed: {elapsed_str}")
            st.session_state.generated_topics = result["data"]
        else:
            status_placeholder.error(f"Error: {result['error']} (Time elapsed: {elapsed_str})")

    # Display generated topics
    if 'generated_topics' in st.session_state and st.session_state.generated_topics:
        topics = st.session_state.generated_topics

        for i, topic in enumerate(topics):
            with st.expander(f"{i + 1}. {topic.get('title', 'Untitled')}", expanded=(i == 0)):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"**Angle:** {topic.get('angle', 'N/A')}")
                    st.markdown(f"**Rationale:** {topic.get('rationale', 'N/A')}")

                with col2:
                    st.markdown(f"**Content Type:** {topic.get('content_type', 'N/A')}")
                    keywords = topic.get('keywords', [])
                    if keywords:
                        st.markdown(f"**Keywords:** {', '.join(keywords)}")

        # Export options
        st.markdown("---")
        st.subheader("Export")

        # Convert to JSON for download
        topics_json = json.dumps(topics, indent=2)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download as JSON",
                data=topics_json,
                file_name="topic_ideas.json",
                mime="application/json"
            )

        with col2:
            # Convert to markdown
            md_content = "# Generated Topic Ideas\n\n"
            for i, topic in enumerate(topics):
                md_content += f"## {i + 1}. {topic.get('title', 'Untitled')}\n\n"
                md_content += f"- **Angle:** {topic.get('angle', 'N/A')}\n"
                md_content += f"- **Keywords:** {', '.join(topic.get('keywords', []))}\n"
                md_content += f"- **Rationale:** {topic.get('rationale', 'N/A')}\n"
                md_content += f"- **Content Type:** {topic.get('content_type', 'N/A')}\n\n"

            st.download_button(
                label="Download as Markdown",
                data=md_content,
                file_name="topic_ideas.md",
                mime="text/markdown"
            )

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray; padding: 1rem 0;'>
        <p>Powered by TopicIdeaAgent</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
