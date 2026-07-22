from sqlalchemy import inspect, text
from app.database import engine
import logging

logger = logging.getLogger(__name__)


def ensure_profile_columns():
    inspector = inspect(engine)
    cols = [c['name'] for c in inspector.get_columns('profiles')] if 'profiles' in inspector.get_table_names() else []
    with engine.begin() as conn:
        # Add columns if missing (SQLite supports ADD COLUMN)
        if 'preferred_language' not in cols:
            logger.info('Adding column preferred_language to profiles')
            conn.execute(text('ALTER TABLE profiles ADD COLUMN preferred_language VARCHAR(50)'))
        if 'country' not in cols:
            logger.info('Adding column country to profiles')
            conn.execute(text('ALTER TABLE profiles ADD COLUMN country VARCHAR(100)'))
        if 'age' not in cols:
            logger.info('Adding column age to profiles')
            conn.execute(text('ALTER TABLE profiles ADD COLUMN age INTEGER'))
        if 'employment_status' not in cols:
            logger.info('Adding column employment_status to profiles')
            conn.execute(text('ALTER TABLE profiles ADD COLUMN employment_status VARCHAR(50)'))
        if 'skills_json' not in cols:
            logger.info('Adding column skills_json to profiles')
            conn.execute(text("ALTER TABLE profiles ADD COLUMN skills_json VARCHAR(2000) DEFAULT '[]'"))
        if 'skill_score' not in cols:
            logger.info('Adding column skill_score to profiles')
            conn.execute(text('ALTER TABLE profiles ADD COLUMN skill_score INTEGER'))
        if 'skill_level' not in cols:
            logger.info('Adding column skill_level to profiles')
            conn.execute(text('ALTER TABLE profiles ADD COLUMN skill_level VARCHAR(50)'))
        # Ensure assessments table has score_source for auditing
        a_cols = [c['name'] for c in inspector.get_columns('assessments')] if 'assessments' in inspector.get_table_names() else []
        if 'score_source' not in a_cols:
            logger.info('Adding column score_source to assessments')
            conn.execute(text("ALTER TABLE assessments ADD COLUMN score_source VARCHAR(50) DEFAULT 'rule'"))
        if 'missing_key_skill' not in a_cols:
            logger.info('Adding column missing_key_skill to assessments')
            conn.execute(text("ALTER TABLE assessments ADD COLUMN missing_key_skill VARCHAR(100)"))


def ensure_job_columns():
    inspector = inspect(engine)
    job_cols = [c['name'] for c in inspector.get_columns('jobs')] if 'jobs' in inspector.get_table_names() else []
    with engine.begin() as conn:
        if 'company_logo_url' not in job_cols:
            logger.info('Adding column company_logo_url to jobs')
            conn.execute(text('ALTER TABLE jobs ADD COLUMN company_logo_url VARCHAR(500)'))
        if 'work_type' not in job_cols:
            logger.info('Adding column work_type to jobs')
            conn.execute(text("ALTER TABLE jobs ADD COLUMN work_type VARCHAR(50) DEFAULT 'remote'"))
        if 'level' not in job_cols:
            logger.info('Adding column level to jobs')
            conn.execute(text("ALTER TABLE jobs ADD COLUMN level VARCHAR(50) DEFAULT 'mid-level'"))
        if 'salary_min' not in job_cols:
            logger.info('Adding column salary_min to jobs')
            conn.execute(text('ALTER TABLE jobs ADD COLUMN salary_min INTEGER'))
        if 'salary_max' not in job_cols:
            logger.info('Adding column salary_max to jobs')
            conn.execute(text('ALTER TABLE jobs ADD COLUMN salary_max INTEGER'))
        if 'currency' not in job_cols:
            logger.info('Adding column currency to jobs')
            conn.execute(text("ALTER TABLE jobs ADD COLUMN currency VARCHAR(10) DEFAULT 'EUR'"))
        if 'description_short' not in job_cols:
            logger.info('Adding column description_short to jobs')
            conn.execute(text('ALTER TABLE jobs ADD COLUMN description_short VARCHAR(500)'))
        if 'description_full' not in job_cols:
            logger.info('Adding column description_full to jobs')
            conn.execute(text('ALTER TABLE jobs ADD COLUMN description_full VARCHAR(4000)'))
        if 'required_skills' not in job_cols:
            logger.info('Adding column required_skills to jobs')
            conn.execute(text("ALTER TABLE jobs ADD COLUMN required_skills VARCHAR(2000) DEFAULT '[]'"))
        if 'date_posted' not in job_cols:
            logger.info('Adding column date_posted to jobs')
            conn.execute(text('ALTER TABLE jobs ADD COLUMN date_posted TIMESTAMP'))
        if 'application_url' not in job_cols:
            logger.info('Adding column application_url to jobs')
            conn.execute(text('ALTER TABLE jobs ADD COLUMN application_url VARCHAR(500)'))
        if 'is_active' not in job_cols:
            logger.info('Adding column is_active to jobs')
            conn.execute(text("ALTER TABLE jobs ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
