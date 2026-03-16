import os
import re
from collections import Counter
from pdfminer.high_level import extract_text
from datetime import datetime, timedelta

class ExamAIEngine:
    def __init__(self):
        # Removed heavy libraries for 32-bit compatibility
        self.stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'else', 'when', 'at', 'from', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'in', 'on', 'of', 'for', 'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'done', 'that', 'this', 'there', 'which', 'who', 'whom', 'what', 'whose', 'where', 'how', 'each', 'every', 'either', 'neither', 'some', 'any', 'none', 'both', 'all', 'many', 'much', 'few', 'several', 'only', 'own', 'same', 'such', 'very', 'too', 'also', 'just', 'well', 'now', 'then', 'here', 'there', 'coffee', 'paper', 'marks', 'exam', 'questions', 'answer', 'time', 'date', 'roll', 'number'}
        
        # Knowledge base of chapters for major subjects (Class 10-12)
        self.knowledge_base = {
            'Physics': [
                'Electrostatics', 'Current Electricity', 'Magnetic Effects of Current', 'Magnetism', 
                'Electromagnetic Induction', 'Alternating Currents', 'Electromagnetic Waves', 'Optics', 
                'Dual Nature of Matter', 'Atoms and Nuclei', 'Electronic Devices', 'Communication Systems',
                'Units and Measurements', 'Kinematics', 'Laws of Motion', 'Work Energy and Power',
                'Rotational Motion', 'Gravitation', 'Thermodynamics', 'Oscillations', 'Waves'
            ],
            'Chemistry': [
                'Solid State', 'Solutions', 'Electrochemistry', 'Chemical Kinetics', 'Surface Chemistry', 
                'General Principles of Extraction', 'p-Block Elements', 'd and f Block Elements', 
                'Coordination Compounds', 'Haloalkanes and Haloarenes', 'Alcohols Phenols and Ethers', 
                'Aldehydes Ketones and Carboxylic Acids', 'Amines', 'Biomolecules', 'Polymers', 
                'Chemistry in Everyday Life', 'Atomic Structure', 'Chemical Bonding', 'Equilibrium'
            ],
            'Mathematics': [
                'Relations and Functions', 'Inverse Trigonometric Functions', 'Matrices', 'Determinants', 
                'Continuity and Differentiability', 'Applications of Derivatives', 'Integrals', 
                'Applications of Integrals', 'Differential Equations', 'Vector Algebra', 
                'Three Dimensional Geometry', 'Linear Programming', 'Probability', 'Sets', 'Calculus'
            ],
            'Biology': [
                'Reproduction', 'Genetics and Evolution', 'Biology and Human Welfare', 'Biotechnology', 
                'Ecology and Environment', 'Cell Structure', 'Plant Physiology', 'Human Physiology'
            ]
        }

        # Keywords to detect subject
        self.subject_keywords = {
            'Physics': ['force', 'velocity', 'electric', 'magnetic', 'charge', 'lens', 'wave', 'current', 'potential', 'energy', 'mass', 'acceleration', 'light', 'mirror'],
            'Chemistry': ['molecule', 'atom', 'reaction', 'bond', 'acid', 'base', 'solution', 'organic', 'inorganic', 'chemical', 'element', 'polymer', 'molar', 'oxidation'],
            'Mathematics': ['derivative', 'integral', 'matrix', 'vector', 'function', 'equation', 'probability', 'limit', 'triangle', 'set', 'geometric', 'algebra', 'calculus'],
            'Biology': ['cell', 'dna', 'organism', 'tissue', 'botany', 'zoology', 'evolution', 'genetics', 'plant', 'animal', 'human', 'reproduction', 'environment']
        }

    def detect_subject(self, text):
        """Detects the subject based on keyword counts."""
        text_lower = text.lower()
        scores = Counter()
        for subject, keywords in self.subject_keywords.items():
            for kw in keywords:
                # Count occurrences of keywords
                scores[subject] += len(re.findall(rf'\b{kw}\b', text_lower))
        
        if not scores:
            return None
        return scores.most_common(1)[0][0]
        
    def extract_text_from_file(self, file_path):
        """Extracts text from various file formats (PDF, DOCX, TXT)."""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return self._extract_from_pdf(file_path)
        elif ext == '.docx':
            return self._extract_from_docx(file_path)
        elif ext in ['.txt', '.md']:
            return self._extract_from_text(file_path)
        return ""

    def _extract_from_pdf(self, pdf_path):
        """Extracts text from a PDF file using multiple fallbacks."""
        # 1. Try pypdf (Fast and robust for modern PDFs)
        try:
            from pypdf import PdfReader
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            if len(text.strip()) > 100:
                print(f"DEBUG: pypdf extracted {len(text)} chars from {pdf_path}")
                return self._cleanup_text(text)
        except Exception as e:
            print(f"DEBUG: pypdf failed: {e}")

        # 2. Try pdfminer (Good for complex layouts)
        try:
            text = extract_text(pdf_path)
            if len(text.strip()) > 100:
                print(f"DEBUG: pdfminer extracted {len(text)} chars")
                return self._cleanup_text(text)
        except Exception as e:
            print(f"DEBUG: pdfminer failed: {e}")

        # 3. OCR Fallback (For scans/images)
        try:
            from pdf2image import convert_from_path
            import pytesseract
            print(f"DEBUG: Attempting OCR for {pdf_path}")
            # Note: Requires Tesseract binary and Poppler in PATH
            images = convert_from_path(pdf_path)
            text = ""
            for img in images:
                text += pytesseract.image_to_string(img)
            if len(text.strip()) > 50:
                print(f"DEBUG: OCR extracted {len(text)} chars")
                return self._cleanup_text(text)
        except Exception as e:
            # Silent failure for OCR if binaries missing, but log for debug
            print(f"DEBUG: OCR failed: {e}")

        return ""

    def _extract_from_docx(self, docx_path):
        """Extracts text from a .docx file."""
        try:
            import docx
            doc = docx.Document(docx_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            if len(text.strip()) > 50:
                print(f"DEBUG: docx extracted {len(text)} chars from {docx_path}")
                return self._cleanup_text(text)
        except Exception as e:
            print(f"DEBUG: docx extraction error: {e}")
        return ""

    def _extract_from_text(self, text_path):
        """Extracts text from a plain text file."""
        try:
            with open(text_path, 'r', encoding='utf-8', errors='ignore') as f:
                return self._cleanup_text(f.read())
        except Exception as e:
            print(f"DEBUG: text extraction error: {e}")
        return ""

    def _cleanup_text(self, text):
        # Basic cleanup
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def analyze_topics(self, docs_with_metadata):
        """
        Analyzes topics by matching extracted text against a knowledge base of chapters.
        """
        if not docs_with_metadata:
            return []

        # 1. Combine all text to detect overall subject
        combined_text = " ".join([doc['text'] for doc in docs_with_metadata])
        detected_subject = self.detect_subject(combined_text)
        
        if not detected_subject:
            print("DEBUG: Could not detect specific academic subject. Using frequency analysis.")
            return self._frequency_analysis(docs_with_metadata)

        print(f"DEBUG: Detected subject: {detected_subject}")
        chapters = self.knowledge_base.get(detected_subject, [])
        
        # 2. Score each chapter based on term overlaps
        chapter_scores = Counter()
        current_year = datetime.now().year

        for doc in docs_with_metadata:
            text_lower = doc['text'].lower()
            year_diff = current_year - (doc.get('year') or current_year)
            weight = max(1.0, 1.5 - (year_diff / 10.0)) if doc['type'] == 'Past Paper' else 2.5
            
            for chapter in chapters:
                # Break chapter name into keywords (e.g., "Current Electricity" -> ["current", "electricity"])
                chapter_keywords = [k.lower() for k in re.findall(r'\b[A-Za-z]{3,}\b', chapter)]
                
                # Simple semantic matching: how many chapter keywords appear in the text?
                match_count = 0
                for kw in chapter_keywords:
                    if kw in text_lower:
                        # Give higher points if the exact multi-word phrase appears
                        if chapter.lower() in text_lower:
                            match_count += 5
                        else:
                            match_count += 1
                
                if match_count > 0:
                    chapter_scores[chapter] += match_count * weight

        # 3. Sort and Normalize
        sorted_topics = chapter_scores.most_common(10)
        if not sorted_topics:
            return self._frequency_analysis(docs_with_metadata)
            
        max_score = sorted_topics[0][1]
        results = []
        for chapter, score in sorted_topics:
            probability = min(0.98, (score / max_score) * 0.7 + 0.25)
            importance = 'High' if probability > 0.8 else 'Medium' if probability > 0.6 else 'Low'
            results.append({
                'topic': chapter,
                'probability': round(probability * 100, 1),
                'importance': importance
            })
            
        return results

    def _frequency_analysis(self, docs_with_metadata):
        """Fallback frequency analysis for unknown subjects."""
        current_year = datetime.now().year
        word_scores = Counter()
        for doc in docs_with_metadata:
            text = doc['text'].lower()
            words = re.findall(r'\b[a-z]{4,}\b', text) # Min 4 chars for better quality
            year_diff = current_year - (doc.get('year') or current_year)
            weight = max(1.0, 1.5 - (year_diff / 10.0))
            
            filtered_words = [w for w in words if w not in self.stop_words]
            for w in filtered_words:
                word_scores[w] += weight
        
        sorted_stats = word_scores.most_common(10)
        if not sorted_stats: return []
        max_s = sorted_stats[0][1]
        return [{
            'topic': t.title(),
            'probability': round(min(0.95, (s/max_s)*0.6 + 0.2)*100, 1),
            'importance': 'High' if s/max_s > 0.8 else 'Medium'
        } for t, s in sorted_stats]

    def generate_questions(self, topics):
        """Generates likely questions using templates."""
        question_templates = [
            "Explain the concept of {topic} in detail.",
            "Derive the fundamental formula for {topic}.",
            "Solve a numerical problem based on {topic}.",
            "What are the major applications of {topic}?",
            "Discuss the historical significance of {topic}."
        ]
        
        questions = []
        import random
        for topic_data in topics[:5]:
            topic = topic_data['topic']
            template = random.choice(question_templates)
            questions.append({
                'topic': topic,
                'question': template.format(topic=topic)
            })
        return questions

    def generate_revision_plan(self, topics, days_remaining):
        """Generates a smart revision roadmap."""
        plan = []
        start_date = datetime.now()
        sorted_topics = sorted(topics, key=lambda x: x['probability'], reverse=True)
        
        for i, topic_data in enumerate(sorted_topics):
            if i >= days_remaining:
                break
            plan.append({
                'day': i + 1,
                'date': (start_date + timedelta(days=i)).strftime('%Y-%m-%d'),
                'topic': topic_data['topic']
            })
            
        return plan
