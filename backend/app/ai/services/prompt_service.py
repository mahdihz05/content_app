class PromptService:
    """
    سرویس مدیریت مگا-پرامپت‌ها برای مراحل مختلف تولید محتوا.
    تمام خروجی‌ها برای پردازش راحت‌تر در لایه‌های بعدی، به صورت JSON (یا متن کنترل‌شده) درخواست شده‌اند.
    """

    # =========================
    # 1) RESEARCH: تحلیل اولیه کیورد
    # =========================
    @staticmethod
    def get_research_prompt(keyword, language="Persian"):
        return f"""
You are a Senior SEO Strategist and Topic Researcher.
Your job is to deeply analyze the following keyword and provide structured insights for high-quality content planning.

Target Keyword: "{keyword}"

INSTRUCTIONS:
- Think step by step.
- Base your reasoning on real-world SEO and SERP behavior.
- Do NOT add any explanation outside the JSON.
- Make sure the JSON is valid and can be parsed by a standard JSON parser.
- Do NOT include trailing commas.

TASKS:
1) Search Intent:
   - Determine the dominant search intent for this keyword.
   - One of: "Informational", "Transactional", "Navigational", "Commercial Investigation".
2) Target Audience:
   - Describe who is searching for this keyword (job role, level, needs, pain points).
3) Competitor Gap Overview:
   - List up to 5 important sub-topics that top-ranking pages usually cover.
   - Then list 3–5 angle ideas or gaps that are often missing and can be used to stand out.
4) Semantic / LSI Keywords:
   - Provide a list of 10–20 LSI / NLP-related keywords and phrases for "{keyword}".
5) Key Takeaways:
   - List 5–7 crucial insights or points that MUST be included in the final content.
6) Suggested Title:
   - Propose 1 strong SEO title that is attractive and click-worthy.

OUTPUT FORMAT (STRICT JSON ONLY):

{{
  "search_intent": "Informational | Transactional | Navigational | Commercial Investigation",
  "target_audience": "string describing audience profile",
  "competitor_subtopics": [
    "subtopic 1",
    "subtopic 2"
  ],
  "gap_opportunities": [
    "angle or gap 1",
    "angle or gap 2"
  ],
  "key_takeaways": [
    "point 1",
    "point 2"
  ],
  "lsi_keywords": [
    "lsi keyword 1",
    "lsi keyword 2"
  ],
  "suggested_title": "SEO-friendly blog post title"
}}

Language: Respond in {language}.
"""

    # =========================
    # 2) SEARCH QUERIES: تولید کوئری برای سرچ
    # =========================
    @staticmethod
    def get_search_queries_prompt(
            topic_title,
            main_keyword,
            language="Persian",
            count=5,
            existing_queries=None
    ):

        existing_queries = existing_queries or []

        return f"""
    You are an SEO research assistant that generates realistic Google search queries.

    Your task is to simulate how real users search on Google when researching a topic.

    =====================
    INPUT
    =====================

    Topic Title:
    "{topic_title}"

    Main Keyword:
    "{main_keyword}"

    Language:
    {language}

    Number of queries to generate:
    {count}

    Existing queries (DO NOT repeat these):
    {existing_queries}

    =====================
    GOAL
    =====================

    Generate {count} realistic Google search queries that a user might type when
    trying to research this topic.

    The queries must look like **real Google searches**, not SEO keywords.

    They will later be used for:
    - web search
    - web scraping
    - research discovery

    So they must feel natural and realistic.

    =====================
    QUERY REQUIREMENTS
    =====================

    Queries should:

    • be short and clear  
    • be understandable at first glance  
    • resemble real Google searches  
    • vary in perspective and intent  
    • cover different angles of the topic  
    • avoid duplicates  
    • avoid repeating the same structure

    Include a mix of intents such as:

    • informational  
    • how-to  
    • beginner questions  
    • common problems  
    • comparisons  
    • best practices  
    • tools or strategies

    Queries should NOT all look the same.

    =====================
    LANGUAGE RULE
    =====================

    If the topic and keyword are Persian → generate Persian queries.

    If the topic and keyword are English → generate English queries.

    Do NOT mix languages.

    =====================
    REALISM
    =====================

    Queries should resemble things people actually type into Google.

    Examples of style (NOT actual answers):

    good examples:
    - how to learn python for beginners
    - best seo tools for small websites
    - چرا سایت در گوگل ایندکس نمی شود
    - آموزش تحقیق کلمات کلیدی سئو

    bad examples:
    - seo_keyword_research_guide
    - keyword research optimization strategy advanced

    =====================
    OUTPUT FORMAT
    =====================

    Return ONLY valid JSON:

    {{
      "queries": [
        "query 1",
        "query 2",
        "query 3"
      ]
    }}

    Rules:

    - Do NOT include explanations
    - Do NOT include markdown
    - Do NOT include text outside JSON
    - Ensure valid JSON
    """

    # =========================
    # 3) FETCH SOURCE DATA: شبیه‌سازی اسکرپ گوگل برای یک کوئری
    # =========================
    @staticmethod
    def get_fetch_source_data_prompt(source_title, main_keyword=None, language="Persian"):
        extra_kw = f'Main keyword (if relevant): "{main_keyword}".' if main_keyword else ""
        return f"""
    You are simulating a real, high-quality, top-ranking article from a reputable website
    for the following search query:

    Search query/title: "{source_title}"
    {extra_kw}

    ROLE:
    - Act as a professional content writer producing an article that feels like it exists on a real website.
    - The article must sound natural, well-researched, and similar to content ranking in Google top 3.
    - This is synthetic research only; not intended for direct publication.

    ARTICLE REQUIREMENTS:
    1) LENGTH:
       - Write a long, comprehensive article of 1200–1800 words.

    2) STRUCTURE (NO MARKDOWN HEADINGS):
       - Use clear sectioning separated by double newlines.
       - Each section should have an implicit heading (in plain text, NOT markdown).
       - Maintain natural web-article style: short paragraphs, flowing narrative.

    3) CONTENT STYLE:
       - Write as if published by a high-authority website.
       - Provide explanations, examples, and practical guidelines.
       - Include semi-realistic data or examples (e.g. “در یک نظرسنجی سال ۲۰۲۳ اشاره شد که…”).
       - Avoid exact verifiable facts or fake statistics.
       - Avoid claims requiring citations.
       - Sound credible, helpful, and structured.

    4) SUMMARY:
       - Provide a concise 4–6 sentence summary.
       - Summarize the article’s core points, angle, and primary insights.

    OUTPUT FORMAT (STRICT JSON ONLY):

    {{
      "raw_text": "full article text in {language}, sections separated by \\n\\n",
      "summary": "4–6 sentence summary in {language}"
    }}

    RULES:
    - Do NOT include any text outside JSON.
    - Do NOT use markdown.
    - Do NOT include unescaped quotes.
    Language: Respond in {language}.
    """

    # =========================
    # 4) MERGE RESEARCH: ادغام چند منبع تحقیق در یک تحقیق نهایی
    # =========================
    @staticmethod
    def get_merge_research_prompt(research_items, topic_title, main_keyword, language="Persian"):
        """
        research_items: رشته‌ی JSON (لیست از {id, title, summary, raw_text}) که از بک‌اند پاس داده می‌کنی.
        """
        return f"""
You are a Senior Research Synthesizer.

Your job is to read multiple research sources and synthesize them into one clean, de-duplicated,
high-value research summary that will be used to generate a final article.

TOPIC CONTEXT:
- Content title: "{topic_title}"
- Main keyword: "{main_keyword}"

RESEARCH SOURCES (JSON LIST):
{research_items}

EACH SOURCE ITEM HAS:
- id
- title
- summary
- raw_text

TASKS:
1) Global Understanding:
   - Understand the main ideas covered across all sources.
2) Deduplication:
   - Remove duplicated/overlapping information.
3) Conflict Handling:
   - If sources disagree, briefly note the disagreement and pick the most reliable/common view.
4) Final Synthesized Notes:
   - Produce a set of structured notes that cover all important angles without repetition.
5) Key Stats / Facts (if any):
   - Extract concrete numbers, stats, or facts that are valuable.

OUTPUT FORMAT (STRICT JSON ONLY):

{{
  "high_level_summary": "2-4 paragraph overview in {language}.",
  "structured_notes": [
    {{
      "heading": "subtopic or theme",
      "summary": "short explanation in {language}",
      "key_points": [
        "bullet point 1",
        "bullet point 2"
      ]
    }}
  ],
  "conflicts_or_caveats": [
    "optional note about conflicting info or caveats"
  ],
  "important_stats": [
    "if any, list key stats/facts, otherwise empty array"
  ]
}}

RULES:
- Do NOT copy full raw_text; instead, paraphrase and synthesize.
- Do NOT add any explanation outside JSON.
Language: Respond in {language}.
"""

    # =========================
    # 5) OUTLINE: بر اساس تحقیق ادغام‌شده
    # =========================
    @staticmethod
    def get_final_content_prompt(
            title,
            main_keyword,
            additional_keywords_json,
            description,
            goal,
            language,
            writer_persona,
            target_length,
            information_json,
            merged_research_json
    ):
        """
        تولید مگا پرامپت نهایی تولید محتوای وب‌سایت
        """

        return f"""
    You are an Elite Content Writer, SEO Architect, and Narrative Strategist.

    Your task is to generate a complete, polished, SEO‑optimized HTML article for a website.
    The article must be written using the following structured inputs, with weighted importance and content‑quality rules.

    ------------------------------------------------------
    USER INPUT DATA (Structured)
    ------------------------------------------------------

    CONTENT DATA:
    - Title: "{title}"
    - Main Keyword: "{main_keyword}"
    - Additional Keywords: {additional_keywords_json}
    - Description (user intent): "{description}"
    - Goal (high priority): "{goal}"
    - Language: "{language}"
    - Writer Persona: "{writer_persona}"
    - Target Content Length: {target_length} words
    - Extra Metadata / Information: {information_json}
    - Platform: "website"

    RESEARCH KNOWLEDGE BASE:
    (High priority for factual grounding, depth, structure)
    {merged_research_json}

    ------------------------------------------------------
    WRITING OBJECTIVE
    ------------------------------------------------------

    Generate a complete website article that:
    - Fully matches the *goal* of the content (highest weight).
    - Uses the user-provided description to infer tone, audience level, and formality.
    - Uses the research knowledge base to extract insights and enrich the article.
    - Uses the main keyword as SEO anchor, and additional keywords naturally.
    - Uses the writer persona as narrative voice.
    - Matches the requested target length.
    - Produces a ready-to-publish clean HTML output.

    ------------------------------------------------------
    TONE & STYLE RULES
    ------------------------------------------------------

    - Default tone: formal  
    - If topic or description requires conversational tone → adapt automatically  
    - Follow the specified writer persona  
    - Avoid filler and generic content  
    - Avoid keyword stuffing  
    - Use short readable paragraphs  
    - Use examples, storytelling, and frameworks where helpful  
    - Maintain coherence and narrative flow  

    ------------------------------------------------------
    SEO RULES
    ------------------------------------------------------

    Mandatory elements:
    - One H1
    - Multiple H2 sections
    - Optional H3 subsections
    - SEO‑friendly intro and conclusion
    - Meta Title + Meta Description
    - Natural use of semantic keywords (LSI)
    - Address search intent clearly
    - Include "People Also Ask" style subsections
    - Add FAQ section with schema-friendly Q/A
    - Suggest internal link anchors (no URLs)
    - Maintain natural keyword density

    ------------------------------------------------------
    RESEARCH USAGE RULES
    ------------------------------------------------------

    From merged_research_json:
    - Extract important insights
    - Combine relevant points
    - Avoid factual errors
    - Integrate research naturally
    - Expand argumentation with supported reasoning
    - Never explicitly mention the research data in the article

    ------------------------------------------------------
    HTML OUTPUT RULES
    ------------------------------------------------------

    Return a clean HTML article:
    - Use standard tags only:
      <h1>, <h2>, <h3>, <p>, <ul>, <li>, <blockquote>, <strong>, <em>
    - No inline CSS unless necessary
    - Wrap entire content inside <article> ... </article>

    Include at the top:
    - meta title
    - meta description

    Return only one final article.

    ------------------------------------------------------
    OPTIONAL IMAGE SUPPORT
    ------------------------------------------------------

    Also generate optional image prompts:
    - 1 hero/banner image
    - 1–2 inline image prompts

    Prompts must be in English and suitable for image generation models.

    ------------------------------------------------------
    FINAL OUTPUT FORMAT (STRICT JSON)
    ------------------------------------------------------

    Return ONLY:

    {{
      "meta": {{
        "title": "...",
        "description": "..."
      }},
      "html": "<article> ... FULL HTML CONTENT ... </article>",
      "images": [
        "hero image prompt",
        "inline image prompt"
      ]
    }}

    No commentary outside this JSON.

    ------------------------------------------------------
    BEHAVIOR RULES
    ------------------------------------------------------

    - If user input is incomplete → infer intelligently.
    - Never ask questions.
    - Never show warnings.
    - Never break JSON format.
    - Produce fully polished final HTML content.

    ------------------------------------------------------
    NOW GENERATE THE FINAL ARTICLE
    ------------------------------------------------------

    Write the full optimized HTML article in {language} using all rules above.

    """

    # =========================
    # 6) GENERATION: تولید متن نهایی از روی اوت‌لاین + تحقیق
    # =========================

    # ==========================================================
    # MULTI-PLATFORM FINAL GENERATION PROMPT
    # ==========================================================
    @staticmethod
    def get_final_generation_prompt(platform,
                                    outline_json,
                                    merged_research_json,
                                    tone="Professional",
                                    language="Persian"):
        """
        انتخاب هوشمند پرامپت نهایی بر اساس پلتفرم هدف
        platforms supported:
        - instagram
        - website (default)
        """

        # -----------------------------
        # PLATFORM: INSTAGRAM
        # -----------------------------
        if platform and platform.lower() == "instagram":
            return f"""
You are a Professional Instagram Content Creator.

Your task is to generate a complete Instagram post based on:
- the structured outline
- the merged research insights

The output must simulate a REAL Instagram post including:
1) A suggested main visual concept (image or short video idea)
2) A compelling caption (3–8 lines, mobile-friendly)
3) Optional mini storytelling or hook
4) CTA relevant to the topic
5) A clean list of 5–12 hashtags
6) Do NOT use Markdown
7) Output STRICT JSON ONLY

OUTLINE (JSON):
{outline_json}

SYNTHESIZED RESEARCH (JSON):
{merged_research_json}

OUTPUT FORMAT (STRICT JSON):
{{
  "visual_idea": "short description for image or video concept in {language}",
  "caption": "3–8 line caption in {language}, mobile-friendly, no markdown, no emojis unless natural",
  "cta": "call to action in {language}",
  "hashtags": [
    "#tag1",
    "#tag2",
    "#tag3"
  ]
}}

RULES:
- No text outside JSON.
- No Markdown.
Language: Respond in {language}.
"""

        # ---------------------------------------------------------
        # DEFAULT (WEBSITE / BLOG / UNKNOWN PLATFORM)
        # ---------------------------------------------------------
        return f"""
You are a World-Class Copywriter and SEO Expert.

Your task is to write a deep, engaging, and high-value article based on:
- the final outline
- the synthesized research

CONTEXT:
- Tone/style: {tone}
- Writing language: {language}

OUTLINE (JSON):
{outline_json}

SYNTHESIZED RESEARCH (JSON):
{merged_research_json}

WRITING GUIDELINES:
- Write HTML only (<h2>, <h3>, <p>, <ul>, <li>, <strong>, <em>)
- No Markdown.
- Follow the outline structure strictly.
- Use short paragraphs and bullet points.
- Integrate research insights.
- No extra text outside HTML.

OUTPUT FORMAT:
- Return ONLY valid HTML code.
- No extra comments, no meta explanations.
Language: Write the article in {language}.
"""

    # =========================
    # 7) SEO METADATA: متاتایتل، دیسکریپشن، اسلاگ
    # =========================
    @staticmethod
    def get_seo_metadata_prompt(content, language="Persian"):
        return f"""
You are an SEO Specialist.

Based on the following article content, generate optimized meta tags.

ARTICLE CONTENT (TRUNCATED):
\"\"\" 
{content[:2000]}
\"\"\"

TASKS:
1) Meta Title:
   - Under 60 characters.
   - Include the main topic/keyword.
   - Make it compelling and click-worthy.
2) Meta Description:
   - Under 160 characters.
   - Summarize the value of the article.
   - Encourage clicks (use benefit + curiosity, avoid clickbait).
3) URL Slug:
   - Short, lowercase, hyphen-separated.
   - No stop words if possible.
4) Tags:
   - 5 to 8 relevant topical tags/labels.

OUTPUT FORMAT (STRICT JSON ONLY):

{{
  "meta_title": "string under 60 characters in {language}",
  "meta_description": "string under 160 characters in {language}",
  "slug": "url-friendly-slug-in-english-or-transliterated",
  "tags": [
    "tag 1",
    "tag 2",
    "tag 3"
  ]
}}

RULES:
- Do NOT output anything outside the JSON.
Language: Respond in {language}.
"""

    # =========================
    # 8) SUMMARY: خلاصه کوتاه یا کپشن شبکه اجتماعی
    # =========================
    @staticmethod
    def get_summary_prompt(content, platform="generic", language="Persian"):
        """
        platform: مثلا "LinkedIn", "Instagram", "Twitter" (X), ...
        """
        return f"""
You are a Copywriter specialized in summarizing long-form content into short, punchy summaries.

ARTICLE CONTENT (TRUNCATED):
\"\"\" 
{content[:1200]}
\"\"\"

GOAL:
- Create a short, engaging summary that could be used as a social media post or teaser.
- Platform: {platform} (adapt the tone slightly if relevant).

GUIDELINES:
- 1–3 short paragraphs OR 3–6 bullet points.
- Include the core benefit or insight of the article.
- Avoid hashtags unless they are naturally helpful (no more than 3).
- No emojis unless they truly fit the platform tone.

OUTPUT:
- Return ONLY the text of the summary in {language}, no JSON, no explanations.
"""

    # =========================
    # 9) KEYWORD GENERATION: ست کامل کیوردها
    # =========================
    @staticmethod
    def get_keyword_generation_prompt(form_data, language="Persian"):
        return f"""
You are a professional SEO Keyword Strategist.

Your task is to generate a comprehensive keyword set for a content piece based on the structured information provided.

CONTENT INPUT DATA (JSON-LIKE):
{form_data}

INSTRUCTIONS:

1) Analyze the provided data carefully:
   - Topic/title
   - Audience
   - Goal/intent
   - Industry/niche
2) Understand the search intent behind the content.
3) Generate SEO keywords that can help this content rank well in search engines.
4) Include multiple types of keywords:
   - Primary keyword (1)
   - Secondary keywords (5–10)
   - Long-tail keywords (5–15)
   - Question-based keywords (for FAQ and featured snippets) (5–10)
   - Semantic / LSI keywords (10–20)
5) Keywords should reflect real search intent and natural language queries.
6) Avoid duplicates.
7) Prefer phrases users actually type in Google.

OUTPUT FORMAT (STRICT JSON):

{{
  "primary_keyword": "one main keyword phrase",
  "secondary_keywords": [
    "secondary keyword 1",
    "secondary keyword 2"
  ],
  "long_tail_keywords": [
    "long tail keyword 1",
    "long tail keyword 2"
  ],
  "question_keywords": [
    "question keyword 1",
    "question keyword 2"
  ],
  "lsi_keywords": [
    "lsi keyword 1",
    "lsi keyword 2"
  ]
}}

RULES:
- Do NOT output anything outside the JSON.
Language: Respond in {language}.
"""

    # =========================
    # 10) QUALITY / POLISH: بازنویسی و بهبود نهایی متن
    # =========================
    @staticmethod
    def get_quality_enhancement_prompt(content, tone="Professional", language="Persian"):
        return f"""
You are a Senior Editor and Style Specialist.

Your task is to revise and polish the following article, improving:
- clarity
- flow and coherence
- readability
- tone consistency ({tone})
- grammar and spelling

ARTICLE DRAFT:
\"\"\" 
{content[:8000]}
\"\"\"

GUIDELINES:
- Keep the meaning and structure, but improve phrasing where useful.
- Break long sentences into shorter, clearer ones.
- Use smooth transitions between paragraphs.
- Remove redundancy and generic filler.
- Keep or improve headings (if present).
- Preserve Markdown formatting if the original text is in Markdown.
- Do NOT shorten the text aggressively; preserve most of the detail.

OUTPUT:
- Return ONLY the improved article text in {language}.
- Maintain Markdown if present.
"""

    @staticmethod
    def get_outline_prompt(topic_title, main_keyword, merged_research_json,
                           goal=None, platform=None, form_schema_data=None,
                           language="Persian"):
        """
        merged_research_json: خروجی get_merge_research_prompt به‌صورت string
        form_schema_data: JSON string شامل فرم داینامیک محتوای خاص
        (مثلاً تعداد کلمه، audience, tone, extra constraints)
        """
        goal_text = f"- Content goal: \"{goal}\"" if goal else ""
        platform_text = f"- Target platform: \"{platform}\"" if platform else ""
        form_text = f"- Additional structured form data (JSON): {form_schema_data}" if form_schema_data else ""

        return f"""
You are a Content Architect and SEO Strategist.

Your task is to create a comprehensive, SEO-optimized outline for a content piece.

TOPIC:
- Title: "{topic_title}"
- Main keyword: "{main_keyword}"
{goal_text}
{platform_text}
{form_text}

RESEARCH SYNTHESIS (JSON):
{merged_research_json}

GUIDELINES:
- Use a logical narrative flow: Introduction → Core Sections → Advanced / Examples → Conclusion.
- Include H1 (only one), multiple H2, and optional H3 subsections.
- Each section should have a clear purpose.
- Make it suitable for ranking for "{main_keyword}" and related queries.
- Adapt depth, structure and angle to the content goal and platform if provided.
- Aim for a depth suitable for a 2000–3000 word article (if topic needs it).
- For each heading, add a short description or goal.
- Make sure to naturally cover key ideas from "structured_notes".

OUTPUT FORMAT (STRICT JSON):

{{
  "outline": [
    {{
      "tag": "H1",
      "title": "main article title",
      "description": "what this article will cover overall"
    }},
    {{
      "tag": "H2",
      "title": "section title",
      "description": "goal/purpose of this section",
      "subsections": [
        {{
          "tag": "H3",
          "title": "subsection title",
          "goal": "what this part explains",
          "notes": [
            "optional bullet note 1",
            "optional bullet note 2"
          ]
        }}
      ]
    }}
  ],
  "recommended_length_words": 2200
}}

RULES:
- Do NOT output anything outside the JSON.
Language: Respond in {language}.
"""




    @staticmethod
    def get_outline_improvement_prompt(current_outline_json, feedback_text,
                                       topic_title=None, main_keyword=None,
                                       language="Persian"):
        """
        استفاده برای زمانی که کاربر اوت‌لاین را ادیت کرده یا فیدبک داده:
        - current_outline_json: اوت‌لاین فعلی
        - feedback_text: توضیح کاربر مثل "بخش مقدماتی را کوتاه‌تر کن و مثال‌های عملی اضافه کن"
        """
        topic_info = ""
        if topic_title:
            topic_info += f'- Title: "{topic_title}"\n'
        if main_keyword:
            topic_info += f'- Main keyword: "{main_keyword}"\n'

        return f"""
You are an Expert Content Architect.

Your job is to revise and improve an existing article outline based on user feedback.

TOPIC CONTEXT (optional):
{topic_info}

CURRENT OUTLINE (JSON):
{current_outline_json}

USER FEEDBACK / EDIT INSTRUCTIONS:
\"\"\"{feedback_text}\"\"\"

TASKS:
1) Understand the current outline structure (H1, H2, H3).
2) Apply the user feedback carefully while preserving any good structure that already exists.
3) Improve flow, remove redundancies, and ensure a logical narrative.
4) If needed, merge or split sections for better clarity and reader experience.

OUTPUT FORMAT (STRICT JSON):

{{
  "outline": [
    {{
      "tag": "H1",
      "title": "main article title",
      "description": "what this article will cover overall"
    }},
    {{
      "tag": "H2",
      "title": "section title",
      "description": "goal/purpose of this section",
      "subsections": [
        {{
          "tag": "H3",
          "title": "subsection title",
          "goal": "what this part explains",
          "notes": [
            "optional bullet note 1",
            "optional bullet note 2"
          ]
        }}
      ]
    }}
  ],
  "recommended_length_words": 2200
}}

RULES:
- Keep the output valid JSON.
- Do NOT add any explanation outside the JSON.
Language: Respond in {language}.
"""



    @staticmethod
    def get_section_generation_prompt(full_outline_json,
                                      merged_research_json,
                                      target_section_id_or_title,
                                      tone="Professional",
                                      language="Persian"):
        """
        برای رجنریت/تولید فقط یک بخش (مثلا یک H2 یا H3)
        - target_section_id_or_title: می‌تواند یک ID داخلی خودمان یا title دقیق بخش باشد
        """
        return f"""
You are a World-Class Copywriter and SEO Expert.

Your task is to write ONLY ONE SECTION of an article based on:
- the full outline (for context)
- the synthesized research
- the target section identifier

CONTEXT:
- Tone/style: {tone}
- Writing language: {language}

FULL OUTLINE (JSON):
{full_outline_json}

SYNTHESIZED RESEARCH (JSON):
{merged_research_json}

TARGET SECTION IDENTIFIER:
"{target_section_id_or_title}"

INSTRUCTIONS:
- First, locate the target section in the outline by its id/title.
- Write only the content for this specific section (including any sub-parts if relevant).
- Do NOT repeat the main H1 introduction or conclusion unless the target section is that part.
- Use Markdown headings appropriate for the section level (## or ###).
- Use short paragraphs and bullet points where helpful.
- Integrate relevant research insights and stats from the synthesized research.
- Maintain consistent tone and style with the rest of the article.

OUTPUT FORMAT:
- Return ONLY the Markdown content for the target section.
- Do NOT include JSON or any explanations.
Language: Write the section in {language}.
"""




    @staticmethod
    def get_quality_evaluation_prompt(content,
                                      main_keyword=None,
                                      goal=None,
                                      platform=None,
                                      language="Persian"):
        """
        برای scoring کیفیت متن.
        """
        kw_text = f'- Main keyword: "{main_keyword}"' if main_keyword else ""
        goal_text = f'- Content goal: "{goal}"' if goal else ""
        platform_text = f'- Platform: "{platform}"' if platform else ""

        return f"""
You are an Expert Content Quality Analyst.

Your task is to evaluate the following article and provide a structured quality assessment.

CONTEXT:
{kw_text}
{goal_text}
{platform_text}

ARTICLE:
\"\"\" 
{content[:8000]}
\"\"\" 

EVALUATION DIMENSIONS:
1) Overall quality (1–10)
2) Clarity & readability (1–10)
3) Depth & usefulness (1–10)
4) Structure & flow (1–10)
5) SEO alignment with main topic/keyword (1–10)
6) Tone consistency (1–10)
7) Potential issues:
   - redundancy
   - vagueness
   - missing key aspects
   - possible factual risks (if any)

OUTPUT FORMAT (STRICT JSON ONLY):

{{
  "overall_score": 8,
  "clarity_readability": 8,
  "depth_usefulness": 8,
  "structure_flow": 8,
  "seo_alignment": 8,
  "tone_consistency": 8,
  "strengths": [
    "strength 1",
    "strength 2"
  ],
  "weaknesses": [
    "weakness 1",
    "weakness 2"
  ],
  "recommended_improvements": [
    "concrete suggestion 1",
    "concrete suggestion 2"
  ],
  "factual_risk_notes": [
    "optional note if any factual uncertainty"
  ]
}}

RULES:
- Use integers 1–10 for scores.
- Do NOT output anything outside the JSON.
Language: Respond in {language}.
"""



    @staticmethod
    def get_brand_voice_extraction_prompt(sample_text, language="Persian"):
        """
        وقتی کاربر چند پاراگراف متن برندش را می‌دهد.
        """
        return f"""
You are a Brand Voice Strategist.

Your task is to analyze the following brand content and extract a reusable brand voice guideline.

SAMPLE BRAND CONTENT:
\"\"\" 
{sample_text[:6000]}
\"\"\" 

TASKS:
1) Identify tone and style characteristics.
2) Identify typical sentence structure and level of formality.
3) List do's and don'ts for writing in this brand's voice.
4) Provide 3 short example sentences that match the brand voice.

OUTPUT FORMAT (STRICT JSON ONLY):

{{
  "voice_name": "short label for this voice",
  "tone_description": "2-3 sentence description in {language}",
  "formality_level": "informal | neutral | formal",
  "style_traits": [
    "trait 1",
    "trait 2"
  ],
  "dos": [
    "do 1",
    "do 2"
  ],
  "donts": [
    "dont 1",
    "dont 2"
  ],
  "example_sentences": [
    "example sentence 1",
    "example sentence 2",
    "example sentence 3"
  ]
}}

RULES:
- Do NOT output anything outside the JSON.
Language: Respond in {language}.
"""




    @staticmethod
    def get_content_brief_prompt(research_json, form_data_json,
                                 language="Persian"):
        """
        research_json: خروجی merge research
        form_data_json: فرم داینامیک آیتم محتوا (title, goal, audience, length, etc.)
        """
        return f"""
You are a Senior Content Strategist.

Your task is to create a concise, practical content brief that a human writer could use.

INPUTS:

MERGED RESEARCH (JSON):
{research_json}

CONTENT FORM DATA (JSON-LIKE):
{form_data_json}

TASKS:
1) Summarize the main objective of the content.
2) Define the primary target audience.
3) Specify the main angle and unique value.
4) Suggest structure at a high level (sections, but not detailed outline).
5) List must-cover points and questions to answer.
6) Suggest tone, style, and examples if relevant.

OUTPUT FORMAT (STRICT JSON ONLY):

{{
  "objective": "1-2 sentence goal description in {language}",
  "target_audience": "description of audience in {language}",
  "main_angle": "unique angle or positioning in {language}",
  "high_level_structure": [
    "section 1",
    "section 2",
    "section 3"
  ],
  "must_cover_points": [
    "point 1",
    "point 2"
  ],
  "key_questions_to_answer": [
    "question 1",
    "question 2"
  ],
  "tone_style_notes": "short note on tone/style in {language}"
}}

RULES:
- Do NOT output anything outside the JSON.
Language: Respond in {language}.
"""




    @staticmethod
    def get_fetch_source_data_prompt(query: str) -> str:
        """
        Generates a mega prompt that simulates Google search and scraping
        of the first three results, returning JSON with sources and summary.
        """
        return f"""
You are simulating a web scraping system that collects content from the internet.

Your task is to simulate searching Google for the following query and extracting the first three relevant results.

Search Query:
"{query}"

General behavior rules:
- Simulate a realistic Google search.
- Select the top 3 realistic results that could appear for this query.
- Each result should represent a different website or source.
- The extracted content must look like real scraped HTML from a webpage.
- Preserve natural HTML structure such as headings, paragraphs, lists, and sections.
- Do NOT rewrite the content like an article. Instead, simulate raw scraped page content.
- Each source should have different writing style, structure, and formatting.
- The sources should feel authentic and independent from each other.

Content length rules:
- For typical website content: between 800 and 1500 words.
- If the query clearly relates to social media platforms (e.g., Instagram), content may be shorter (<= 1200 words).
- Automatically decide the appropriate length based on the query topic.

Language rules:
- The language must match the language of the search query.
- Do not translate the query; assume the user searched in that language.

Realism rules:
- Each source should simulate content as if it was scraped from a real page.
- Include realistic structures such as:
  - headings
  - paragraphs
  - bullet lists
  - numbered lists
  - FAQ sections
  - tips or best practices
- The content should look like actual page HTML extracted by a crawler.

Final analysis section:
- After reading the three sources, generate a combined summary and conclusion that synthesizes the key information from all sources.

The summary must include:
1) A short explanatory paragraph summarizing the topic.
2) A bullet list of key insights gathered from the three sources.

Output format (IMPORTANT):
Return ONLY valid JSON with the following structure:

{{
  "sources": [
    {{
      "title": "Title of the simulated page",
      "url": "https://example-site-1.com/article",
      "raw_html": "<html> ... realistic page HTML ... </html>"
    }},
    {{
      "title": "Title of the simulated page",
      "url": "https://example-site-2.com/article",
      "raw_html": "<html> ... realistic page HTML ... </html>"
    }},
    {{
      "title": "Title of the simulated page",
      "url": "https://example-site-3.com/article",
      "raw_html": "<html> ... realistic page HTML ... </html>"
    }}
  ],
  "summary": {{
    "paragraph": "A concise explanation summarizing the overall findings from the three sources.",
    "key_points": [
      "Key insight 1",
      "Key insight 2",
      "Key insight 3",
      "Key insight 4"
    ]
  }}
}}

Important constraints:
- The response MUST be valid JSON.
- Do NOT include explanations outside the JSON.
- Do NOT include markdown formatting.
- The HTML should look realistic but does not need to be a full webpage with scripts or CSS.
- Focus on content structure (headings, paragraphs, lists).
"""