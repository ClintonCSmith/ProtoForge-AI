import os
from celery import Celery
from celery.schedules import crontab
from kombu import Queue

celery_app = Celery(
    'protoforge',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone="UTC",
    enable_utc=True,
    task_queues=[Queue('default'), Queue('evolution')],
    task_default_queue='default',
    task_soft_time_limit=600,
    task_time_limit=900,
    worker_max_tasks_per_child=50,
    beat_schedule={
        'self-evolution-nightly': {
            'task': 'agents.self_evolution.run_evolution_pipeline',
            'schedule': crontab(hour=2, minute=0),
        },
    },
)
