import unittest
import asyncio
import os
from agents.semantic_tagger.tagger import SemanticTagger
from agents.semantic_tagger.connector import MockAIModelConnector
from agents.semantic_tagger.models import TagCategory

class TestSemanticTagger(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.connector = MockAIModelConnector()
        self.tagger = SemanticTagger(self.connector)
        self.test_file = "tests/test_semantic_tagger_tmp.txt"
        with open(self.test_file, "w") as f:
            f.write("If you buy now, we will process your order immediately. Transaction is secure.")

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    async def test_tag_file(self):
        analysis = await self.tagger.tag_file(self.test_file)
        self.assertEqual(analysis.file_path, self.test_file)
        self.assertTrue(any(t.tag_name == "Decision Logic" for t in analysis.tags))
        self.assertTrue(any(t.tag_name == "Persuasion" for t in analysis.tags))
        self.assertTrue(any(t.tag_name == "Financial Flow" for t in analysis.tags))

    async def test_tag_text(self):
        text = "Ethical logic dictates that truth is paramount."
        analysis = await self.tagger.tag_text(text)
        self.assertTrue(any(t.category == TagCategory.PHILOSOPHY for t in analysis.tags))
        self.assertTrue(any(t.tag_name == "Ethical Logic" for t in analysis.tags))

if __name__ == "__main__":
    unittest.main()
