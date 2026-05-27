import os
from utils.ai_engine import ExamAIEngine

engine = ExamAIEngine()
# Note: Update these paths to match your local file system
files = [
    'uploads/exam_docs/sample.pdf',
    'uploads/exam_docs/sample.docx'
]

for f in files:
    if os.path.exists(f):
        print(f"DEBUG: Extracting from {f}")
        text = engine.extract_text_from_file(f)
        
        print(f"DEBUG: Extracted text length: {len(text)}")
        if len(text) > 0:
            print(f"DEBUG: Preview: {text[:200]}...")
    else:
        print(f"ERROR: File not found: {f}")
