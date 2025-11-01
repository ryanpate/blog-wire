#!/usr/bin/env python3
"""
Debug script to see raw OpenAI output
"""

from openai import OpenAI
from config import Config

client = OpenAI(api_key=Config.OPENAI_API_KEY)

prompt = """Write a comprehensive, SEO-optimized blog post about: "test artificial intelligence"

Requirements:
- Word count: 2000-3500 words (IMPORTANT: Ensure the content is substantial and meets this requirement)
- Tone: Conversational, friendly, and personable - write as Ryan Pate speaking directly to readers
- Style: Long-form, informative, well-structured with deep insights
- Use first-person perspective ("I", "my experience", etc.) to make it personal
- Include relevant headers (H2, H3) for better readability
- Naturally incorporate long-tail SEO keywords throughout
- Add real value with actionable insights, examples, and personal observations
- End with a signature: "- Ryan Pate"

SEO Focus:
- Use long-form keywords (e.g., "how to invest in cryptocurrency for beginners" not just "crypto")
- Include semantic keywords and related terms
- Front-load important keywords in title and first paragraph
- Use natural language that people actually search for

Structure your response EXACTLY as follows:

TITLE: [Compelling, SEO-friendly title with long-tail keywords]

META_DESCRIPTION: [150-160 character meta description with primary keyword]

META_KEYWORDS: [5-7 long-form keywords, comma-separated - focus on phrases people search]

EXCERPT: [2-3 sentence compelling excerpt that includes main keyword]

CONTENT:
[Full blog post content in Markdown format with headers, lists, and formatting]

IMPORTANT:
- End the blog post with a conversational closing paragraph
- Sign off with: "- Ryan Pate"
- Write as if Ryan is sharing personal insights and expertise
- Make it feel authentic and relatable, not corporate or robotic
- Ensure content is truly 2000-3500 words - no shorter!"""

print("Sending request to OpenAI...")
print("=" * 80)

response = client.chat.completions.create(
    model=Config.OPENAI_MODEL,
    messages=[
        {
            "role": "system",
            "content": "You are an expert blog writer who creates engaging, SEO-optimized, long-form content in a conversational and friendly tone. Your blogs are well-researched, informative, and easy to read."
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.7,
    max_tokens=4096
)

content = response.choices[0].message.content

print("RAW OPENAI RESPONSE:")
print("=" * 80)
print(content)
print("=" * 80)
print(f"\nResponse length: {len(content)} characters")
print(f"Word count: {len(content.split())} words")
