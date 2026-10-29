from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_skills import validate


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "skills").mkdir()

    def skill(self, directory="example", frontmatter=None, body="# Instructions\n\nDo the work."):
        path = self.root / "skills" / directory / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        if frontmatter is None:
            frontmatter = f"name: {directory}\ndescription: When and how to use this skill."
        path.write_text(f"---\n{frontmatter}\n---\n\n{body}\n", encoding="utf-8")
        return path

    def test_empty_collection_is_valid(self):
        (self.root / "skills" / ".gitkeep").touch()
        self.assertEqual(validate(self.root), [])

    def test_yaml_block_description_and_local_references(self):
        skill = self.skill(
            frontmatter="name: example\ndescription: |\n  A multiline description.\n  Use when needed.",
            body="[Guide](references/guide%20one.md#details)\n![Icon](assets/icon.svg)\n[Site](https://example.com)\n[Section](#details)",
        )
        for name in ["references/guide one.md", "assets/icon.svg"]:
            target = skill.parent / name
            target.parent.mkdir(exist_ok=True)
            target.touch()
        self.assertEqual(validate(self.root), [])

    def test_metadata_errors(self):
        for metadata, expected in [
            ("name: [", "invalid YAML"),
            ("- example", "must be a mapping"),
            ("name: Bad_Name\ndescription: Text", "name must be lowercase"),
            ("name: another\ndescription: Text", "name must match directory"),
            ("name: example\ndescription: false", "description must be a nonempty string"),
            ("name: example\ndescription: ''", "description must be a nonempty string"),
            ("name: example\ndescription: " + "x" * 1025, "description must be a nonempty string"),
        ]:
            with self.subTest(metadata=metadata):
                self.skill(frontmatter=metadata)
                self.assertTrue(any(expected in error for error in validate(self.root)))

    def test_missing_frontmatter_and_empty_instructions(self):
        path = self.skill(body="")
        self.assertTrue(any("instructions must not be empty" in error for error in validate(self.root)))
        path.write_text("# No frontmatter", encoding="utf-8")
        self.assertTrue(any("expected YAML frontmatter" in error for error in validate(self.root)))

    def test_duplicate_names(self):
        self.skill()
        self.skill("other", frontmatter="name: example\ndescription: Another skill.")
        self.assertTrue(any("duplicate skill name" in error for error in validate(self.root)))

    def test_flat_layout_required(self):
        self.skill("category/nested", frontmatter="name: nested\ndescription: A nested skill.")
        errors = validate(self.root)
        self.assertTrue(any("missing SKILL.md" in error for error in errors))
        self.assertTrue(any("direct children" in error for error in errors))

    def test_broken_links_images_and_reference_links(self):
        self.skill(body="[Guide][guide]\n\n[guide]: missing.md\n\n![Icon](missing.png)")
        self.assertEqual(sum("broken local link" in error for error in validate(self.root)), 2)

    def test_code_examples_are_not_links(self):
        self.skill(body="```markdown\n[Example](missing.md)\n```\n\n`[Example](missing.md)`")
        self.assertEqual(validate(self.root), [])

    def test_machine_paths_and_repository_escapes_are_rejected(self):
        self.skill(body="[Machine](/tmp/example.md)\n[Outside](../../../outside.md)")
        self.assertEqual(sum("must stay inside" in error for error in validate(self.root)), 2)

    def test_readme_links_are_checked(self):
        (self.root / "README.md").write_text("[Guide](missing.md)", encoding="utf-8")
        self.assertTrue(any("broken local link" in error for error in validate(self.root)))


if __name__ == "__main__":
    unittest.main()
