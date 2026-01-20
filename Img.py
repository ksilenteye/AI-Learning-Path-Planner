# img.py
import json
import os

from google import genai
from google.genai import types
from LLM import generate_learning_path
from gemini_api02 import key

client = genai.Client(api_key=key)


def generate_roadmap_image():
    # 1. Load user profile and get learning path JSON from Groq
    with open("user_data_GPT_LLM.json") as f:
        profile = json.load(f)

    learning_plan = generate_learning_path(profile)

    # 2. Create concise text summary
    plan_summary = (
        f"User Level: {learning_plan['user_level']}\n"
        f"Missing Skills: {', '.join(learning_plan['missing_skills'])}\n"
        f"Weekly Plan: {len(learning_plan.get('weekly_learning_plan', []))} weeks"
    )

    prompt = (
        "Create a simple, clear learning roadmap infographic. "
        "Use a horizontal timeline with one box per week, labeled Week 1, Week 2, etc. "
        "Each box has 1–2 short tasks, large readable text, minimal icons. "
        "No decorative curves or maze layout. "
        f"Context:\n{plan_summary}"
    )

    # 3. Generate image with Gemini image model
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",   # or latest image model name
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio="16:9",
            ),
        ),
    )

    # 4. Save first returned image
    saved = False
    for part in response.parts:
        if part.inline_data is not None:
            image = part.as_image()
            image.save("learning_roadmap.png")
            saved = True
            break

    if saved:
        print("Roadmap image generated as learning_roadmap.png")
    else:
        print("No image returned from Gemini.")


if __name__ == "__main__":
    generate_roadmap_image()
