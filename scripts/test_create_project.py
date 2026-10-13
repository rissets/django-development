import importlib.util
import stat
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "starter_generator", Path(__file__).with_name("create_project.py")
)
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class GeneratorTests(unittest.TestCase):
    def test_copy_modes_lock_name_private_unique_secret_and_migrations(self):
        with tempfile.TemporaryDirectory() as directory:
            secrets = []
            for mode in ("fullstack", "api", "hybrid"):
                target = generator.create_project(
                    Path(directory) / mode, name=f"app-{mode}", mode=mode
                )
                values = dict(
                    line.split("=", 1) for line in (target / ".env").read_text().splitlines()
                )
                self.assertEqual(values["APP_MODE"], mode)
                self.assertGreaterEqual(len(values["DJANGO_SECRET_KEY"]), 50)
                secrets.append(values["DJANGO_SECRET_KEY"])
                self.assertEqual(stat.S_IMODE((target / ".env").stat().st_mode), 0o600)
                self.assertIn(f'name = "app-{mode}"', (target / "pyproject.toml").read_text())
                self.assertIn(f'name = "app-{mode}"', (target / "uv.lock").read_text())
                self.assertTrue((target / "apps/accounts/migrations/0001_initial.py").is_file())
                self.assertFalse((target / ".venv").exists())
            self.assertEqual(len(set(secrets)), 3)

    def test_existing_directory_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "existing"
            target.mkdir()
            sentinel = target / "keep.txt"
            sentinel.write_text("User work")
            with self.assertRaises(FileExistsError):
                generator.create_project(target, name="safe-app", mode="hybrid")
            self.assertEqual(sentinel.read_text(), "User work")

    def test_invalid_name_or_mode_rejected_before_creating_target(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "invalid"
            for name, mode in (("bad\nname", "hybrid"), ("safe-app", "unknown")):
                with self.assertRaises(ValueError):
                    generator.create_project(target, name=name, mode=mode)
                self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
