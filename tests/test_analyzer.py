import unittest
import os
import shutil
from agents.structure_analyzer.analyzer import CodeStructureAnalyzer

class TestCodeStructureAnalyzer(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/test_analyzer_tmp"
        os.makedirs(self.test_dir, exist_ok=True)
        self.test_file = os.path.join(self.test_dir, "sample.py")

        with open(self.test_file, "w") as f:
            f.write("""
import os
from typing import List

@decorator1
class MyClass(BaseClass):
    '''Docstring'''
    def __init__(self, val):
        self.val = val

    @property
    def my_method(self):
        return self.val

def my_function(a: int, b: str):
    return a

async def my_async_func():
    pass
""")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_analyzer(self):
        analyzer = CodeStructureAnalyzer(self.test_file)
        analysis = analyzer.analyze()

        self.assertEqual(analysis.file_name, "sample.py")
        self.assertEqual(len(analysis.classes), 1)
        self.assertEqual(analysis.classes[0].name, "MyClass")
        self.assertIn("BaseClass", analysis.classes[0].bases)
        self.assertIn("decorator1", analysis.classes[0].decorators)

        self.assertEqual(len(analysis.classes[0].methods), 2)
        method_names = [m.name for m in analysis.classes[0].methods]
        self.assertIn("__init__", method_names)
        self.assertIn("my_method", method_names)

        self.assertEqual(len(analysis.functions), 2)
        func_names = [f.name for f in analysis.functions]
        self.assertIn("my_function", func_names)
        self.assertIn("my_async_func", func_names)

        self.assertEqual(len(analysis.imports), 2)
        modules = [i.module for i in analysis.imports]
        self.assertIn("os", modules)
        self.assertIn("typing", modules)

if __name__ == "__main__":
    unittest.main()
