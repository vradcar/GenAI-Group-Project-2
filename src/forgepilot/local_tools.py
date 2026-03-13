from pathlib import Path
import subprocess


class LocalTools:
    def __init__(self, workspace_root: str) -> None:
        self.workspace_root = Path(workspace_root).resolve()

    def read_file(self, path: str) -> str:
        target = (self.workspace_root / path).resolve()
        return target.read_text(encoding="utf-8")

    def write_file(self, path: str, content: str) -> str:
        target = (self.workspace_root / path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Wrote {target}"

    def run_shell(self, command: str) -> str:
        result = subprocess.run(
            command,
            cwd=self.workspace_root,
            capture_output=True,
            text=True,
            shell=True,
            check=False,
        )
        output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
        return output.strip() or "(no output)"
