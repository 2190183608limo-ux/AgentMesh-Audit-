import asyncio
from celery import Celery
from git import Repo

app = Celery('audit_swarm', broker='redis://localhost:6379/0')

async def scan_and_dispatch(repo_path: str):
    repo = Repo(repo_path)
    changed_files = [item.a_path for item in repo.index.diff(None)]
    # 按语言和规则类型拆解任务
    tasks = []
    for f in changed_files:
        if f.endswith('.py'):
            tasks.append({'file': f, 'type': 'security', 'model': 'claude-3.5'})
            tasks.append({'file': f, 'type': 'architecture', 'model': 'gpt-4'})
    # 分发到不同节点的 Worker Agent
    for t in tasks:
        app.send_task('worker_agent.run_audit', args=[t], queue=t['model'])
    return tasks
