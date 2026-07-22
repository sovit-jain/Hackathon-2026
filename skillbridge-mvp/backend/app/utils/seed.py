import json
import logging
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.job import Job
from app.models.lesson import Lesson

logger = logging.getLogger(__name__)


def seed_database() -> None:
    logger.info("Seeding database if needed")
    db: Session = SessionLocal()
    try:
        from app.data.lessons import LESSONS

        existing_lessons = {(lesson.title, lesson.category, lesson.level) for lesson in db.query(Lesson).all()}
        lesson_count = 0
        for lesson_data in LESSONS:
            lesson_key = (lesson_data["title"], lesson_data["category"], lesson_data["level"])
            if lesson_key not in existing_lessons:
                db.add(Lesson(**lesson_data))
                existing_lessons.add(lesson_key)
                lesson_count += 1
        if lesson_count:
            logger.info("Seeded %d lessons", lesson_count)

        from app.data.jobs import JOBS

        existing_jobs = {(job.title, job.company, job.role): job for job in db.query(Job).all()}
        job_count = 0
        for job_data in JOBS:
            job_key = (job_data["title"], job_data["company"], job_data["role"])
            normalized_job_data = dict(job_data)
            normalized_job_data["required_skills"] = json.dumps(normalized_job_data.get("required_skills", []))
            existing_job = existing_jobs.get(job_key)
            if existing_job is None:
                new_job = Job(**normalized_job_data)
                db.add(new_job)
                existing_jobs[job_key] = new_job
                job_count += 1
            else:
                for field, value in job_data.items():
                    if getattr(existing_job, field, None) in (None, "", [], False, 0):
                        setattr(existing_job, field, value)
        if job_count:
            logger.info("Seeded %d jobs", job_count)

        db.commit()
    finally:
        db.close()
        logger.info("Database seed complete")
