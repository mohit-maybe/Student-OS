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
        text = ""
        if f.endswith('.pdf'):
            text = engine.extract_text_from_pdf(f)
        elif f.endswith('.docx'):
            print("DEBUG: DOCX detected - not currently supported in ai_engine!")
        
        print(f"DEBUG: Extracted text length: {len(text)}")
        if len(text) > 0:
            print(f"DEBUG: Preview: {text[:200]}...")
    else:
        print(f"ERROR: File not found: {f}")
