# backend/app/services/entity_extractor.py
"""
Entity extractor using regex (fallback if ONNX NER is not available)
"""

import re
from typing import List, Dict, Any

# ============================================
# IDENTITAS DIRI
# ============================================

def extract_name(text: str) -> str:
    """Ekstrak nama dari CV - prioritaskan baris pertama"""
    lines = text.strip().split('\n')
    
    # Kata kunci yang BUKAN nama (header section)
    skip_keywords = [
        'top skills', 'keahlian teratas', 'skills', 'pengalaman', 'experience',
        'pendidikan', 'education', 'contact', 'kontak', 'profile', 'profil',
        'summary', 'ringkasan', 'cv', 'curriculum vitae', 'resume',
        'work', 'kerja', 'projects', 'proyek', 'portfolio', 'portofolio'
    ]
    
    # Cek 5 baris pertama (prioritas)
    for i, line in enumerate(lines[:5]):
        line = line.strip()
        line_lower = line.lower()
        
        # Skip jika baris adalah header section
        if any(keyword in line_lower for keyword in skip_keywords):
            continue
        
        # Skip jika mengandung email
        if '@' in line:
            continue
        
        # Skip jika mengandung nomor telepon
        if re.search(r'(\+62|0|62)\d{8,12}', line.replace(' ', '')):
            continue
        
        # Pola nama: minimal 2 kata, huruf besar di awal
        # Contoh: "Budi Santoso", "Ani Wijaya", "Muhammad Fathir Afif"
        if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}$', line):
            if 5 < len(line) < 60:
                return line
        
        # Jika baris 1 adalah "Top Skills", cek baris 2
        if i == 0 and any(keyword in line_lower for keyword in ['top skills', 'keahlian teratas']):
            continue
    
    # Fallback: ambil baris pertama yang tidak kosong dan bukan header
    for line in lines[:10]:
        line = line.strip()
        line_lower = line.lower()
        
        if line and not any(keyword in line_lower for keyword in skip_keywords):
            if len(line) < 60 and not any(c in line for c in ['@', 'http', 'telp', 'phone']):
                # Kapitalisasi setiap kata
                return line.title()
    
    return "Unknown"

def extract_email(text: str) -> str:
    """Ekstrak email dari CV"""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)
    return match.group(0) if match else ""

def extract_phone(text: str) -> str:
    """Ekstrak nomor telepon dari CV"""
    phone_patterns = [
        r'(?:\+62|0)[0-9]{9,14}',
        r'08[0-9]{8,11}',
    ]
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return ""

def extract_location(text: str) -> str:
    """Ekstrak lokasi/alamat dari CV"""
    location_keywords = ['Jakarta', 'Bandung', 'Surabaya', 'Yogyakarta', 'Bali', 
                         'Medan', 'Semarang', 'Malang', 'Bekasi', 'Tangerang',
                         'Depok', 'Bogor', 'Solo', 'Denpasar', 'Makassar']
    for loc in location_keywords:
        if loc.lower() in text.lower():
            return loc
    return ""

# ============================================
# SKILLS
# ============================================

SKILL_DATABASE = {
    'programming': ['python', 'java', 'javascript', 'typescript', 'go', 'rust', 'c++', 'c#', 'php', 'ruby', 'swift', 'kotlin'],
    'web': ['react', 'vue', 'angular', 'django', 'flask', 'fastapi', 'spring', 'laravel', 'express', 'nextjs'],
    'database': ['sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch'],
    'data': ['pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn', 'tableau', 'power bi'],
    'devops': ['docker', 'kubernetes', 'aws', 'gcp', 'azure', 'jenkins', 'git', 'github actions', 'ci/cd'],
}

def extract_skills(text: str) -> List[str]:
    """Ekstrak skills dari CV"""
    text_lower = text.lower()
    found_skills = []
    
    for category, skills in SKILL_DATABASE.items():
        for skill in skills:
            if skill in text_lower:
                found_skills.append(skill)
    
    return sorted(list(set(found_skills)))

# ============================================
# PENGALAMAN & PENDIDIKAN
# ============================================

def extract_experience(text: str) -> str:
    """Ekstrak pengalaman kerja"""
    lines = text.split('\n')
    exp_lines = []
    in_exp = False
    
    for line in lines:
        line_lower = line.lower()
        if 'pengalaman' in line_lower or 'experience' in line_lower:
            in_exp = True
            continue
        if in_exp:
            if 'pendidikan' in line_lower or 'education' in line_lower:
                break
            if line.strip():
                exp_lines.append(line.strip())
    
    return '\n'.join(exp_lines[:10])

def extract_education(text: str) -> str:
    """Ekstrak pendidikan"""
    lines = text.split('\n')
    edu_lines = []
    in_edu = False
    
    for line in lines:
        line_lower = line.lower()
        if 'pendidikan' in line_lower or 'education' in line_lower:
            in_edu = True
            continue
        if in_edu:
            if 'pengalaman' in line_lower or 'experience' in line_lower:
                break
            if line.strip():
                edu_lines.append(line.strip())
    
    return '\n'.join(edu_lines[:5])

# ============================================
# SERTIFIKASI & LAINNYA
# ============================================

def extract_certifications(text: str) -> List[str]:
    """Ekstrak sertifikasi"""
    return []

def extract_organizations(text: str) -> List[str]:
    """Ekstrak organisasi"""
    return []

def extract_awards(text: str) -> List[str]:
    """Ekstrak penghargaan"""
    return []

def extract_projects(text: str) -> List[str]:
    """Ekstrak proyek"""
    return []

# ============================================
# FUNGSI UTAMA
# ============================================

def extract_all_entities(text: str) -> Dict[str, Any]:
    """Ekstrak semua entities dari CV"""
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "location": extract_location(text),
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "education": extract_education(text),
        "certifications": extract_certifications(text),
        "organizations": extract_organizations(text),
        "awards": extract_awards(text),
        "projects": extract_projects(text)
    }