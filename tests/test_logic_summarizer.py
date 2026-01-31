import unittest
import asyncio
import os
from agents.logic_summarizer.summarizer import LogicSummarizer
from agents.logic_summarizer.connector import MockLLMConnector
from agents.logic_summarizer.utils import chunk_text

class TestLogicSummarizer(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.connector = MockLLMConnector()
        self.summarizer = LogicSummarizer(self.connector)
        self.test_file = "tests/test_logic_summarizer_tmp.py"
        with open(self.test_file, "w") as f:
            f.write("def hello():\n    print('world')\n" * 100)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_chunk_text(self):
        text = "a\n" * 5000
        chunks = chunk_text(text, max_chunk_size=2000)
        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 2001)

    async def test_summarize_file(self):
        result = await self.summarizer.summarize_file(self.test_file)
        self.assertEqual(result.file_path, self.test_file)
        self.assertIsInstance(result.analysis.summary, str)
        self.assertEqual(result.analysis.role, "utility")

    async def test_summarize_text(self):
        result = await self.summarizer.summarize_text("print('test')", label="test_label")
        self.assertEqual(result.file_path, "test_label")
        self.assertTrue("mock summary" in result.analysis.summary.lower())

if __name__ == "__main__":
    unittest.main()
