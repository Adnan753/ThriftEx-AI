import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from services.memory import get_past_decisions, format_memory_for_prompt

load_dotenv()

client = OpenAI (
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url=os.getenv("NVIDIA_BASE_URL")
)

MODEL = os.getenv("NVIDIA_MODEL", "openai/gpt-oss-120b")

def call_llm(prompt: str, max_tokens: int = 1000) -> str:
    response = client.chat.completions.create(
        model = MODEL,
        max_tokens = max_tokens,
        messages = [{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def analyze_costs_multistep(summary: dict, cost_data: list, goal: str = None) -> str:

    past_decisions = get_past_decisions(10)
    memory_context = format_memory_for_prompt(past_decisions)

    top_spenders = '\n'.join([
        f"{i+1}. {s['service']}: ${s['total']}"
        for i, s in enumerate(summary.get('top_spenders', []))
    ])

    step1_prompt = f"""You are a FinOps AI agent. Analyze this AWS cost data objectively.

CURRENT SPENDING:
- This month: ${summary.get('current_month_total', 0)}
- Last month: ${summary.get('previous_month_total', 0)}
- Change: {summary.get('percent_change', '0%')}
- Forecasted total: ${summary.get('forecasted_total', 0)}
- Daily average: ${summary.get('avg_daily', 0)}

TOP SERVICES:
{top_spenders}

PAST AGENT DECISIONS:
{memory_context}

{'USER GOAL: ' + goal if goal else ''}

Identify the 3 most critical cost patterns. Be specific and data-driven. Plain text only."""

    observation = call_llm(step1_prompt, 500)

    # Step 2 — Reason
    step2_prompt = f"""Based on these AWS cost observations:
{observation}

Now perform root cause analysis. For each pattern:
1. Why is this happening?
2. What is the business impact?
3. How urgent is it?

Be concise and specific. Plain text only."""

    reasoning = call_llm(step2_prompt, 500)

    # Step 3 — Plan + Output JSON
    step3_prompt = f"""Based on this analysis:

OBSERVATIONS: {observation}
REASONING: {reasoning}

Generate a final structured response as valid JSON only, no markdown:
{{
    "summary": "2-3 sentence executive summary",
    "insights": [
        {{
            "type": "warning/info/success",
            "title": "Short title",
            "description": "What this means"
        }}
    ],
    "recommendations": [
        {{
            "priority": "high/medium/low",
            "service": "AWS service name",
            "action": "Exact action to take",
            "estimated_saving": "Amount or percentage",
            "reasoning": "Why this helps"
        }}
    ],
    "agent_reasoning": {{
        "observations": "{observation[:200]}",
        "root_causes": "{reasoning[:200]}",
        "confidence": "high/medium/low"
    }}
}}"""

    raw_output = call_llm(step3_prompt, 1000)

    # Parse JSON safely
    try:
        # Strip markdown if model adds it
        clean = raw_output.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean.strip())
    except json.JSONDecodeError:
        return {
            "summary": observation,
            "insights": [],
            "recommendations": [],
            "agent_reasoning": {
                "observations": observation,
                "root_causes": reasoning,
                "confidence": "low"
            }
        }