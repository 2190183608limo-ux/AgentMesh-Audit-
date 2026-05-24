from celery import Celery
import openai, anthropic, subprocess, os

app = Celery('audit_swarm', broker='redis://localhost:6379/0')

@app.task
def run_audit(task: dict):
    file = task['file']
    with open(file) as f:
        code = f.read()
    # 根据模型类型调用不同 LLM
    if task['model'] == 'claude-3.5':
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            messages=[{"role": "user", "content": f"审计并修复安全漏洞：\n{code}"}]
        )
        fixed_code = response.content[0].text
    else:
        import openai
        response = openai.ChatCompletion.create(
            model="gpt-4", messages=[{"role": "user", "content": f"检查架构规范并修复：\n{code}"}]
        )
        fixed_code = response.choices[0].message.content

    # 本地沙箱测试
    with open(f"patched_{file}", "w") as f:
        f.write(fixed_code)
    result = subprocess.run(["pytest", f"test_{file}"], capture_output=True)
    if result.returncode != 0:
        # 失败则重新推理（简化处理）
        return "fix_failed"
    
    # 上传到云端仓库并触发合规检查
    from git_gateway import push_and_check
    push_and_check(file, fixed_code)
    return "success"
