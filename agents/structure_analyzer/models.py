from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ImportMetadata(BaseModel):
    module: str
    names: List[str]
    is_internal: bool
    line_number: int

class FunctionMetadata(BaseModel):
    name: str
    args: List[str]
    decorators: List[str]
    line_number: int
    end_line_number: int
    is_method: bool = False

class ClassMetadata(BaseModel):
    name: str
    bases: List[str]
    methods: List[FunctionMetadata]
    decorators: List[str]
    line_number: int
    end_line_number: int

class FileAnalysis(BaseModel):
    file_path: str
    file_name: str
    total_lines: int
    classes: List[ClassMetadata]
    functions: List[FunctionMetadata]
    imports: List[ImportMetadata]

class ProjectAnalysis(BaseModel):
    root_path: str
    files: List[FileAnalysis]
