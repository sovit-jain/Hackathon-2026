from sqlalchemy import inspect, text
from app.database import engine
import logging

logger = logging.getLogger(__name__)


def ensure_profile_columns():
    inspector = inspect(engine)
    cols = [c['name'] for c in inspector.get_columns('profiles')] if 'profiles' in inspector.get_table_names() else []
    with engine.begin() as conn:
        if 'preferred_language' not in cols:
            conn.execute(text('ALTER TABLE profiles ADD COLUMN preferred_language VARCHAR(50)'))
        if 'country' not in cols:
            conn.execute(text('ALTER TABLE profiles ADD COLUMN country VARCHAR(100)'))
        if 'age' not in cols:
            conn.execute(text('ALTER TABLE profiles ADD COLUMN age INTEGER'))
        if 'employment_status' not in cols:
            conn.execute(text('ALTER TABLE profiles ADD COLUMN employment_status VARCHAR(50)'))
        if 'skills_json' not in cols:
            conn.execute(text("ALTER TABLE profiles ADD COLUMN skills_json VARCHAR(2000) DEFAULT '[]'"))
        if 'skill_score' not in cols:
            conn.execute(text('ALTER TABLE profiles ADD COLUMN skill_score INTEGER'))
        if 'skill_level' not in cols:
            conn.execute(text('ALTER TABLE profiles ADD COLUMN skill_level VARCHAR(50)'))
        # DB AI Career Navigator path columns
        if 'user_path' not in cols:
            conn.execute(text('ALTER TABLE profiles ADD COLUMN user_path VARCHAR(10)'))
        if 'current_db_position' not in cols:
            conn.execute(text('ALTER TABLE profiles ADD COLUMN current_db_position VARCHAR(200)'))
        if 'current_db_department' not in cols:
            conn.execute(text('ALTER TABLE profiles ADD COLUMN current_db_department VARCHAR(100)'))
        if 'current_designation' not in cols:
            conn.execute(text('ALTER TABLE profiles ADD COLUMN current_designation VARCHAR(50)'))
        if 'current_company' not in cols:
            conn.execute(text('ALTER TABLE profiles ADD COLUMN current_company VARCHAR(200)'))
        if 'current_external_role' not in cols:
            conn.execute(text('ALTER TABLE profiles ADD COLUMN current_external_role VARCHAR(200)'))
        if 'education' not in cols:
            conn.execute(text('ALTER TABLE profiles ADD COLUMN education VARCHAR(500)'))
        if 'certifications' not in cols:
            conn.execute(text('ALTER TABLE profiles ADD COLUMN certifications VARCHAR(500)'))
        if 'experience_years' not in cols:
            conn.execute(text('ALTER TABLE profiles ADD COLUMN experience_years INTEGER'))
        if 'jobs_unlocked' not in cols:
            conn.execute(text('ALTER TABLE profiles ADD COLUMN jobs_unlocked BOOLEAN DEFAULT FALSE'))
        if 'db_score' not in cols:
            conn.execute(text('ALTER TABLE profiles ADD COLUMN db_score INTEGER'))
        if 'score_type' not in cols:
            conn.execute(text('ALTER TABLE profiles ADD COLUMN score_type VARCHAR(50)'))
        # Assessment audit columns
        a_cols = [c['name'] for c in inspector.get_columns('assessments')] if 'assessments' in inspector.get_table_names() else []
        if 'score_source' not in a_cols:
            conn.execute(text("ALTER TABLE assessments ADD COLUMN score_source VARCHAR(50) DEFAULT 'rule'"))
        if 'missing_key_skill' not in a_cols:
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
