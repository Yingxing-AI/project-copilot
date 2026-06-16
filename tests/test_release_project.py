import subprocess
import tempfile
import unittest
from pathlib import Path

from project_copilot.workflow.release_project import extract_tag, release_project


class ReleaseProjectTest(unittest.TestCase):
    def test_extracts_release_tag(self) -> None:
        self.assertEqual(extract_tag("发布 v0.3.0-alpha.2"), "v0.3.0-alpha.2")
        self.assertEqual(extract_tag("release 1.2.3"), "1.2.3")
        self.assertIsNone(extract_tag("发布 Alpha"))

    def test_release_runs_push_tag_and_gh_release_in_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".ai").mkdir()
            (root / ".ai" / "STATUS.md").write_text("# Status\n", encoding="utf-8")
            (root / ".ai" / "ROADMAP.md").write_text("- [x] Pytest baseline: 25 passed\n", encoding="utf-8")
            (root / "ROADMAP.md").write_text("- [x] Pytest baseline: 25 passed\n", encoding="utf-8")
            (root / "CHANGELOG.md").write_text("# Changelog\n\n## v0.3 Alpha\n\n### Added\n\n### Verified\n\n- Current baseline: 25 passed.\n", encoding="utf-8")
            (root / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
            calls: list[list[str]] = []

            def runner(_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
                calls.append(args)
                if args[:2] == ["git", "rev-parse"]:
                    return _ok("true\n")
                if args[:3] == ["git", "branch", "--show-current"]:
                    return _ok("main\n")
                if args[:3] == ["git", "remote", "get-url"]:
                    return _ok("https://github.com/example/project.git\n")
                if args[:3] == ["git", "tag", "--list"]:
                    return _ok("")
                if args[:2] == ["gh", "auth"]:
                    return _ok("Logged in\n")
                if args == ["pytest", "-q"]:
                    return _ok("25 passed in 0.01s\n")
                if args[:3] == ["git", "status", "--short"]:
                    return _ok(" M README.md\n")
                return _ok("")

            outcome = release_project(root, "v0.3.0-alpha.5", runner=runner)

            self.assertEqual(outcome.status, "success")
            self.assertIn(["git", "push", "origin", "main"], calls)
            self.assertIn(["git", "tag", "-a", "v0.3.0-alpha.5", "-m", "Project Copilot v0.3.0-alpha.5"], calls)
            self.assertIn(["git", "push", "origin", "v0.3.0-alpha.5"], calls)
            self.assertTrue(any(call[:3] == ["gh", "release", "create"] for call in calls))

    def test_release_notes_include_changes_since_previous_tag(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".ai").mkdir()
            (root / ".ai" / "STATUS.md").write_text("# Status\n", encoding="utf-8")
            (root / ".ai" / "ROADMAP.md").write_text("- [x] Pytest baseline: 25 passed\n", encoding="utf-8")
            (root / "ROADMAP.md").write_text("- [x] Pytest baseline: 25 passed\n", encoding="utf-8")
            (root / "CHANGELOG.md").write_text("# Changelog\n\n## v0.3 Alpha\n\n### Added\n\n- Release automation.\n", encoding="utf-8")
            (root / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")

            def runner(_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
                if args[:2] == ["git", "rev-parse"]:
                    return _ok("true\n")
                if args[:3] == ["git", "branch", "--show-current"]:
                    return _ok("main\n")
                if args[:3] == ["git", "remote", "get-url"]:
                    return _ok("https://github.com/example/project.git\n")
                if args == ["git", "tag", "--list", "v0.3.0-alpha.5"]:
                    return _ok("")
                if args == ["git", "tag", "--sort=-version:refname"]:
                    return _ok("v0.3.0-alpha.4\nv0.3.0-alpha.3\nproject-copilot\n")
                if args == ["git", "log", "--pretty=format:%h %s", "v0.3.0-alpha.4..HEAD"]:
                    return _ok("d92ef0f docs: clarify alpha install guidance\n")
                if args[:2] == ["gh", "auth"]:
                    return _ok("Logged in\n")
                if args == ["pytest", "-q"]:
                    return _ok("25 passed in 0.01s\n")
                if args[:3] == ["git", "status", "--short"]:
                    return _ok(" M README.md\n")
                return _ok("")

            outcome = release_project(root, "v0.3.0-alpha.5", runner=runner)

            self.assertEqual(outcome.status, "success")
            self.assertIsNotNone(outcome.release_notes)
            notes = outcome.release_notes.read_text(encoding="utf-8")
            self.assertIn("## Changes since v0.3.0-alpha.4", notes)
            self.assertIn("- d92ef0f docs: clarify alpha install guidance", notes)
            self.assertIn("## Project Changelog", notes)

    def test_release_dry_run_does_not_push_or_tag(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            calls: list[list[str]] = []

            def runner(_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
                calls.append(args)
                if args[:2] == ["git", "rev-parse"]:
                    return _ok("true\n")
                if args[:3] == ["git", "branch", "--show-current"]:
                    return _ok("main\n")
                if args[:3] == ["git", "remote", "get-url"]:
                    return _ok("https://github.com/example/project.git\n")
                if args[:3] == ["git", "tag", "--list"]:
                    return _ok("")
                if args[:2] == ["gh", "auth"]:
                    return _ok("Logged in\n")
                return _ok("")

            outcome = release_project(root, "v0.3.0-alpha.5", runner=runner, dry_run=True)

            self.assertEqual(outcome.status, "success")
            self.assertTrue(outcome.dry_run)
            self.assertIn("git push origin main", outcome.actions)
            self.assertNotIn(["git", "push", "origin", "main"], calls)
            self.assertNotIn(["gh", "auth", "status"], calls)

    def test_release_blocks_when_tag_and_package_version_do_not_match(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def runner(_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
                if args[:2] == ["git", "rev-parse"]:
                    return _ok("true\n")
                if args[:3] == ["git", "branch", "--show-current"]:
                    return _ok("main\n")
                if args[:3] == ["git", "remote", "get-url"]:
                    return _ok("https://github.com/example/project.git\n")
                if args[:3] == ["git", "tag", "--list"]:
                    return _ok("")
                if args[:1] == ["gh"]:
                    return _ok("")
                return _ok("")

            outcome = release_project(root, "v0.3.0-alpha.6", runner=runner, dry_run=True)

            self.assertEqual(outcome.status, "blocked")
            self.assertTrue(any("版本不匹配" in blocker for blocker in outcome.blockers))


def _ok(stdout: str) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout, stderr="")
