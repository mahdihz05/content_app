import logging
from ai.models import AIJob

logger = logging.getLogger(__name__)


class AIJobService:

    @staticmethod
    def create_job(
        user,
        job_type,
        media_type="text",
        content_item=None,
        parent_job=None,
        input_data=None
    ):

        job = AIJob.objects.create(
            user=user,
            job_type=job_type,
            media_type=media_type,
            content_item=content_item,
            parent_job=parent_job,
            input_data=input_data or {},
            status="pending"
        )

        logger.info(f"AIJob created: {job.id}")

        return job


    @staticmethod
    def start_job(job_id):

        job = AIJob.objects.get(id=job_id)

        job.status = "running"
        job.save(update_fields=["status"])

        logger.info(f"AIJob started: {job.id}")

        return job


    @staticmethod
    def complete_job(job_id, output_data=None):

        job = AIJob.objects.get(id=job_id)

        job.status = "completed"
        job.output_data = output_data or {}

        job.save(update_fields=["status", "output_data"])

        logger.info(f"AIJob completed: {job.id}")

        return job


    @staticmethod
    def fail_job(job_id, error_message):

        job = AIJob.objects.get(id=job_id)

        job.status = "failed"
        job.error = error_message

        job.save(update_fields=["status", "error"])

        logger.error(f"AIJob failed: {job.id} | {error_message}")

        return job


    @staticmethod
    def retry_job(job_id):

        job = AIJob.objects.get(id=job_id)

        job.status = "pending"
        job.error = ""

        job.save(update_fields=["status", "error"])

        logger.info(f"AIJob retry: {job.id}")

        return job


    @staticmethod
    def delete_job(job_id):

        job = AIJob.objects.get(id=job_id)

        logger.info(f"AIJob deleted: {job.id}")

        job.delete()


    @staticmethod
    def get_job(job_id):

        return AIJob.objects.get(id=job_id)


    @staticmethod
    def list_user_jobs(user):

        return AIJob.objects.filter(user=user).order_by("-created_at")
