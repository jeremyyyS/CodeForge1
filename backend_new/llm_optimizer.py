# llm_optimizer.py
import ast
import asyncio
from typing import List, Dict, Optional
from config import GEMINI_API_KEY, MODEL_NAME, API_TIMEOUT

client = None
if GEMINI_API_KEY:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=GEMINI_API_KEY)


async def optimize_with_gemini(code: str, hints: Optional[List[Dict]] = None) -> str:
    if not client:
        raise Exception("Gemini API key not configured. Cannot use online optimization.")

    from google.genai import types

    hint_text = ""
    if hints:
        hint_text = f"\nDETECTED ISSUES:\n{[h['message'] for h in hints]}\n"

    prompt = f"""You are an expert Python optimizer.
{hint_text}

CRITICAL RULES:
1. Keep ALL variable definitions and assignments intact (e.g., data = list(range(1000)))
2. Keep ALL import statements
3. Only optimize loops, comprehensions, and algorithms
4. Do NOT remove setup code or variable initializations

CODE:
{code}

Optimize this code for performance.
Return ONLY the optimized Python code. No explanations, no markdown fences."""

    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(
                lambda: client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2
                    )
                )
            ),
            timeout=API_TIMEOUT
        )

        optimized = response.text.strip()

        # Clean markdown fences
        if optimized.startswith("```python"):
            optimized = optimized[len("```python"):].strip()
            if optimized.endswith("```"):
                optimized = optimized[:-3].strip()
        elif optimized.startswith("```"):
            optimized = optimized[3:].strip()
            if optimized.endswith("```"):
                optimized = optimized[:-3].strip()

        ast.parse(optimized)
        return optimized
    except asyncio.TimeoutError:
        raise Exception(f"Gemini API timeout ({API_TIMEOUT}s)")
    except SyntaxError:
        return code
    except Exception as e:
        raise Exception(f"Gemini optimization failed: {str(e)}")
