import asyncio
import logging
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import settings

logger = logging.getLogger(__name__)


def _looks_complete(content: str) -> bool:
    lowered = content.lower()
    has_sections = all(section in lowered for section in ["what you will learn:", "introduction:", "key concepts:", "real world scenario:", "key takeaways:", "quick check:"])
    has_examples = "example:" in lowered
    has_takeaways = lowered.count("- ") >= 3
    return has_sections and has_examples and has_takeaways


def build_curated_lesson_content(
    user_name: str,
    target_role: str,
    skill_level: str,
    lesson_title: str,
    lesson_description: str,
) -> str:
    role_label = (target_role or "data-analyst").replace("-", " ").title()
    normalized_level = (skill_level or "beginner").strip().lower()
    skill_label = (normalized_level or "beginner").title()
    lesson_label = lesson_title.strip()

    if normalized_level == "advanced":
        learn_points = [
            f"Master the core idea behind {lesson_label.lower()} with a more strategic lens.",
            f"Apply a practical approach that fits a {role_label} role at an {skill_label.lower()} level.",
            f"Turn the lesson into a repeatable habit you can use to improve quality, ownership, and decision-making.",
        ]
        intro_paragraphs = [
            f"{lesson_label} is a high-impact capability for {role_label} professionals who need to work with sharper judgment and stronger execution. The goal is not simply to know the topic, but to use it to improve outcomes under real constraints.",
            f"In this lesson, you will connect the idea behind {lesson_label.lower()} to complex tasks, trade-offs, and communication. The focus is on building a disciplined habit you can apply in demanding workflows and team settings.",
        ]
        concepts = [
            {
                "name": "Frame the problem clearly",
                "explanation": f"Before you begin {lesson_label.lower()}, define the outcome you want to achieve and the trade-offs that matter. Clear framing helps you make stronger decisions and communicate them effectively.",
                "example": f"In a {role_label} context, you might compare options, identify risk, and explain why one approach is more strategic than another.",
            },
            {
                "name": "Apply a structured method",
                "explanation": "Turn a broad task into a repeatable sequence of actions so quality stays high even when the work becomes complex. This makes your thinking easier to review and easier to improve.",
                "example": f"For a {role_label} task, you could define the decision points, the evidence you need, and the follow-up action that will improve the result.",
            },
            {
                "name": "Review and strengthen",
                "explanation": "A strong lesson ends with reflection on what worked, what was difficult, and how you would improve next time. That review helps turn knowledge into durable expertise.",
                "example": f"After practicing {lesson_label.lower()}, you can log what improved, what still needs refinement, and what you would optimize next time.",
            },
        ]
        scenario = f"Imagine you are leading a {role_label} workflow where the stakes are higher and the team needs a clear, defensible plan. By using the approach from {lesson_label}, you can turn a complicated situation into something manageable, strategic, and actionable."
        takeaways = [
            f"{lesson_label} helps you work with more structure, better judgment, and stronger ownership.",
            "Advanced habits make professional work easier to scale and easier to improve over time.",
            f"The best results come from applying the lesson in a real {role_label} environment where trade-offs and quality matter.",
            "A short review at the end helps the lesson stick and makes your next step clearer.",
        ]
        quick_check = [
            f"What advanced outcome do you want to improve when applying {lesson_label.lower()}?",
            "Which step in this process creates the highest value for your work?",
            "How would you explain this lesson to a teammate in a way that supports a stronger decision?",
        ]
    elif normalized_level == "intermediate":
        learn_points = [
            f"Build on the basics behind {lesson_label.lower()} with a more practical lens.",
            f"Apply a method that fits a {role_label} role at an {skill_label.lower()} level.",
            f"Turn the lesson into a repeatable habit you can use in everyday work.",
        ]
        intro_paragraphs = [
            f"{lesson_label} is a practical skill that helps {role_label} professionals work with more clarity and confidence. The goal is to move beyond the basics and apply the idea in a way that feels useful in daily work.",
            f"In this lesson, you will connect the idea behind {lesson_label.lower()} to more realistic tasks, communication, and follow-through. The focus is on building a dependable habit you can use with growing confidence.",
        ]
        concepts = [
            {
                "name": "Set a clear target",
                "explanation": f"Before you begin {lesson_label.lower()}, define the result you want and what success should look like. Clear goals make the work easier to organize and easier to communicate.",
                "example": f"In a {role_label} context, you might define success as a smoother handoff, a stronger update, or a better decision process.",
            },
            {
                "name": "Break the work into steps",
                "explanation": "Turn a broad task into a short sequence of actions so the process feels manageable and repeatable. This makes it easier to stay consistent and to spot where a problem might begin.",
                "example": f"For a {role_label} task, you could list the main actions, the people involved, and the first decision that needs to happen.",
            },
            {
                "name": "Review the result",
                "explanation": "A good lesson ends with reflection. Ask what worked, what felt unclear, and what you would do differently next time so the skill becomes more durable.",
                "example": f"After practicing {lesson_label.lower()}, you can write a short note on what improved and where you still want more support.",
            },
        ]
        scenario = f"Imagine you are supporting a team in a {role_label} workflow and you need to explain a problem clearly. By using the approach from {lesson_label}, you can turn a messy situation into something manageable, helpful, and easy to act on."
        takeaways = [
            f"{lesson_label} helps you work with more structure and better judgment.",
            "Simple habits make professional work easier to repeat and easier to improve.",
            f"The best results come from applying the lesson in a real {role_label} situation rather than just reading about it.",
            "A short review at the end helps the lesson stick and makes your next step clearer.",
        ]
        quick_check = [
            f"What is one outcome you want to improve when applying {lesson_label.lower()}?",
            "Which step in this process feels most useful to you right now?",
            "How would you explain this lesson to a teammate in your own words?",
        ]
    else:
        learn_points = [
            f"Build a strong foundation around {lesson_label.lower()}.",
            f"Apply a practical approach that fits a {role_label} role at a {skill_label.lower()} level.",
            f"Turn the lesson into a repeatable habit you can use in real work.",
        ]
        intro_paragraphs = [
            f"{lesson_label} is a practical skill that helps {role_label} professionals work with more clarity and confidence. The goal is not just to know the topic, but to use it in a real workflow with calm, structured thinking.",
            f"In this lesson, you will connect the idea behind {lesson_label.lower()} to everyday tasks, decision-making, and communication. The focus is on building a simple habit you can apply immediately, even if you are still building experience.",
        ]
        concepts = [
            {
                "name": "Start with the goal",
                "explanation": f"Before you begin {lesson_label.lower()}, define the outcome you want to achieve. Clear goals make the work easier to follow and easier to explain to others.",
                "example": f"In a {role_label} context, you might define the outcome as reducing confusion, speeding up a handoff, or making a decision easier to explain.",
            },
            {
                "name": "Break the work into steps",
                "explanation": "Turn a broad task into a short sequence of actions so the process feels manageable. This makes it easier to stay consistent and to spot where a problem might begin.",
                "example": f"For a {role_label} task, you could list the main actions, the people involved, and the first decision that needs to happen.",
            },
            {
                "name": "Review the result",
                "explanation": "A good lesson ends with reflection. Ask what worked, what felt unclear, and what you would do differently next time so the skill becomes more durable.",
                "example": f"After practicing {lesson_label.lower()}, you can write a short note on what improved and where you still want more support.",
            },
        ]
        scenario = f"Imagine you are supporting a team in a {role_label} workflow and you need to explain a problem clearly. By using the approach from {lesson_label}, you can turn a messy situation into something manageable, helpful, and easy to act on."
        takeaways = [
            f"{lesson_label} helps you work with more structure and better judgment.",
            "Simple habits make professional work easier to repeat and easier to improve.",
            f"The best results come from applying the lesson in a real {role_label} situation rather than just reading about it.",
            "A short review at the end helps the lesson stick and makes your next step clearer.",
        ]
        quick_check = [
            f"What is one outcome you want to improve when applying {lesson_label.lower()}?",
            "Which step in this process feels most useful to you right now?",
            "How would you explain this lesson to a teammate in your own words?",
        ]

    concept_lines = []
    for index, concept in enumerate(concepts, start=1):
        concept_lines.append(
            f"{index}. {concept['name']}\n"
            f"   {concept['explanation']}\n"
            f"   Example: {concept['example']}"
        )

    return (
        "WHAT YOU WILL LEARN:\n"
        + "\n".join(f"- {point}" for point in learn_points)
        + "\n\n"
        "INTRODUCTION:\n"
        + "\n\n".join(intro_paragraphs)
        + "\n\n"
        "KEY CONCEPTS:\n"
        + "\n\n".join(concept_lines)
        + "\n\n"
        "REAL WORLD SCENARIO:\n"
        + scenario
        + "\n\n"
        "KEY TAKEAWAYS:\n"
        + "\n".join(f"- {takeaway}" for takeaway in takeaways)
        + "\n\n"
        "QUICK CHECK:\n"
        + "\n".join(f"{index}. {question}" for index, question in enumerate(quick_check, start=1))
    )


def _describe_api_key(api_key: Optional[str]) -> str:
    if not api_key:
        return "not configured"

    normalized_key = api_key.strip()
    if not normalized_key:
        return "empty/whitespace"

    if len(normalized_key) <= 10:
        return f"configured (length={len(normalized_key)}, preview={normalized_key[:2]}*** )"

    return (
        f"configured (length={len(normalized_key)}, "
        f"prefix={normalized_key[:6]}..., suffix=...{normalized_key[-4:]})"
    )


async def _call_mesh(prompt: str, system_prompt: str) -> Optional[str]:
    api_key = (settings.OPENAI_API_KEY or "").strip()
    logger.info("OpenAI API key status before request: %s", _describe_api_key(api_key))

    if not api_key:
        logger.warning("OpenAI API key not configured; using fallback response")
        return None

    logger.info("OpenAI API key detected; proceeding with LLM request")

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt),
    ]

    try:
        logger.info("Calling OpenAI chat completion with system prompt and user prompt")
        llm = ChatOpenAI(
            api_key=api_key,
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=220,
        )

        response = await asyncio.to_thread(llm.invoke, messages)
        content = response.content.strip() if getattr(response, "content", None) else str(response)
        logger.info("Mesh AI call succeeded")
        return content
    except Exception as exc:
        logger.exception("Mesh AI call failed: %s", exc)
        return None


async def generate_intervention(user_name: str, score: int, completed_lessons: int) -> str:
    prompt = (
        f"Create a supportive, concise intervention message for {user_name}. "
        f"Their latest assessment score is {score} and they completed {completed_lessons} lessons. "
        "Encourage them, highlight a small next step, and mention that progress is still possible."
    )
    content = await _call_mesh(prompt, "You are SkillBridge, a warm learning coach.")
    if content:
        return content
    return (
        f"You’re doing better than you think, {user_name}. "
        f"A score of {score} means you’re learning, and finishing one more lesson today will build momentum."
    )


async def generate_lesson_content(
    user_name: str,
    target_role: str,
    skill_level: str,
    lesson_title: str,
    lesson_description: str,
) -> str | None:
    prompt = (
        "Generate a structured lesson for a learner with these details:\n\n"
        f"Learner name: {user_name}\n"
        f"Target role: {target_role}\n"
        f"Skill level: {skill_level}\n"
        f"Lesson title: {lesson_title}\n"
        f"Lesson description: {lesson_description}\n\n"
        "Return the lesson in this exact structure:\n\n"
        "WHAT YOU WILL LEARN:\n"
        "- [point 1]\n"
        "- [point 2]\n"
        "- [point 3]\n\n"
        "INTRODUCTION:\n"
        "[2-3 paragraphs introducing the topic]\n\n"
        "KEY CONCEPTS:\n"
        "1. [Concept Name]\n"
        "   [2-3 sentence explanation]\n"
        "   Example: [real world example]\n\n"
        "2. [Concept Name]\n"
        "   [2-3 sentence explanation]\n"
        "   Example: [real world example]\n\n"
        "3. [Concept Name]\n"
        "   [2-3 sentence explanation]\n"
        "   Example: [real world example]\n\n"
        "REAL WORLD SCENARIO:\n"
        "[One practical scenario specific to the role and level]\n\n"
        "KEY TAKEAWAYS:\n"
        "- [takeaway 1]\n"
        "- [takeaway 2]\n"
        "- [takeaway 3]\n"
        "- [takeaway 4]\n"
        "- [takeaway 5]\n\n"
        "QUICK CHECK:\n"
        "1. [Self-reflection question 1]\n"
        "2. [Self-reflection question 2]\n"
        "3. [Self-reflection question 3]\n\n"
        "Keep the tone friendly, practical and encouraging.\n"
        "Keep content specific to [target_role] at [skill_level] level."
    )
    content = await _call_mesh(prompt, "You are SkillBridge, a friendly lesson coach for learners in career transition. Write polished, complete lesson content that feels practical and human, with every concept explained and every section filled in.")
    if content and _looks_complete(content):
        return content

    logger.info("Using curated lesson content fallback for %s", lesson_title)
    return build_curated_lesson_content(user_name, target_role, skill_level, lesson_title, lesson_description)


async def generate_chat_reply(message: str, profile_role: str) -> str:
    prompt = (
        f"A learner asks: {message}. They are preparing for a {profile_role} role. "
        "Respond with a short, actionable, supportive answer."
    )
    content = await _call_mesh(prompt, "You are SkillBridge, an expert learning assistant.")
    if content:
        return content
    if "lesson" in message.lower():
        return "Start with the next lesson in your path and focus on one concept at a time. Small progress compounds quickly."
    if "job" in message.lower() or "career" in message.lower():
        return "Review the resume-focused lessons and match your progress to the recommended roles in the jobs section."
    return "I can help you with your next learning step, a confidence boost, or a practical study plan."
