"""
Topic Idea Agent - Generates blog topic ideas based on reference blog analysis.
"""
import asyncio
import os
import re
import logging
from typing import List, Dict, Optional, Callable
from agents import Agent, Runner, WebSearchTool
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration for TopicIdeaAgent."""
    DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_KEYWORDS = 10
    MAX_EXISTING_TOPICS = 50


# Logging setup
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class TopicIdeaAgent:
    """
    Agent for generating blog topic ideas based on reference blog analysis.

    Features:
    - Analyzes reference blog style and content
    - Incorporates trending keywords for SEO
    - Avoids duplicate topics from existing content
    - Supports product/service promotion context
    """

    def __init__(self, model: str = None):
        """
        Initialize the TopicIdeaAgent.

        Args:
            model: OpenAI model to use (defaults to Config.DEFAULT_MODEL)
        """
        self.model = model or Config.DEFAULT_MODEL
        self._agent = None
        self._web_search_tool = WebSearchTool(
            search_context_size="medium",
            user_location={"type": "approximate"}
        )
        logger.info(f"TopicIdeaAgent initialized with model: {self.model}")

    def _get_agent(self):
        """Lazy initialization of the underlying agent."""
        if self._agent is None:
            self._agent = Agent(
                name="topic_generator",
                instructions="""You are a content strategist specializing in blog topic ideation.

Your tasks:
1. Analyze the reference blog to understand their content style and strategy
2. Generate fresh, engaging topic ideas that match their brand voice
3. Incorporate provided keywords naturally into topic suggestions
4. Ensure topics are unique and don't duplicate existing content
5. Consider product/service promotion opportunities when provided

Always provide specific, actionable topic ideas with clear angles and rationale.""",
                model=self.model,
                tools=[self._web_search_tool]
            )
            logger.info("Topic generator agent created")
        return self._agent

    def _build_keyword_context(self, target_keywords: Optional[List[str]]) -> str:
        """
        Build the keyword context section of the prompt.

        Args:
            target_keywords: List of keywords to incorporate

        Returns:
            Formatted keyword context string
        """
        if not target_keywords:
            return ""

        keywords_to_use = target_keywords[:Config.MAX_KEYWORDS]
        logger.info(f"Building keyword context with {len(keywords_to_use)} keywords")

        return f"""

TARGET KEYWORDS TO INCORPORATE:
These keywords should be incorporated into the topic ideas for SEO. Try to build topics around these:
{', '.join(keywords_to_use)}
"""

    def _build_product_context(self, product_target: Optional[str]) -> str:
        """
        Build the product/service context section of the prompt.

        Args:
            product_target: Product/service description or URL to promote

        Returns:
            Formatted product context string
        """
        if not product_target:
            return ""

        logger.info("Building product context")

        return f"""

PRODUCT/SERVICE TO PROMOTE:
{product_target}

IMPORTANT: Create topics that naturally lead to this product as a solution. The content should provide value first, then subtly position the product as helpful. Avoid being overly promotional.
"""

    def _build_duplication_context(self, existing_topics: Optional[List[str]]) -> str:
        """
        Build the duplication avoidance context section of the prompt.

        Args:
            existing_topics: List of existing blog post titles to avoid

        Returns:
            Formatted duplication context string
        """
        if not existing_topics or len(existing_topics) == 0:
            return ""

        topics_sample = existing_topics[:Config.MAX_EXISTING_TOPICS]
        overflow_count = len(existing_topics) - Config.MAX_EXISTING_TOPICS

        logger.info(f"Building duplication context with {len(topics_sample)} topics")

        overflow_text = f"(and {overflow_count} more...)" if overflow_count > 0 else ""

        return f"""

EXISTING BLOG POSTS TO AVOID DUPLICATING:
{chr(10).join(f"- {title}" for title in topics_sample)}
{overflow_text}

CRITICAL: Do NOT suggest topics that are too similar to these existing posts. Generate completely new angles and subjects.
"""

    def _build_prompt(
        self,
        reference_blog: str,
        preferences: str = "",
        target_keywords: Optional[List[str]] = None,
        product_target: Optional[str] = None,
        existing_topics: Optional[List[str]] = None,
        num_topics: int = 5
    ) -> str:
        """
        Build the complete prompt for topic generation.

        Args:
            reference_blog: URL of the blog to analyze
            preferences: User preferences for topic generation
            target_keywords: Keywords to incorporate
            product_target: Product/service to promote
            existing_topics: Topics to avoid duplicating
            num_topics: Number of topics to generate

        Returns:
            Complete formatted prompt string
        """
        keyword_context = self._build_keyword_context(target_keywords)
        product_context = self._build_product_context(product_target)
        duplication_context = self._build_duplication_context(existing_topics)

        prompt = f"""
Generate {num_topics} topic ideas for the blog: {reference_blog}

Additional preferences:
{preferences if preferences else "No specific preferences"}
{keyword_context}
{product_context}
{duplication_context}

Instructions:
1. Quickly search {reference_blog} for 3-5 recent articles to understand their style
2. Generate {num_topics} specific, actionable topic ideas that match their content style
3. Focus on topics they HAVEN'T covered yet - avoid duplicating the existing topics list above
4. If target keywords were provided, prioritize topics that incorporate those high-value keywords
5. If a product target was provided, create topics that naturally allow mentioning/promoting the product while providing genuine value

For EACH topic, use this EXACT format:
## 1. Compelling Title Here
- **Angle**: One sentence unique perspective
- **Keywords**: keyword1, keyword2, keyword3
- **Rationale**: One sentence why this works
- **Content Type**: Guide/Tutorial/Listicle/Case Study

Generate all {num_topics} topics now. Be concise but specific.
"""

        logger.debug(f"Built prompt with {len(prompt)} characters")
        return prompt

    def _parse_topic_ideas(self, raw_output: str) -> List[Dict]:
        """
        Parse the agent's topic ideas output into structured format.

        Args:
            raw_output: Raw text output from the agent

        Returns:
            List of topic dictionaries with title, angle, keywords, rationale, content_type
        """
        topics = []
        lines = raw_output.split('\n')
        current_topic = None

        for line in lines:
            line = line.strip()

            # Match topic title (e.g., "## 1. Title Here" or "1. Title Here")
            title_match = re.match(r'^#{0,2}\s*\d+\.\s*(.+)$', line)
            if title_match:
                # Save previous topic
                if current_topic and current_topic.get('title'):
                    topics.append(current_topic)

                # Start new topic
                current_topic = {
                    'title': title_match.group(1).strip(),
                    'angle': '',
                    'keywords': [],
                    'rationale': '',
                    'content_type': ''
                }
                continue

            if not current_topic:
                continue

            # Extract fields (handle both "- **Field**:" and "**Field**:" formats)
            if line.startswith('- **Angle**:') or line.startswith('**Angle**:'):
                current_topic['angle'] = line.split(':', 1)[1].strip()
            elif line.startswith('- **Keywords**:') or line.startswith('**Keywords**:'):
                keywords_str = line.split(':', 1)[1].strip()
                current_topic['keywords'] = [kw.strip() for kw in keywords_str.split(',')]
            elif line.startswith('- **Rationale**:') or line.startswith('**Rationale**:'):
                current_topic['rationale'] = line.split(':', 1)[1].strip()
            elif line.startswith('- **Content Type**:') or line.startswith('**Content Type**:'):
                current_topic['content_type'] = line.split(':', 1)[1].strip()

        # Don't forget last topic
        if current_topic and current_topic.get('title'):
            topics.append(current_topic)

        logger.info(f"Parsed {len(topics)} topic ideas from output")
        return topics

    async def _run_agent_async(self, prompt: str) -> str:
        """
        Run the agent asynchronously.

        Args:
            prompt: The prompt to send to the agent

        Returns:
            Agent's output string

        Raises:
            Exception: If agent execution fails
        """
        agent = self._get_agent()

        logger.info("Running topic generator agent")

        conversation_input = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt
                    }
                ]
            }
        ]

        result = await Runner.run(agent, input=conversation_input)
        return result.final_output

    def _run_agent_sync(self, prompt: str) -> str:
        """
        Run the agent synchronously (wrapper around async method).

        Args:
            prompt: The prompt to send to the agent

        Returns:
            Agent's output string

        Raises:
            Exception: If agent execution fails
        """
        return asyncio.run(self._run_agent_async(prompt))

    def generate(
        self,
        reference_blog: str,
        preferences: str = "",
        status_callback: Optional[Callable[[str, int], None]] = None,
        target_keywords: Optional[List[str]] = None,
        product_target: Optional[str] = None,
        existing_topics: Optional[List[str]] = None,
        num_topics: int = 5
    ) -> List[Dict]:
        """
        Generate topic ideas for a blog.

        Args:
            reference_blog: URL of the blog to analyze
            preferences: Optional user preferences (industry, audience, content type)
            status_callback: Optional callback for progress updates (message, progress%)
            target_keywords: Optional list of target keywords to incorporate
            product_target: Optional product/service to promote naturally
            existing_topics: Optional list of existing blog post titles to avoid
            num_topics: Number of topics to generate (default: 5)

        Returns:
            List of topic idea dictionaries with keys:
            - title: Topic title
            - angle: Unique perspective
            - keywords: List of target keywords
            - rationale: Why this topic works
            - content_type: Guide/Tutorial/Listicle/Case Study
        """
        try:
            if status_callback:
                status_callback("Analyzing blog and generating topic ideas...", 50)

            logger.info(f"Generating {num_topics} topic ideas for {reference_blog}")

            prompt = self._build_prompt(
                reference_blog=reference_blog,
                preferences=preferences,
                target_keywords=target_keywords,
                product_target=product_target,
                existing_topics=existing_topics,
                num_topics=num_topics
            )

            raw_output = self._run_agent_sync(prompt)

            if status_callback:
                status_callback("Topic ideas generated!", 100)

            topics = self._parse_topic_ideas(raw_output)

            logger.info(f"Successfully generated {len(topics)} topic ideas")
            return topics

        except Exception as e:
            logger.error(f"Error generating topics: {e}")
            if status_callback:
                status_callback(f"Error: {str(e)}", 0)
            raise

    def generate_topic_ideas(self, *args, **kwargs) -> List[Dict]:
        """Alias for generate() method for backward compatibility."""
        return self.generate(*args, **kwargs)
