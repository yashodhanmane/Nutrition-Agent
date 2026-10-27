"""
Nutrition Agent — core agentic logic
Builds structured prompts, calls Granite, post-processes responses.
"""

from .granite_client import call_granite
from .guardrails import check_input_safety, check_output_safety, get_medical_disclaimer

# ── System persona ─────────────────────────────────────────────────────────────
SYSTEM_PERSONA = """You are NutriCare AI, a compassionate and knowledgeable nutrition assistant powered by IBM Granite.
Your role is to provide personalised, evidence-based nutrition guidance while:
- Being helpful, respectful, and empathetic (HAM principles)
- Respecting cultural food preferences and dietary restrictions
- Acknowledging medical conditions without replacing professional advice
- Providing practical, actionable, and realistic recommendations
- Always encouraging consultation with healthcare professionals for medical conditions
- Being inclusive and sensitive to all body types, backgrounds, and cultures"""


# ── Prompt builders ───────────────────────────────────────────────────────────
def _build_nutrition_plan_prompt(user: dict) -> str:
    conditions = ", ".join(user.get("medical_history", [])) if user.get("medical_history") else "None reported"
    allergies  = ", ".join(user.get("allergies", [])) if user.get("allergies") else "None"
    goals      = ", ".join(user.get("goals", [])) if user.get("goals") else "General wellness"

    return f"""<|system|>
{SYSTEM_PERSONA}
<|user|>
A user has provided the following details and is requesting a personalised nutrition plan:

Name            : {user.get('name', 'User')}
Age             : {user.get('age', 'Not specified')} years
Gender          : {user.get('gender', 'Not specified')}
Location        : {user.get('city', '')}, {user.get('country', '')}
Diet Preference : {user.get('diet_preference', 'No preference')}
Activity Level  : {user.get('activity_level', 'Moderate')}
Weight Goal     : {goals}
Medical History : {conditions}
Allergies       : {allergies}

Please provide a comprehensive, personalised nutrition plan that includes:

1. **Daily Caloric Needs** - estimated calorie range based on age, gender, activity level, and goals
2. **Macronutrient Breakdown** - recommended percentages and grams for carbohydrates, proteins, and fats
3. **Key Micronutrients** - vitamins and minerals to prioritise given their medical conditions
4. **7-Day Meal Plan** - breakfast, lunch, dinner, and 2 snacks per day using locally available foods from {user.get('city', 'their region')}, {user.get('country', '')}
5. **Foods to Include** - nutrient-dense foods aligned with diet preference and cultural context
6. **Foods to Avoid/Limit** - especially considering medical conditions: {conditions}
7. **Hydration Guidelines** - daily water intake recommendation
8. **Practical Tips** - 3-5 actionable lifestyle tips for nutritional success
9. **When to Seek Medical Advice** - specific warning signs to watch for

Be warm, encouraging, and culturally sensitive. Format the plan clearly with headings and bullet points.
<|assistant|>
"""


def _build_query_prompt(user_context: dict, user_query: str) -> str:
    name = user_context.get("name", "there")
    conditions = ", ".join(user_context.get("medical_history", [])) if user_context.get("medical_history") else "None"
    diet = user_context.get("diet_preference", "No specific preference")

    return f"""<|system|>
{SYSTEM_PERSONA}
<|user|>
Context about the user asking this question:
- Name: {name}
- Diet Preference: {diet}
- Medical History: {conditions}
- Location: {user_context.get('city', '')}, {user_context.get('country', '')}

Question: {user_query}

Provide a helpful, accurate, and compassionate answer. If the question involves serious medical concerns,
gently remind the user to consult a healthcare professional. Keep the answer concise but thorough.
Use a warm, friendly tone. If relevant, tailor advice to their dietary preferences and medical background.
<|assistant|>
"""


# ── Agent actions ──────────────────────────────────────────────────────────────
def generate_nutrition_plan(user_data: dict) -> dict:
    """
    Main agentic action: generate personalised nutrition plan.
    Returns {"success": bool, "plan": str, "disclaimer": str, "error": str}
    """
    # Input safety check
    summary = f"{user_data.get('medical_history', '')} {user_data.get('goals', '')}"
    safety  = check_input_safety(summary)

    if not safety["safe"]:
        return {"success": False, "error": safety["reason"]}

    warning = safety.get("reason", "") if safety.get("sensitive") else ""

    try:
        prompt    = _build_nutrition_plan_prompt(user_data)
        raw_plan  = call_granite(prompt, max_tokens=1200, temperature=0.6)
        safe_plan = check_output_safety(raw_plan)

        return {
            "success"   : True,
            "plan"      : safe_plan,
            "warning"   : warning,
            "disclaimer": get_medical_disclaimer(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def answer_nutrition_query(user_context: dict, query: str) -> dict:
    """
    Agentic Q&A: answer a free-form nutrition question.
    Returns {"success": bool, "answer": str, "disclaimer": str, "error": str}
    """
    safety = check_input_safety(query)

    if not safety["safe"]:
        return {"success": False, "error": safety["reason"]}

    warning = safety.get("reason", "") if safety.get("sensitive") else ""

    try:
        prompt     = _build_query_prompt(user_context, query)
        raw_answer = call_granite(prompt, max_tokens=600, temperature=0.7)
        safe_ans   = check_output_safety(raw_answer)

        return {
            "success"   : True,
            "answer"    : safe_ans,
            "warning"   : warning,
            "disclaimer": get_medical_disclaimer(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
