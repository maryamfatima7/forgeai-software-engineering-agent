from pathlib import Path

from app.code_intelligence.interfaces import FileMetadata, RepositoryScanner


class DefaultRepositoryScanner(RepositoryScanner):
    IGNORED_DIRECTORIES = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build"}

    def scan(self, repository_path: Path) -> list[FileMetadata]:
        files: list[FileMetadata] = []
        for path in repository_path.rglob("*"):
            if path.is_file() and not self._is_ignored(path, repository_path):
                stat = path.stat()
                files.append(FileMetadata(path, stat.st_size, stat.st_mtime))
        return files

    def _is_ignored(self, path: Path, repository_path: Path) -> bool:
        return any(part in self.IGNORED_DIRECTORIES for part in path.relative_to(repository_path).parts)
