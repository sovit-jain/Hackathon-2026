import json
import logging
import os
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

SKILL_CATEGORY_MAP = {
    'Language & communication': ['hindi', 'english', 'communication', 'customer support', 'basic communication'],
    'Office & productivity': ['ms excel', 'microsoft excel', 'excel', 'microsoft word', 'word', 'powerpoint', 'google sheets', 'google docs'],
    'Technical skills': ['python', 'java', 'sql', 'web development', 'data analysis', 'machine learning', 'automation', 'apis'],
    'Career readiness': ['resume writing', 'interview preparation', 'networking', 'project management', 'presentation'],
}


def _parse_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(text)
    except Exception:
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except Exception:
                return None
        return None


def build_skill_assessment_context(
    answers: List[Dict[str, Any]],
    goal: str,
    skills: List[str],
    employment_status: Optional[str] = None,
) -> Dict[str, Any]:
    question_summary = []
    for answer in answers:
        question_summary.append({
            'id': answer.get('question_id'),
            'selected': answer.get('selected_option'),
            'correct': answer.get('correct_option'),
        })

    selected_skills = [skill.strip() for skill in skills if skill and skill.strip()]
    grouped_skills = []
    for category, known_skills in SKILL_CATEGORY_MAP.items():
        matched_skills = [
            skill for skill in selected_skills if any(skill.lower() == known.lower() for known in known_skills)
        ]
        if matched_skills:
            grouped_skills.append({'category': category, 'skills': matched_skills})

    return {
        'goal': goal,
        'employment_status': employment_status or 'unemployed',
        'selected_skills': selected_skills,
        'skill_categories': grouped_skills,
        'answers': question_summary,
        'scoring_criteria': {
            'beginner': '0-39: little evidence of job-ready skills',
            'intermediate': '40-69: solid foundation with a few relevant skills',
            'advanced': '70-100: strong and relevant foundation for the target role',
        },
    }


def score_skills_assessment(skills: List[str], goal: str, employment_status: Optional[str] = None) -> Dict[str, Any]:
    selected_skills = [skill.strip() for skill in skills if skill and skill.strip() and skill.strip() != "None"]
    if not selected_skills:
        return {
            'score': 0,
            'level': 'beginner',
            'label': 'Digital Beginner',
            'summary': 'No current skills were selected yet. Choose a few strengths to build your first profile.',
            'top_skill': 'None',
            'missing_key_skill': 'Python',
            'explanation': 'No current skills were selected yet.',
            'source': 'rule',
        }

    # Define skill weights
    skill_weights = {
        "Hindi": 1, "English": 1,
        "MS Word": 2, "MS Excel": 2,
        "Excel Advanced": 3, "PowerPoint": 3,
        "Python": 5, "SQL": 5, "JavaScript": 5,
        "Data Analysis": 6, "Business Intelligence": 6,
        "Machine Learning": 8, "Cloud": 8,
    }
    
    # Calculate raw score based on weights
    raw_score = sum(skill_weights.get(skill, 0) for skill in selected_skills)
    max_possible = sum(skill_weights.values())  # 65
    
    # Normalize to 0-100 scale
    score = int((raw_score / max_possible) * 100)
    score = max(0, min(100, score))

    if score >= 70:
        level = 'advanced'
        explanation = 'You have a strong set of practical skills that fits the target role well.'
    elif score >= 40:
        level = 'intermediate'
        explanation = 'You have a useful foundation and a few high-value skills to build on.'
    else:
        level = 'beginner'
        explanation = 'Your current skills are still developing, so the next step is to strengthen a few key areas.'

    top_skill = selected_skills[0] if selected_skills else 'None'
    missing_key_skill = 'Python' if goal == 'data-analyst' else 'Communication'
    return {
        'score': score,
        'level': level,
        'label': 'Digital Beginner' if level == 'beginner' else 'Digital Builder' if level == 'intermediate' else 'Digital Advanced',
        'summary': explanation,
        'top_skill': top_skill,
        'missing_key_skill': missing_key_skill,
        'explanation': explanation,
        'source': 'rule',
    }


def llm_score_assessment(
    answers: List[Dict[str, Any]],
    goal: str,
    skills: List[str],
    employment_status: Optional[str] = None,
) -> Dict[str, Any]:
    """Call an OpenAI-compatible chat endpoint to score a skill-based assessment.

    Returns a dict with keys: score (int 0-100), level (str), explanation (str), and source (llm|rule).
    """
    api_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('LLM_API_KEY')
    model = os.environ.get('LLM_MODEL') or 'gpt-3.5-turbo'

    user_context = build_skill_assessment_context(answers, goal, skills, employment_status)
    if not api_key:
        logger.debug('No LLM API key configured, falling back to rule-based scoring')
        return score_skills_assessment(skills, goal, employment_status)

    system_prompt = (
        'You are an assessment coach for job seekers. Score the user\'s current skill profile based on weights and relevance to their target role. '
        'Use this skill weight system:\n'
        '- Life Skills (Hindi, English): 1 point each\n'
        '- Basic Computer (MS Word, MS Excel): 2 points each\n'
        '- Intermediate Digital (Excel Advanced, PowerPoint): 3 points each\n'
        '- Programming (Python, SQL, JavaScript): 5 points each\n'
        '- Analytics (Data Analysis, Business Intelligence): 6 points each\n'
        '- Advanced (Machine Learning, Cloud): 8 points each\n'
        'Max possible score: 65 points (normalize to 0-100)\n'
        'Score ranges: 0-39 = beginner, 40-69 = intermediate, 70-100 = advanced\n'
        'Return ONLY a JSON object with keys: score (integer 0-100), level (beginner|intermediate|advanced), '
        'label (short string), summary (short string), top_skill (the highest value skill selected), missing_key_skill (most important skill to learn), '
        'and explanation (short string). Calculate score by: (sum of selected skill weights / 65) * 100'
    )
    user_prompt = f"Context:\n{json.dumps(user_context)}\n\nRespond with JSON only."
    logger.info('Skill assessment system prompt: %s', system_prompt)
    logger.info('Skill assessment user prompt: %s', user_prompt)

    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        payload = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            'temperature': 0.0,
            'max_tokens': 300,
        }
        resp = httpx.post('https://api.openai.com/v1/chat/completions', headers=headers, json=payload, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
        parsed = _parse_json_from_text(content)
        if not parsed:
            logger.warning('LLM returned unparsable content: %s', content)
            return score_skills_assessment(skills, goal, employment_status)

        score = int(parsed.get('score', parsed.get('score_pct', 0)))
        score = max(0, min(100, score))
        level = parsed.get('level') or ('advanced' if score >= 70 else 'intermediate' if score >= 40 else 'beginner')
        explanation = parsed.get('explanation', '')
        return {
            'score': score,
            'level': level,
            'label': parsed.get('label') or ('Digital Beginner' if level == 'beginner' else 'Digital Builder' if level == 'intermediate' else 'Digital Advanced'),
            'summary': parsed.get('summary') or explanation,
            'top_skill': parsed.get('top_skill') or (skills[0] if skills else 'None'),
            'missing_key_skill': parsed.get('missing_key_skill') or ('Python' if goal == 'data-analyst' else 'Communication'),
            'explanation': explanation,
            'source': 'llm',
        }
    except Exception as e:
        logger.exception('LLM scoring failed: %s', e)
        return score_skills_assessment(skills, goal, employment_status)
