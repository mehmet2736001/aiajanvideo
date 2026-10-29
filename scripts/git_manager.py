"""
scripts/git_manager.py
Instant Git & GitHub Backup & Rollback Manager
Notebook Video AI Studio Pro
"""

import os
import time
import subprocess
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_git(args: List[str]) -> subprocess.CompletedProcess:
    """Executes a git command in BASE_DIR with UTF-8 encoding."""
    return subprocess.run(
        ["git"] + args,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )


def get_git_status() -> Dict[str, Any]:
    """Returns current git repository status, branch, remote, and uncommitted changes."""
    # Check if .git exists
    if not os.path.exists(os.path.join(BASE_DIR, ".git")):
        return {"initialized": False, "message": "Git deposu başlatılmamış."}

    # Branch
    res_branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    branch = res_branch.stdout.strip() if res_branch.returncode == 0 else "main"

    # Remote URL
    res_remote = run_git(["remote", "get-url", "origin"])
    remote_url = res_remote.stdout.strip() if res_remote.returncode == 0 else None

    # Latest commit
    res_log = run_git(["log", "-1", "--format=%h||%s||%cr||%an"])
    latest_commit = None
    if res_log.returncode == 0 and res_log.stdout.strip():
        parts = res_log.stdout.strip().split("||")
        if len(parts) >= 4:
            latest_commit = {
                "hash": parts[0],
                "message": parts[1],
                "relative_date": parts[2],
                "author": parts[3]
            }

    # Status / Modified files
    res_status = run_git(["status", "--porcelain"])
    changed_files = [line.strip() for line in res_status.stdout.splitlines() if line.strip()]

    return {
        "initialized": True,
        "branch": branch,
        "remote_url": remote_url,
        "has_remote": bool(remote_url),
        "latest_commit": latest_commit,
        "has_uncommitted_changes": len(changed_files) > 0,
        "changed_files_count": len(changed_files)
    }


def create_git_backup(commit_message: Optional[str] = None, push_to_remote: bool = True) -> Dict[str, Any]:
    """
    Stages all modified files (respecting .gitignore), creates a timestamped commit,
    and pushes to GitHub remote if configured.
    """
    # 1. Initialize git if not present
    if not os.path.exists(os.path.join(BASE_DIR, ".git")):
        run_git(["init"])
        run_git(["branch", "-M", "main"])

    # 2. Add files
    res_add = run_git(["add", "."])
    if res_add.returncode != 0:
        return {"success": False, "message": f"Dosyalar eklenemedi: {res_add.stderr}"}

    # 3. Check if there are changes to commit
    res_diff = run_git(["status", "--porcelain"])
    if not res_diff.stdout.strip():
        status = get_git_status()
        return {
            "success": True,
            "message": "Değişiklik yok. Sistem zaten en güncel yedekleme durumunda.",
            "status": status
        }

    # 4. Commit
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    msg = commit_message.strip() if commit_message else f"Yedekleme: {timestamp} (Notebook Video AI)"
    res_commit = run_git(["commit", "-m", msg])
    if res_commit.returncode != 0:
        return {"success": False, "message": f"Commit hatası: {res_commit.stderr}"}

    # 5. Push to remote if requested and remote exists
    push_result = None
    status = get_git_status()
    if push_to_remote and status.get("has_remote"):
        res_push = run_git(["push", "-u", "origin", status.get("branch", "main")])
        push_result = {
            "pushed": res_push.returncode == 0,
            "output": res_push.stdout if res_push.returncode == 0 else res_push.stderr
        }

    return {
        "success": True,
        "message": f"Yedekleme başarıyla oluşturuldu: {msg}",
        "commit": get_git_status().get("latest_commit"),
        "push": push_result
    }


def list_git_history(limit: int = 15) -> List[Dict[str, Any]]:
    """Returns the list of recent commits with metadata."""
    if not os.path.exists(os.path.join(BASE_DIR, ".git")):
        return []

    res = run_git(["log", f"-{limit}", "--format=%h||%s||%cd||%cr||%an", "--date=format:%Y-%m-%d %H:%M"])
    if res.returncode != 0:
        return []

    commits = []
    for line in res.stdout.splitlines():
        parts = line.strip().split("||")
        if len(parts) >= 5:
            commits.append({
                "hash": parts[0],
                "message": parts[1],
                "date": parts[2],
                "relative": parts[3],
                "author": parts[4]
            })
    return commits


def rollback_to_commit(commit_hash: str) -> Dict[str, Any]:
    """Rolls back the repository to a specific commit hash."""
    if not os.path.exists(os.path.join(BASE_DIR, ".git")):
        return {"success": False, "message": "Git deposu bulunamadı."}

    res = run_git(["checkout", commit_hash.strip()])
    if res.returncode == 0:
        return {"success": True, "message": f"{commit_hash} sürümüne başarıyla geri dönüldü."}
    else:
        return {"success": False, "message": f"Geri dönüş hatası: {res.stderr}"}
