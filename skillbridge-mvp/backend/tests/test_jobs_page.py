from app.utils.scoring import calculate_skill_match_percentage


def test_skill_match_percentage_is_skill_based_only():
    user_skills = ["Python", "APIs", "Excel"]
    job_required_skills = ["Python", "SQL", "APIs", "Cloud"]

    match_a = calculate_skill_match_percentage(user_skills, job_required_skills)
    match_b = calculate_skill_match_percentage(user_skills, job_required_skills)

    assert match_a == 50
    assert match_b == 50


def test_skill_match_percentage_is_not_score_based():
    user_skills = ["Python", "APIs", "Excel"]
    job_required_skills = ["Python", "SQL", "APIs", "Cloud"]

    low_score_match = calculate_skill_match_percentage(user_skills, job_required_skills, score=15)
    high_score_match = calculate_skill_match_percentage(user_skills, job_required_skills, score=85)

    assert low_score_match == high_score_match == 50
