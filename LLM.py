import json
from groq import Groq
from groq_API import groq_api_key
client = Groq(api_key=groq_api_key)

def generate_learning_path(user_profile):

    prompt = f"""
You are an AI learning-path generator.

### USER PROFILE
Name: {user_profile["name"]}
Known Skills with level: {user_profile["known_skills_with_levels"]}
Known Skills: {", ".join(user_profile["known_skills"])}
Skills to Learn: {", ".join(user_profile["skills_to_learn"])}
Career Goals: {", ".join(user_profile["career_goals"])}
Learning Speed: {user_profile["learning_speed"]}
Preferred Format: {user_profile["preferred_format"]}

### TASKS   
1. Determine the user's proficiency level:
   Output exactly one: Beginner, Intermediate, Advanced.

2. Compare known skills vs required skills for the target career goal.
   Identify missing skills.
   Create a skill-gap map with:
   - skill
   - why needed
   - current level guess
   - priority

3. Create a weekly learning plan customized to the user's:
   - skill gaps
   - learning speed
   - target career
   - preferred learning format

4. Output ONLY THIS JSON:

{{
  "user_level": "",
  "required_skills": [],
  "missing_skills": [],
  "skill_gap_map": {{}},
  "weekly_learning_plan": []
}}

Make sure the JSON is valid and contains no extra text.
"""

        
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    text = response.choices[0].message.content
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        fixed = text[text.find("{"): text.rfind("}")+1]
        data = json.loads(fixed)

    return data


if __name__ == "__main__":
    with open("user_data_GPT_LLM.json") as f:
        profile = json.load(f)

    result = generate_learning_path(profile)
    print(json.dumps(result, indent=4))
