# 主控节点
celery -A master worker --loglevel=info
# Worker 节点（可横向扩展）
celery -A worker_agent worker -Q gpt-4 --concurrency=4
celery -A worker_agent worker -Q claude-3.5 --concurrency=4
