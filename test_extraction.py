import os
from utils.ai_engine import ExamAIEngine

engine = ExamAIEngine()
files = [
    r'C:\Users\GURU\Desktop\Student OS ready\uploads\exam_docs\Whatsapp_Scan_5_March_2026_at_16.58.24.pdf',
    r'C:\Users\GURU\Desktop\Student OS ready\uploads\exam_docs\sample_paper_11.docx'
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
