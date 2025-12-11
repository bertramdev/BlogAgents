#!/usr/bin/env python3
"""
Streamlit app for submitting JSON to OpenAI AgentBuilder workflow.
"""
import streamlit as st
import os
import json
import logging
import time
import asyncio
import traceback
from dotenv import load_dotenv

# Load environment variables immediately after imports
load_dotenv()

# Configuration
class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    WORKFLOW_ID = os.getenv("WORKFLOW_ID", "wf_692e0fdc02508190b3b51b94f2b7deea0f87a40e1a3b5c93")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Logging setup
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Sample JSON template
SAMPLE_JSON = """{
  "high_performing_pages": [
    "https://blog.sliceproducts.com/blog/power-of-listening-in-safety",
    "https://blog.sliceproducts.com/blog/daily-safety-topics"
  ],
  "root_blog_url": "https://blog.sliceproducts.com/",
  "target_product_urls": [
    "https://www.sliceproducts.com/products/manual-box-cutter",
    "https://www.sliceproducts.com/products/auto-retractable-metal-handle-utility-knife"
  ],
  "topics": [
    "safety cutters"
  ],
  "writing_requirements": "length should be 2000 words, include FAQ section, add call to action"
}"""


def validate_json(json_text: str) -> tuple[bool, str, dict | None]:
    """
    Validate JSON text and return parsed object.

    Returns:
        tuple: (is_valid, error_message, parsed_json)
    """
    if not json_text or not json_text.strip():
        return False, "JSON input is empty", None

    try:
        parsed = json.loads(json_text)
        logger.info("JSON validation successful")
        return True, "", parsed
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON: {str(e)}"
        logger.error(error_msg)
        return False, error_msg, None


def call_workflow(json_input: str, api_key: str, status_placeholder=None, progress_bar=None) -> dict:
    """
    Call the OpenAI AgentBuilder workflow with JSON input.

    Args:
        json_input: JSON string to send to the workflow
        api_key: OpenAI API key
        status_placeholder: Streamlit placeholder for status updates
        progress_bar: Streamlit progress bar for visual progress

    Returns:
        dict with response or error
    """
    # Set API key in environment for the agents SDK
    os.environ["OPENAI_API_KEY"] = api_key

    logger.info(f"Calling workflow with input: {json_input[:100]}...")

    # Agent tracking
    agents = [
        ("text_to_json", "Parsing JSON input..."),
        ("writing_style", "Analyzing writing style..."),
        ("research", "Researching topic..."),
        ("writer", "Writing blog draft..."),
        ("seo_analyzer", "Analyzing SEO..."),
        ("internal_links", "Adding internal links..."),
        ("editor", "Final editing...")
    ]
    agent_count = [0]  # Use list to allow mutation in handler

    # Custom handler to track HTTP requests and update status
    class StreamlitHandler(logging.Handler):
        def emit(self, record):
            msg = record.getMessage()
            if "POST https://api.openai.com/v1/responses" in msg and "200 OK" in msg:
                agent_count[0] += 1
                if agent_count[0] <= len(agents):
                    progress = int((agent_count[0] / len(agents)) * 100)
                    if progress_bar:
                        progress_bar.progress(progress)
                    if status_placeholder:
                        if agent_count[0] < len(agents):
                            next_agent = agents[agent_count[0]][1]
                            status_placeholder.info(f"Step {agent_count[0]}/{len(agents)} completed. Next: {next_agent}")
                        else:
                            status_placeholder.success(f"All {len(agents)} agents completed!")

    # Add custom handler to httpx logger
    httpx_logger = logging.getLogger("httpx")
    streamlit_handler = StreamlitHandler()
    streamlit_handler.setLevel(logging.INFO)
    httpx_logger.addHandler(streamlit_handler)

    try:
        # Import the workflow module
        from zzz_pg_openai_workflow import run_workflow, WorkflowInput

        # Create workflow input
        workflow_input = WorkflowInput(input_as_text=json_input)

        if status_placeholder:
            status_placeholder.info(f"Starting: {agents[0][1]}")

        # Run the async workflow
        logger.info("Starting workflow execution...")
        result = asyncio.run(run_workflow(workflow_input))

        logger.info("Workflow completed successfully")
        return {"success": True, "data": result}

    except Exception as e:
        logger.error(f"Workflow failed: {str(e)}")
        traceback.print_exc()
        return {"success": False, "error": f"Workflow failed: {str(e)}"}

    finally:
        # Remove handler to prevent duplicate logs
        httpx_logger.removeHandler(streamlit_handler)


def main():
    """Streamlit app entry point."""
    st.set_page_config(
        page_title="Blog Agent Workflow",
        layout="wide"
    )

    st.title("Blog Agent Workflow")
    st.markdown("Submit JSON configuration to run the OpenAI AgentBuilder workflow")

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

        # Workflow ID display
        st.text_input(
            "Workflow ID",
            value=Config.WORKFLOW_ID,
            disabled=True,
            help="The AgentBuilder workflow ID"
        )

        st.markdown("---")

        # Load sample button
        if st.button("Load Sample JSON"):
            st.session_state.json_input = SAMPLE_JSON
            st.rerun()

        # Clear button
        if st.button("Clear Input"):
            st.session_state.json_input = ""
            st.rerun()

    # Main content
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("JSON Input")

        # Initialize session state for json_input if not exists
        if 'json_input' not in st.session_state:
            st.session_state.json_input = SAMPLE_JSON

        # JSON textarea
        json_input = st.text_area(
            "Enter your JSON configuration:",
            value=st.session_state.json_input,
            height=500,
            placeholder=SAMPLE_JSON,
            help="Paste your JSON configuration here"
        )

        # Update session state
        st.session_state.json_input = json_input

        # Validate button
        col_validate, col_submit = st.columns(2)

        with col_validate:
            if st.button("Validate JSON", use_container_width=True):
                is_valid, error_msg, parsed = validate_json(json_input)
                if is_valid:
                    st.success("JSON is valid!")
                    with st.expander("Parsed JSON", expanded=False):
                        st.json(parsed)
                else:
                    st.error(error_msg)

        with col_submit:
            submit_disabled = not api_key or not json_input.strip()
            if st.button("Submit to Workflow", type="primary", use_container_width=True, disabled=submit_disabled):
                # Validate JSON first
                is_valid, error_msg, parsed = validate_json(json_input)

                if not is_valid:
                    st.error(error_msg)
                else:
                    st.session_state.run_workflow = True
                    st.session_state.workflow_input = json_input

    with col2:
        st.header("Output")

        # Run workflow if triggered
        if st.session_state.get('run_workflow'):
            st.session_state.run_workflow = False

            progress_bar = st.progress(0)
            status_placeholder = st.empty()
            status_placeholder.info("Initializing workflow...")

            start_time = time.time()
            result = call_workflow(st.session_state.workflow_input, api_key, status_placeholder, progress_bar)
            elapsed_seconds = int(time.time() - start_time)

            # Format elapsed time as HH:MM:SS
            hours, remainder = divmod(elapsed_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            elapsed_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            if result["success"]:
                progress_bar.progress(100)
                status_placeholder.success(f"Workflow completed successfully! Time elapsed: {elapsed_str}")

                # Store result in session state
                st.session_state.workflow_result = result["data"]
            else:
                status_placeholder.error(f"{result['error']} (Time elapsed: {elapsed_str})")

        # Display results if available
        if 'workflow_result' in st.session_state:
            result_data = st.session_state.workflow_result

            # Try to extract the output text
            if isinstance(result_data, dict):
                output_text = None

                # Check for output_text from workflow (zzz_pg_openai_workflow returns this)
                if 'output_text' in result_data:
                    output_text = result_data['output_text']
                elif 'output' in result_data:
                    output_text = result_data['output']
                elif 'choices' in result_data and len(result_data['choices']) > 0:
                    choice = result_data['choices'][0]
                    if 'message' in choice:
                        output_text = choice['message'].get('content', '')
                    elif 'text' in choice:
                        output_text = choice['text']

                if output_text:
                    st.markdown("### Generated Content")
                    st.markdown(output_text)

                    # Download button
                    st.download_button(
                        label="Download as Markdown",
                        data=output_text,
                        file_name="blog_post.md",
                        mime="text/markdown"
                    )
                else:
                    st.warning("No output_text found in result")

                # Show raw response in expander
                with st.expander("Raw API Response", expanded=False):
                    st.json(result_data)
            else:
                st.text_area("Result", value=str(result_data), height=400)

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray; padding: 1rem 0;'>
        <p>Powered by OpenAI AgentBuilder | Workflow ID: {}</p>
        </div>
        """.format(Config.WORKFLOW_ID),
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
