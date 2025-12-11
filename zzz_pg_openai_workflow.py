from agents import WebSearchTool, RunContextWrapper, Agent, ModelSettings, TResponseInputItem, Runner, RunConfig, trace
from pydantic import BaseModel
from openai.types.shared.reasoning import Reasoning

# Tool definitions
web_search_preview = WebSearchTool(
  search_context_size="medium",
  user_location={
    "type": "approximate"
  }
)
class WritingStyleSchema(BaseModel):
  writing_style_output: str


class TextToJsonSchema(BaseModel):
  existing_blog_posts_to_avoid: list[str]
  high_performing_pages: list[str]
  root_blog_url: str
  seo_keywords: list[str]
  target_product_urls: list[str]
  topics: list[str]
  writing_requirements: str


class ResearchSchema(BaseModel):
  research_output: str


class WriterSchema(BaseModel):
  writer_output: str


class SeoAnalyzerSchema(BaseModel):
  seo_analzyer_first_pass_output: str


class InternalLinksSchema(BaseModel):
  internal_links_output: str


class WritingStyleContext:
  def __init__(self, state_root_blog_url: str, state_high_performing_pages: str):
    self.state_root_blog_url = state_root_blog_url
    self.state_high_performing_pages = state_high_performing_pages
def writing_style_instructions(run_context: RunContextWrapper[WritingStyleContext], _agent: Agent[WritingStyleContext]):
  state_root_blog_url = run_context.context.state_root_blog_url
  state_high_performing_pages = run_context.context.state_high_performing_pages
  return f"""Analyze the writing style of {state_root_blog_url}.

PRIORITY: Analyze these specific high-performing posts first:
{state_high_performing_pages}

These pages should be the PRIMARY examples in your style guide.

Instructions:
1. Search for recent articles from {state_root_blog_url}
2. If specific pages were provided above, analyze those FIRST and prioritize their patterns
3. Analyze multiple articles to identify consistent patterns
4. Extract the publication's distinctive voice and style characteristics
5. Create a detailed style guide that includes specific examples

Focus on recent articles to capture current writing style. """
writing_style = Agent(
  name="Writing Style",
  instructions=writing_style_instructions,
  model="gpt-5.1",
  tools=[
    web_search_preview
  ],
  output_type=WritingStyleSchema,
  model_settings=ModelSettings(
    store=True,
    reasoning=Reasoning(
      effort="high",
      summary="auto"
    )
  )
)


class TextToJsonContext:
  def __init__(self, workflow_input_as_text: str):
    self.workflow_input_as_text = workflow_input_as_text
def text_to_json_instructions(run_context: RunContextWrapper[TextToJsonContext], _agent: Agent[TextToJsonContext]):
  workflow_input_as_text = run_context.context.workflow_input_as_text
  return f"""transform the following to json:
 {workflow_input_as_text}"""
text_to_json = Agent(
  name="text_to_json",
  instructions=text_to_json_instructions,
  model="gpt-5.1",
  output_type=TextToJsonSchema,
  model_settings=ModelSettings(
    store=True,
    reasoning=Reasoning(
      effort="low",
      summary="auto"
    )
  )
)


class ResearchContext:
  def __init__(self, state_topics: str, state_writing_requirements: str, state_target_product_urls: str):
    self.state_topics = state_topics
    self.state_writing_requirements = state_writing_requirements
    self.state_target_product_urls = state_target_product_urls
def research_instructions(run_context: RunContextWrapper[ResearchContext], _agent: Agent[ResearchContext]):
  state_topics = run_context.context.state_topics
  state_writing_requirements = run_context.context.state_writing_requirements
  state_target_product_urls = run_context.context.state_target_product_urls
  return f"""Research the topic: {state_topics}

Requirements:
{state_writing_requirements}

PRODUCT/PAGE TO PROMOTE: 
{state_target_product_urls}                 

Focus your research on:                                     
- Recent developments or trends in this area                
- Facts, statistics, and examples                            
- Unique insights and perspectives
- Practical, actionable information"""
research = Agent(
  name="Research",
  instructions=research_instructions,
  model="gpt-5.1",
  tools=[
    web_search_preview
  ],
  output_type=ResearchSchema,
  model_settings=ModelSettings(
    store=True,
    reasoning=Reasoning(
      effort="high",
      summary="auto"
    )
  )
)


class WriterContext:
  def __init__(self, state_topics: str, state_writing_style: str, state_research: str, state_writing_requirements: str, state_root_blog_url: str):
    self.state_topics = state_topics
    self.state_writing_style = state_writing_style
    self.state_research = state_research
    self.state_writing_requirements = state_writing_requirements
    self.state_root_blog_url = state_root_blog_url
def writer_instructions(run_context: RunContextWrapper[WriterContext], _agent: Agent[WriterContext]):
  state_topics = run_context.context.state_topics
  state_writing_style = run_context.context.state_writing_style
  state_research = run_context.context.state_research
  state_writing_requirements = run_context.context.state_writing_requirements
  state_root_blog_url = run_context.context.state_root_blog_url
  return f"""Write a blog post about: {state_topics}

STYLE GUIDE TO FOLLOW (including formatting patterns):
{state_writing_style}

RESEARCH DATA:
{state_research}

REQUIREMENTS: 
{state_writing_requirements}

CRITICAL FORMATTING INSTRUCTIONS:
1. Write the post to closely match the style and voice of {state_root_blog_url}
2. Use the specific patterns, tone, and techniques identified in the style guide
3. Pay special attention to the FORMATTING GUIDE section - match their heading structure, list usage, and emphasis patterns
4. Output the content in proper markdown format that will render correctly
5. Use the same heading hierarchy (H2, H3, etc.) as shown in the style guide examples
6. Follow their bullet point vs. numbered list preferences
7. Apply bold/italic emphasis in the same way they do

The final output should be properly formatted markdown that matches both the writing style AND visual formatting of {state_root_blog_url}"""
writer = Agent(
  name="Writer",
  instructions=writer_instructions,
  model="gpt-5.1",
  tools=[
    web_search_preview
  ],
  output_type=WriterSchema,
  model_settings=ModelSettings(
    store=True,
    reasoning=Reasoning(
      effort="high",
      summary="auto"
    )
  )
)


class SeoAnalyzerContext:
  def __init__(self, state_writer_draft: str, state_topics: str, state_root_blog_url: str):
    self.state_writer_draft = state_writer_draft
    self.state_topics = state_topics
    self.state_root_blog_url = state_root_blog_url
def seo_analyzer_instructions(run_context: RunContextWrapper[SeoAnalyzerContext], _agent: Agent[SeoAnalyzerContext]):
  state_writer_draft = run_context.context.state_writer_draft
  state_topics = run_context.context.state_topics
  state_root_blog_url = run_context.context.state_root_blog_url
  return f"""Analyze this blog post draft for SEO optimization opportunities:

BLOG POST DRAFT:
{state_writer_draft}

TARGET TOPIC: {state_topics}
PUBLICATION STYLE: {state_root_blog_url}

Provide specific, actionable SEO recommendations for:
1. Heading structure and keyword optimization
2. Content improvements for better search visibility
3. Strategic internal linking opportunities 
4. Meta description suggestions
5. Readability and structure enhancements

Focus on recommendations that can be implemented in the editing phase."""
seo_analyzer = Agent(
  name="SEO Analyzer",
  instructions=seo_analyzer_instructions,
  model="gpt-5.1",
  tools=[
    web_search_preview
  ],
  output_type=SeoAnalyzerSchema,
  model_settings=ModelSettings(
    store=True,
    reasoning=Reasoning(
      effort="high",
      summary="auto"
    )
  )
)


class InternalLinksContext:
  def __init__(self, state_writer_draft: str, state_response_schema_root_blog_url: str, state_seo_analyze_first_pass: str, state_response_schema_topic: str):
    self.state_writer_draft = state_writer_draft
    self.state_response_schema_root_blog_url = state_response_schema_root_blog_url
    self.state_seo_analyze_first_pass = state_seo_analyze_first_pass
    self.state_response_schema_topic = state_response_schema_topic
def internal_links_instructions(run_context: RunContextWrapper[InternalLinksContext], _agent: Agent[InternalLinksContext]):
  state_writer_draft = run_context.context.state_writer_draft
  state_response_schema_root_blog_url = run_context.context.state_response_schema_root_blog_url
  state_seo_analyze_first_pass = run_context.context.state_seo_analyze_first_pass
  state_response_schema_topic = run_context.context.state_response_schema_topic
  return f"""Add strategic internal links to this blog post:

BLOG POST CONTENT:
{state_writer_draft}

WEBSITE/DOMAIN: 
{state_response_schema_root_blog_url}

SEO RECOMMENDATIONS TO CONSIDER:
{state_seo_analyze_first_pass}

CRITICAL Instructions:
1. Use WebSearchTool to search for existing content on {state_response_schema_root_blog_url} that relates to topics in this post
2. Use search queries like: \"site:{state_response_schema_root_blog_url} [{state_response_schema_topic}]\" to find specific pages
3. ONLY use URLs that you find in actual search results - never guess or construct URLs
4. For each link you want to add:
  - Search for the specific topic using site:{state_response_schema_root_blog_url} operator
  - Copy the EXACT URL from the search result
  - Use that exact URL in your markdown link
5. Add 2-5 relevant internal links using natural anchor text (if found)
6. If you cannot find relevant pages via search, it's better to not add a link
7. Use markdown format: [anchor text](EXACT_URL_FROM_SEARCH)
8. Each link MUST be verified through search - no exceptions

Return the blog post with ONLY verified internal links added.  """
internal_links = Agent(
  name="Internal Links",
  instructions=internal_links_instructions,
  model="gpt-5.1",
  tools=[
    web_search_preview
  ],
  output_type=InternalLinksSchema,
  model_settings=ModelSettings(
    store=True,
    reasoning=Reasoning(
      effort="high",
      summary="auto"
    )
  )
)


class EditorContext:
  def __init__(self, state_root_blog_url: str, state_writing_style: str, input_output_parsed_internal_links_output: str, state_seo_analyze_first_pass: str):
    self.state_root_blog_url = state_root_blog_url
    self.state_writing_style = state_writing_style
    self.input_output_parsed_internal_links_output = input_output_parsed_internal_links_output
    self.state_seo_analyze_first_pass = state_seo_analyze_first_pass
def editor_instructions(run_context: RunContextWrapper[EditorContext], _agent: Agent[EditorContext]):
  state_root_blog_url = run_context.context.state_root_blog_url
  state_writing_style = run_context.context.state_writing_style
  input_output_parsed_internal_links_output = run_context.context.input_output_parsed_internal_links_output
  state_seo_analyze_first_pass = run_context.context.state_seo_analyze_first_pass
  return f"""Edit this blog post while preserving the {state_root_blog_url} style and internal links:

ORIGINAL STYLE GUIDE:
{state_writing_style}

DRAFT TO EDIT:
{input_output_parsed_internal_links_output}

SEO RECOMMENDATIONS TO IMPLEMENT:
{state_seo_analyze_first_pass}

Instructions:
- Improve grammar, flow, and clarity while maintaining the distinctive voice and style patterns
- PRESERVE all internal links that have been added
- Implement SEO recommendations where they don't conflict with style preservation
- Optimize headings, keywords, and content structure based on SEO analysis
  - Ensure the content flows naturally around the linked text
  - Don't remove or modify any [anchor text](URL) formatting
  - Balance SEO optimization with authentic brand voice

Return your output as markdown format"""
editor = Agent(
  name="Editor",
  instructions=editor_instructions,
  model="gpt-5.1",
  tools=[
    web_search_preview
  ],
  model_settings=ModelSettings(
    store=True,
    reasoning=Reasoning(
      effort="high",
      summary="auto"
    )
  )
)


class WorkflowInput(BaseModel):
  input_as_text: str


# Main code entrypoint
async def run_workflow(workflow_input: WorkflowInput):
  with trace("blog_agent"):
    state = {
      "response_schema": {
        "existing_blog_posts_to_avoid": [

        ],
        "high_performing_pages": [

        ],
        "root_blog_url": "",
        "seo_keywords": [

        ],
        "target_product_urls": [

        ],
        "topic": ""
      },
      "global": {
        "existing_blog_posts_to_avoid": [

        ],
        "high_performing_pages": [

        ],
        "root_blog_url": "",
        "seo_keywords": [

        ],
        "target_product_urls": [

        ],
        "topic": ""
      },
      "existing_blog_posts_to_avoid": [

      ],
      "high_performing_pages": [

      ],
      "root_blog_url": None,
      "seo_keywords": [

      ],
      "target_product_urls": [

      ],
      "topics": [

      ],
      "writing_style": None,
      "writing_requirements": None,
      "research": None,
      "writer_draft": None,
      "seo_analyze_first_pass": None,
      "internal_links": None,
      "edit_output": None
    }
    workflow = workflow_input.model_dump()
    conversation_history: list[TResponseInputItem] = [
      {
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": workflow["input_as_text"]
          }
        ]
      }
    ]
    text_to_json_result_temp = await Runner.run(
      text_to_json,
      input=[
        *conversation_history
      ],
      run_config=RunConfig(trace_metadata={
        "__trace_source__": "agent-builder",
        "workflow_id": "wf_692e0fdc02508190b3b51b94f2b7deea0f87a40e1a3b5c93"
      }),
      context=TextToJsonContext(workflow_input_as_text=workflow["input_as_text"])
    )
    text_to_json_result = {
      "output_text": text_to_json_result_temp.final_output.json(),
      "output_parsed": text_to_json_result_temp.final_output.model_dump()
    }
    state["existing_blog_posts_to_avoid"] = text_to_json_result["output_parsed"]["existing_blog_posts_to_avoid"]
    state["high_performing_pages"] = text_to_json_result["output_parsed"]["high_performing_pages"]
    state["root_blog_url"] = text_to_json_result["output_parsed"]["root_blog_url"]
    state["seo_keywords"] = text_to_json_result["output_parsed"]["seo_keywords"]
    state["target_product_urls"] = text_to_json_result["output_parsed"]["target_product_urls"]
    state["topics"] = text_to_json_result["output_parsed"]["topics"]
    state["writing_requirements"] = text_to_json_result["output_parsed"]["writing_requirements"]
    writing_style_result_temp = await Runner.run(
      writing_style,
      input=[
        *conversation_history
      ],
      run_config=RunConfig(trace_metadata={
        "__trace_source__": "agent-builder",
        "workflow_id": "wf_692e0fdc02508190b3b51b94f2b7deea0f87a40e1a3b5c93"
      }),
      context=WritingStyleContext(state_root_blog_url=state["root_blog_url"], state_high_performing_pages=state["high_performing_pages"])
    )
    writing_style_result = {
      "output_text": writing_style_result_temp.final_output.json(),
      "output_parsed": writing_style_result_temp.final_output.model_dump()
    }
    state["writing_style"] = writing_style_result["output_parsed"]["writing_style_output"]
    research_result_temp = await Runner.run(
      research,
      input=[
        *conversation_history
      ],
      run_config=RunConfig(trace_metadata={
        "__trace_source__": "agent-builder",
        "workflow_id": "wf_692e0fdc02508190b3b51b94f2b7deea0f87a40e1a3b5c93"
      }),
      context=ResearchContext(state_topics=state["topics"], state_writing_requirements=state["writing_requirements"], state_target_product_urls=state["target_product_urls"])
    )
    research_result = {
      "output_text": research_result_temp.final_output.json(),
      "output_parsed": research_result_temp.final_output.model_dump()
    }
    state["research"] = research_result["output_parsed"]["research_output"]
    writer_result_temp = await Runner.run(
      writer,
      input=[
        *conversation_history
      ],
      run_config=RunConfig(trace_metadata={
        "__trace_source__": "agent-builder",
        "workflow_id": "wf_692e0fdc02508190b3b51b94f2b7deea0f87a40e1a3b5c93"
      }),
      context=WriterContext(state_topics=state["topics"], state_writing_style=state["writing_style"], state_research=state["research"], state_writing_requirements=state["writing_requirements"], state_root_blog_url=state["root_blog_url"])
    )
    writer_result = {
      "output_text": writer_result_temp.final_output.json(),
      "output_parsed": writer_result_temp.final_output.model_dump()
    }
    state["writer_draft"] = writer_result["output_parsed"]["writer_output"]
    seo_analyzer_result_temp = await Runner.run(
      seo_analyzer,
      input=[
        *conversation_history
      ],
      run_config=RunConfig(trace_metadata={
        "__trace_source__": "agent-builder",
        "workflow_id": "wf_692e0fdc02508190b3b51b94f2b7deea0f87a40e1a3b5c93"
      }),
      context=SeoAnalyzerContext(state_writer_draft=state["writer_draft"], state_topics=state["topics"], state_root_blog_url=state["root_blog_url"])
    )
    seo_analyzer_result = {
      "output_text": seo_analyzer_result_temp.final_output.json(),
      "output_parsed": seo_analyzer_result_temp.final_output.model_dump()
    }
    state["seo_analyze_first_pass"] = seo_analyzer_result["output_parsed"]["seo_analzyer_first_pass_output"]
    internal_links_result_temp = await Runner.run(
      internal_links,
      input=[
        *conversation_history
      ],
      run_config=RunConfig(trace_metadata={
        "__trace_source__": "agent-builder",
        "workflow_id": "wf_692e0fdc02508190b3b51b94f2b7deea0f87a40e1a3b5c93"
      }),
      context=InternalLinksContext(state_writer_draft=state["writer_draft"], state_response_schema_root_blog_url=state["response_schema"]["root_blog_url"], state_seo_analyze_first_pass=state["seo_analyze_first_pass"], state_response_schema_topic=state["response_schema"]["topic"])
    )
    internal_links_result = {
      "output_text": internal_links_result_temp.final_output.json(),
      "output_parsed": internal_links_result_temp.final_output.model_dump()
    }
    state["internal_links"] = internal_links_result["output_parsed"]["internal_links_output"]
    editor_result_temp = await Runner.run(
      editor,
      input=[
        *conversation_history
      ],
      run_config=RunConfig(trace_metadata={
        "__trace_source__": "agent-builder",
        "workflow_id": "wf_692e0fdc02508190b3b51b94f2b7deea0f87a40e1a3b5c93"
      }),
      context=EditorContext(state_root_blog_url=state["root_blog_url"], state_writing_style=state["writing_style"], input_output_parsed_internal_links_output=internal_links_result["output_parsed"]["internal_links_output"], state_seo_analyze_first_pass=state["seo_analyze_first_pass"])
    )
    editor_result = {
      "output_text": editor_result_temp.final_output_as(str)
    }
    return editor_result
