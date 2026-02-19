import asyncio
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, MODEL_NAME, API_TIMEOUT

client = genai.Client(api_key=GEMINI_API_KEY)


async def generate_ai_explanation(
    original_code: str,
    optimized_code: str,
    rules: list,
    speedup: float
) -> str:
    """
    Generate a clear, technically strong explanation of why
    the optimized code performs better.
    """

    # Safely extract top rules
    rules_text = "\n".join(
        [
            f"- {r.get('message', '')} → {r.get('suggestion', '')}"
            for r in (rules or [])[:5]
        ]
    ) or "No specific rule patterns detected."

    speed_text = (
        f"{round(speedup, 2)}x speedup"
        if speedup and speedup > 1
        else "performance improvement"
    )

    prompt = f"""
You are a senior Python performance engineer.

Explain clearly and technically why the optimized version performs better.

Focus on:
• Algorithmic improvements
• Reduced Python-level overhead
• Use of C-backed built-ins
• Improved memory locality
• Reduced repeated computation

ORIGINAL CODE:
{original_code}

OPTIMIZED CODE:
{optimized_code}

DETECTED OPTIMIZATION SIGNALS:
{rules_text}

OBSERVED PERFORMANCE:
{speed_text}

Write a concise but high-quality technical explanation (80–150 words).
Avoid fluff. Be confident and analytical.
"""

    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(
                lambda: client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.25,
                        max_output_tokens=300
                    )
                )
            ),
            timeout=API_TIMEOUT
        )

        text = response.text.strip()

        # Clean markdown fences if any
        if text.startswith("```"):
            text = text.replace("```python", "").replace("```", "").strip()

        return text

    except Exception:
        # Intelligent fallback explanation
        fallback = []

        if rules:
            fallback.append(
                "The optimization restructures inefficient patterns detected in the original code."
            )

        if speedup and speedup > 1:
            fallback.append(
                f"This results in approximately {round(speedup, 2)}x faster execution."
            )

        fallback.append(
            "The improvement likely comes from reducing Python loop overhead and leveraging more efficient built-in operations implemented in optimized C code."
        )

        return " ".join(fallback)
