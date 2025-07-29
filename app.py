#!/usr/bin/env python3
import streamlit as st
import os
import tempfile
from blog_orchestrator import BlogAgentOrchestrator

def main():
    st.set_page_config(
        page_title="Blog Agents - AI Content Generator",
        page_icon="✍️",
        layout="wide"
    )
    
    st.title("✍️ Blog Agents")
    st.markdown("**AI-powered blog content generation with style matching**")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Your OpenAI API key for the Agents SDK"
        )
        
        # Reference blog input
        reference_blog = st.text_input(
            "Reference Blog/RSS Feed",
            value="",
            placeholder="e.g., YourBlog.com or https://yourblog.com/feed/",
            help="Blog URL or RSS feed to analyze for style matching"
        )
        
        if not api_key:
            st.warning("⚠️ Please enter your OpenAI API key to continue")
            st.stop()
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Content Settings")
        
        # Topic input
        topic = st.text_area(
            "Blog Topic",
            height=100,
            placeholder="Enter your blog topic (e.g., 'The Future of Remote Work')",
            help="The main subject for your blog post"
        )
        
        # Requirements input
        requirements = st.text_area(
            "Additional Requirements",
            height=150,
            placeholder="""- Target audience: [your audience]
- Include practical examples
- Keep under [word count] words
- Add call-to-action
- Focus on [specific aspect]""",
            help="Specific requirements for your blog post"
        )
        
        # Generate button
        generate_button = st.button(
            "🚀 Generate Blog Post",
            type="primary",
            disabled=not (api_key and topic.strip())
        )
    
    with col2:
        st.header("📊 Output")
        
        if generate_button:
            if not topic.strip():
                st.error("❌ Please enter a topic for your blog post")
                return
            
            # Set API key as environment variable temporarily
            os.environ["OPENAI_API_KEY"] = api_key
            
            try:
                # Initialize orchestrator
                orchestrator = BlogAgentOrchestrator()
                
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Callback function to update status
                def update_status(message, progress):
                    status_text.text(message)
                    progress_bar.progress(progress)
                
                # Generate blog post with real-time updates
                results = orchestrator.create_blog_post(
                    topic=topic,
                    reference_blog=reference_blog,
                    requirements=requirements,
                    status_callback=update_status
                )
                
                # Display results
                if "error" in results:
                    st.error(f"❌ Error: {results['error']}")
                else:
                    # Tabs for different outputs
                    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📄 Final Post", "🔗 With Links", "✍️ Draft", "🎨 Style Guide", "🔍 Research"])
                    
                    with tab1:
                        st.markdown("### Final Blog Post")
                        st.markdown(results["final"])
                        
                        # Download button
                        st.download_button(
                            label="📥 Download as Text",
                            data=results["final"],
                            file_name=f"blog_post_{topic[:30].replace(' ', '_')}.txt",
                            mime="text/plain"
                        )
                    
                    with tab2:
                        st.markdown("### Post with Internal Links")
                        st.markdown("*Before final editing - shows added internal links*")
                        if "with_links" in results:
                            st.markdown(results["with_links"])
                        else:
                            st.info("Internal linking data not available")
                    
                    with tab3:
                        st.markdown("### Original Draft")
                        st.markdown("*Before internal linking and editing*")
                        if "draft" in results:
                            st.text_area(
                                "Draft Content",
                                value=results["draft"],
                                height=300,
                                disabled=True
                            )
                        else:
                            st.info("Draft not available")
                    
                    with tab4:
                        st.markdown("### Extracted Style Guide")
                        st.markdown(f"*Style analysis from: {reference_blog}*")
                        st.text_area(
                            "Style Guide",
                            value=results["style_guide"],
                            height=300,
                            disabled=True
                        )
                    
                    with tab5:
                        st.markdown("### Research Data")
                        st.text_area(
                            "Research Results",
                            value=results["research"],
                            height=300,
                            disabled=True
                        )
                        
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.info("💡 Make sure your OpenAI API key is valid and has access to the Agents API")
            
            finally:
                # Clean up environment variable
                if "OPENAI_API_KEY" in os.environ:
                    del os.environ["OPENAI_API_KEY"]
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
        <p>Powered by OpenAI Agents SDK | Built with Streamlit</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()