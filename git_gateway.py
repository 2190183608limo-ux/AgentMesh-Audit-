from git import Repo
import subprocess

def push_and_check(filename: str, content: str):
    repo = Repo("cloud_repo")
    file_path = f"cloud_repo/{filename}"
    with open(file_path, "w") as f:
        f.write(content)
    repo.index.add([filename])
    repo.index.commit(f"Agent修复: {filename}")
    # 运行合规检查（如 pylint, safety, license 扫描）
    if not compliance_check(file_path):
        repo.git.reset('HEAD~1')
        raise Exception("合规检查未通过，已驳回")
    repo.remote(name='origin').push()
    return True

def compliance_check(file_path: str) -> bool:
    # 简化示例：必须通过 pylint 且无高危 CVE
    pylint = subprocess.run(["pylint", file_path], capture_output=True)
    safety = subprocess.run(["safety", "check", "--file", file_path], capture_output=True)
    return pylint.returncode == 0 and safety.returncode == 0
