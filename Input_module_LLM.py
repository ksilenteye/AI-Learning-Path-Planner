import json
from groq import Groq
from groq_API import groq_api_key

client = Groq(api_key=groq_api_key)

def generate_mcq_questions(skill, level):
    prompt = f"""
    Generate exactly 5 MCQ questions to test the user's true knowledge level.

    Skill: {skill}
    Level: {level}

    STRICT FORMAT FOR EACH QUESTION:

    Q1: <question>

    A. <long option>
    B. <long option>
    C. <long option>
    D. <long option>

    Correct Answer: <A/B/C/D>

    RULES:
    - Options must be 1–3 sentences, never one-word.
    - Only one correct answer.
    - No explanations.
    - Follow the exact formatting.
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content.strip()

    # Split into question blocks
    blocks = raw.split("\nQ")
    mcqs = []

    for b in blocks:
        b = b.strip()
        if not b.startswith("Q"):
            b = "Q" + b
        if "A." in b and "Correct Answer" in b:
            mcqs.append(b)

    return mcqs[:5]


def evaluate_mcq_answers(mcqs, user_answers):
    prompt_text = ""

    for i in range(5):
        prompt_text += f"{mcqs[i]}\nUser Answer: {user_answers[i]}\n\n"

    prompt = f"""
    Evaluate the user's answers.

    For each MCQ, compare user's answer with "Correct Answer".
    Count how many answers are correct.

    STRICT OUTPUT:
    - Respond ONLY with a single integer from 0 to 5.
    - No explanation.
    
    Here are the questions and user's answers:

    {prompt_text}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    num = response.choices[0].message.content.strip()

    try:
        return int(num)
    except:
        return 0

def adjust_level(level, correct):
    if correct >= 3:
        return level

    if level == "Advanced":
        return "Intermediate"
    if level == "Intermediate":
        return "Beginner"
    return "Beginner"


# ---------------------------
# MAIN INPUT MODULE
# ---------------------------
def Extract_Input():

    print("\nProvide your details:\n")

    user_data = {}

    user_data["name"] = input("Enter your name: ")

    # Known skills
    known = input("Enter known skills (comma separated): ")
    known_skills = [s.strip() for s in known.split(",")]

    known_skill_levels = {}

    for skill in known_skills:
        print(f"\nRate your level for '{skill}':")
        print("1. Beginner\n2. Intermediate\n3. Advanced")
        lvl = input("Enter 1/2/3: ").strip()

        level_map = {
            "1": "Beginner",
            "2": "Intermediate",
            "3": "Advanced"
        }
        selected_level = level_map.get(lvl, "Beginner")

        print(f"\nGenerating MCQ questions for {skill} ({selected_level})...\n")
        mcqs = generate_mcq_questions(skill, selected_level)

        user_answers = []
        for i, q in enumerate(mcqs):
            # Remove the "Correct Answer" line before showing to user
            display_q = q.split("Correct Answer:")[0].strip()
            print("\n" + display_q)
            ans = input("Choose A/B/C/D: ").strip().upper()
            user_answers.append(ans)


        # Evaluate MCQ test using LLM
        correct = evaluate_mcq_answers(mcqs, user_answers)

        final_level = adjust_level(selected_level, correct)

        print(f"\nCorrect Answers: {correct}/5")
        print(f"Verified Level for {skill}: {final_level}\n")

        known_skill_levels[skill] = final_level

    known_skills_with_levels = ", ".join(f"{skill} ({level})" for skill, level in known_skill_levels.items())

    user_data["known_skills"] = known_skill_levels
    user_data["known_skills_with_levels"] = known_skills_with_levels

    # Skills to learn
    learn = input("Enter skills to learn (comma separated): ")
    user_data["skills_to_learn"] = [s.strip() for s in learn.split(",")]

    # Career goals
    goals = input("Enter career goals (comma separated): ")
    user_data["career_goals"] = [g.strip() for g in goals.split(",")]

    # Learning speed
    user_data["learning_speed"] = input("Learning speed (slow/medium/fast): ").strip().lower()

    # Preferred format
    user_data["preferred_format"] = input("Learning format (video/text/project-based): ").strip().lower()

    user_data["raw_text"] = (
        f"Known skills: {known}. "
        f"Skills to learn: {learn}. "
        f"Career goals: {goals}."
    )

    return user_data

def Save_To_JSON(data, filename="user_data_GPT_LLM.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"\nSaved to {filename}")


if __name__ == "__main__":
    data = Extract_Input()
    Save_To_JSON(data)

