# Blog Agents 🤖✍️

AI-powered blog content generation with intelligent style matching and multi-agent orchestration.

## Overview

Blog Agents is a sophisticated content generation system that uses multiple AI agents to create high-quality blog posts that match the style and voice of any reference blog or publication. Built with the OpenAI Agents SDK, it provides a comprehensive workflow from style analysis to final SEO optimization.

## Features

### 🎨 **Intelligent Style Matching**
- Analyzes reference blogs to extract writing patterns, tone, and voice
- Matches headline structure, paragraph flow, and vocabulary
- Preserves authentic voice while creating original content

### 🔍 **Comprehensive Research & Analysis**
- Web search integration for up-to-date information
- Content duplication detection to ensure originality
- Multi-perspective research with source validation

### 🤖 **Multi-Agent Architecture**
- **Style Analyzer**: Extracts writing patterns from reference content
- **Content Checker**: Identifies potential duplicates and suggests differentiation
- **Research Specialist**: Gathers relevant facts, statistics, and insights
- **Content Writer**: Creates engaging, well-structured blog posts
- **Internal Linker**: Adds strategic internal links for SEO
- **Content Editor**: Polishes grammar, flow, and readability
- **SEO Analyzer**: Provides actionable SEO recommendations

### 🚀 **Modern Interface**
- Clean Streamlit web interface
- Real-time progress tracking
- Tabbed output for easy content review
- Download functionality for generated content

## Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key with Agents SDK access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tomleelong/BlogAgents.git
   cd BlogAgents
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv openai-agents-env
   source openai-agents-env/bin/activate  # macOS/Linux
   # openai-agents-env\Scripts\activate   # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env to add your OPENAI_API_KEY
   ```

### Usage

#### Web Interface (Recommended)
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`

#### Command Line
```bash
python blog_orchestrator.py
```

## Supported Models

All models support WebSearchTool for style analysis and research:

### GPT-5 Series (Recommended)
- **gpt-5**: Main reasoning model with advanced capabilities
- **gpt-5-mini**: Efficient version with balanced performance
- **gpt-5-nano**: Fastest version for quick generation

### GPT-4 Series
- **gpt-4o**: Flagship multimodal model
- **gpt-4o-mini**: Cost-effective with good performance
- **chatgpt-4o-latest**: Latest updates and improvements

### GPT-4.1 Series
- **gpt-4.1**: Latest flagship coding-optimized model
- **gpt-4.1-mini**: Cost-effective GPT-4.1 variant

## Workflow

1. **Style Analysis**: Analyzes reference blog for writing patterns
2. **Duplication Check**: Searches for existing content on the topic
3. **Research**: Gathers comprehensive information and insights
4. **Content Creation**: Writes blog post matching the analyzed style
5. **Internal Linking**: Adds strategic internal links for SEO
6. **Editing**: Polishes content while preserving style and links
7. **SEO Analysis**: Provides optimization recommendations

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_ORG_ID=your_org_id_here  # Optional
```

### Security Features
- Input validation and sanitization
- URL validation with SSRF protection
- Rate limiting and timeout controls
- Secure API key handling

## Output

The system generates:
- **Final Blog Post**: Polished, style-matched content
- **Style Guide**: Extracted writing patterns and guidelines
- **Research Data**: Comprehensive topic research and insights
- **SEO Analysis**: Actionable optimization recommendations
- **Duplication Report**: Content uniqueness assessment

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on GitHub or contact [Bertram Labs](https://www.bertramlabs.com).

---

**Built with ❤️ by [Bertram Labs](https://www.bertramlabs.com)**

*Professional AI Solutions & Custom Development*