import ast
import re

from app.repository.ingestion import RepositoryFile, RepositorySnapshot
from app.schemas.analysis import Finding, Symbol


class CodeAnalyzer:
    def analyze(self, snapshot: RepositorySnapshot, selected_paths: list[str] | None = None) -> tuple[list[Symbol], list[Finding]]:
        symbols: list[Symbol] = []
        findings: list[Finding] = []
        selected = set(selected_paths or [])
        for file in snapshot.files:
            if selected and file.path not in selected:
                continue
            if file.language == "python":
                file_symbols, file_findings = self._analyze_python(file)
            elif file.language in {"javascript", "typescript"}:
                file_symbols, file_findings = self._analyze_javascript(file)
            else:
                file_symbols, file_findings = [], self._marker_findings(file)
            symbols.extend(file_symbols)
            findings.extend(file_findings)
        return symbols, findings

    def _analyze_python(self, file: RepositoryFile) -> tuple[list[Symbol], list[Finding]]:
        symbols: list[Symbol] = []
        findings = self._marker_findings(file)
        try:
            tree = ast.parse(file.content, filename=file.path)
        except SyntaxError as error:
            findings.append(Finding(severity="high", category="syntax", file=file.path, line=error.lineno, description="Python syntax error detected.", reason=error.msg, remediation="Fix the syntax error and run the project formatter or test suite."))
            return symbols, findings
        used_names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                symbols.append(Symbol(kind="function", name=node.name, file=file.path, line=node.lineno))
                if len(node.body) > 40:
                    findings.append(Finding(severity="medium", category="maintainability", file=file.path, line=node.lineno, description=f"Function '{node.name}' is unusually large.", reason="Large functions are harder to test and reason about.", remediation="Split the function into focused helpers with explicit responsibilities."))
            elif isinstance(node, ast.ClassDef):
                symbols.append(Symbol(kind="class", name=node.name, file=file.path, line=node.lineno))
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    imported = alias.asname or alias.name.split(".")[0]
                    if imported not in used_names and imported not in {"annotations"}:
                        findings.append(Finding(severity="low", category="unused_import", file=file.path, line=node.lineno, description=f"Import '{imported}' may be unused.", reason="The imported name was not found in a load context.", remediation="Remove the import after confirming it is not needed for side effects."))
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
                findings.append(Finding(severity="high", category="risky_construct", file=file.path, line=node.lineno, description=f"Dynamic {node.func.id} usage detected.", reason="Dynamic evaluation can execute data as code.", remediation="Avoid dynamic evaluation or strictly constrain and validate the input."))
        return symbols, findings

    def _analyze_javascript(self, file: RepositoryFile) -> tuple[list[Symbol], list[Finding]]:
        symbols: list[Symbol] = []
        findings = self._marker_findings(file)
        for pattern, kind in ((r"\bfunction\s+([A-Za-z_$][\w$]*)", "function"), (r"\bclass\s+([A-Za-z_$][\w$]*)", "class"), (r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(", "function")):
            for match in re.finditer(pattern, file.content):
                symbols.append(Symbol(kind=kind, name=match.group(1), file=file.path, line=file.content.count("\n", 0, match.start()) + 1))
        for pattern, category, description, remediation in ((r"\beval\s*\(", "risky_construct", "Dynamic eval usage detected.", "Avoid eval and use explicit parsing or dispatch."), (r"child_process\.(?:exec|execSync)\s*\(", "risky_construct", "Shell command execution API detected.", "Validate arguments and prefer non-shell process APIs.")):
            for match in re.finditer(pattern, file.content):
                findings.append(Finding(severity="high", category=category, file=file.path, line=file.content.count("\n", 0, match.start()) + 1, description=description, reason="This construct can become dangerous when input is not tightly controlled.", remediation=remediation))
        return symbols, findings

    def _marker_findings(self, file: RepositoryFile) -> list[Finding]:
        findings: list[Finding] = []
        for line_number, line in enumerate(file.content.splitlines(), 1):
            if re.search(r"\b(TODO|FIXME)\b", line, re.IGNORECASE):
                findings.append(Finding(severity="low", category="todo", file=file.path, line=line_number, description="TODO or FIXME marker found.", reason="The source identifies unfinished or deferred work.", remediation="Track the work in an issue or resolve it before release."))
        return findings
