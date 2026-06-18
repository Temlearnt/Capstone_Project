# backend/app/services/section_extractor.py
import re
from typing import List, Dict, Any

# ============================================
# SKILL DATABASE (Lebih lengkap)
# ============================================

SKILL_DATABASE = {
    'programming': ['python', 'java', 'javascript', 'typescript', 'go', 'rust', 'c++', 'c#', 'php', 'ruby', 'swift', 'kotlin', 'golang'],
    'web_framework': ['react', 'vue', 'angular', 'django', 'flask', 'fastapi', 'spring', 'laravel', 'express', 'nextjs', 'nuxt'],
    'database': ['sql', 'postgresql', 'mysql', 'mongodb', 'oracle', 'redis', 'elasticsearch', 'mariadb', 'firebase', 'dynamodb'],
    'data_science': ['pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn', 'matplotlib', 'seaborn', 'keras', 'opencv', 'nltk'],
    'cloud_devops': ['docker', 'kubernetes', 'aws', 'gcp', 'azure', 'jenkins', 'git', 'github actions', 'ci/cd', 'terraform', 'ansible'],
    'bi_tools': ['tableau', 'power bi', 'looker', 'metabase', 'qlik', 'google data studio', 'superset'],
    'soft_skills': ['komunikasi', 'leadership', 'problem solving', 'team work', 'manajemen waktu', 'public speaking', 'critical thinking', 'adaptability']
}

def extract_all_skills(text: str) -> List[str]:
    """Ekstrak semua skill dari teks"""
    text_lower = text.lower()
    found_skills = []
    
    for category, skills in SKILL_DATABASE.items():
        for skill in skills:
            if skill in text_lower:
                found_skills.append(skill)
    
    # Deduplicate and sort
    return sorted(list(set(found_skills)))

# ============================================
# SECTION EXTRACTORS
# ============================================

def extract_section(text: str, section_name: str, keywords: List[str], max_lines: int = 10) -> str:
    """
    Generic function to extract a section from CV
    """
    lines = text.split('\n')
    section_lines = []
    in_section = False
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        # Check if this line starts the section
        if any(kw in line_lower for kw in keywords):
            in_section = True
            continue
        
        # Check if we've reached the end (next section)
        if in_section:
            next_section_keywords = ['pendidikan', 'education', 'pengalaman', 'experience', 
                                      'sertifikasi', 'certification', 'organisasi', 'organization',
                                      'penghargaan', 'award', 'proyek', 'project']
            if any(kw in line_lower for kw in next_section_keywords):
                break
            
            if line.strip() and len(section_lines) < max_lines:
                section_lines.append(line.strip())
    
    return '\n'.join(section_lines)

def extract_experience(text: str) -> Dict[str, Any]:
    """Extract experience section"""
    keywords = ['pengalaman kerja', 'work experience', 'pengalaman', 'experience', 'riwayat pekerjaan']
    exp_text = extract_section(text, 'experience', keywords, max_lines=15)
    
    # Extract companies
    companies = []
    company_patterns = [
        r'(?:di|at|–|-)\s*([A-Z][a-zA-Z\s&]+)(?:\n|,|\.)',
        r'^([A-Z][a-zA-Z\s&]+)(?:\n|,|\.)'
    ]
    
    for line in exp_text.split('\n'):
        for pattern in company_patterns:
            match = re.search(pattern, line)
            if match:
                companies.append(match.group(1).strip())
                break
    
    return {
        "full_text": exp_text[:1000],
        "companies": list(set(companies))[:5],
        "years": extract_experience_years(exp_text)
    }

def extract_experience_years(text: str) -> float:
    """Extract total years of experience"""
    patterns = [
        r'(\d+)\+?\s*(?:tahun|years?)\s*(?:pengalaman|experience)',
        r'(?:pengalaman|experience)\s*(\d+)\+?\s*(?:tahun|years?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return float(match.group(1))
    return 0.0

def extract_education(text: str) -> Dict[str, Any]:
    """Extract education section"""
    keywords = ['pendidikan', 'education', 'riwayat pendidikan']
    edu_text = extract_section(text, 'education', keywords, max_lines=8)
    
    # Detect education level
    edu_level = "Unknown"
    level_patterns = {
        's3': ['doktor', 'doctor', 'phd', 's3'],
        's2': ['magister', 'master', 's2'],
        's1': ['sarjana', 'bachelor', 's1', 'strata 1'],
        'd4': ['d4', 'diploma 4'],
        'd3': ['d3', 'diploma 3'],
        'sma': ['sma', 'smk', 'sekolah menengah', 'high school']
    }
    
    edu_lower = edu_text.lower()
    for level, patterns in level_patterns.items():
        if any(p in edu_lower for p in patterns):
            edu_level = level.upper()
            break
    
    return {
        "full_text": edu_text[:500],
        "level": edu_level
    }

def extract_certifications(text: str) -> List[str]:
    """Extract certifications section"""
    keywords = ['sertifikasi', 'certification', 'sertifikat', 'certificate']
    cert_text = extract_section(text, 'certifications', keywords, max_lines=10)
    
    certs = []
    for line in cert_text.split('\n'):
        line = line.strip()
        if line and len(line) > 5 and len(line) < 200:
            certs.append(line)
    
    return certs[:10]

def extract_organizations(text: str) -> List[str]:
    """Extract organizations section"""
    keywords = ['organisasi', 'organization', 'himpunan', 'komunitas', 'community', 'volunteer']
    org_text = extract_section(text, 'organizations', keywords, max_lines=10)
    
    orgs = []
    for line in org_text.split('\n'):
        line = line.strip()
        if line and len(line) > 5 and len(line) < 200:
            orgs.append(line)
    
    return orgs[:10]

def extract_awards(text: str) -> List[str]:
    """Extract awards section"""
    keywords = ['penghargaan', 'award', 'prestasi', 'achievement', 'juara', 'winner']
    award_text = extract_section(text, 'awards', keywords, max_lines=10)
    
    awards = []
    for line in award_text.split('\n'):
        line = line.strip()
        if line and len(line) > 5 and len(line) < 200:
            awards.append(line)
    
    return awards[:10]

def extract_projects(text: str) -> List[str]:
    """Extract projects section"""
    keywords = ['proyek', 'project', 'portofolio', 'portfolio']
    project_text = extract_section(text, 'projects', keywords, max_lines=15)
    
    projects = []
    for line in project_text.split('\n'):
        line = line.strip()
        if line and len(line) > 5:
            projects.append(line)
    
    return projects[:10]

def extract_publications(text: str) -> List[str]:
    """Extract publications section"""
    keywords = ['publikasi', 'publication', 'jurnal', 'journal', 'paper', 'artikel', 'conference']
    pub_text = extract_section(text, 'publications', keywords, max_lines=10)
    
    pubs = []
    for line in pub_text.split('\n'):
        line = line.strip()
        if line and len(line) > 10:
            pubs.append(line)
    
    return pubs[:10]

def extract_summary(text: str) -> str:
    """Extract summary/profile section (usually at the beginning)"""
    lines = text.split('\n')
    
    # Check first 20 lines for summary
    summary_lines = []
    in_summary = False
    
    for i, line in enumerate(lines[:20]):
        line_lower = line.lower()
        if 'summary' in line_lower or 'profile' in line_lower or 'ringkasan' in line_lower:
            in_summary = True
            continue
        if in_summary:
            if not line.strip():
                break
            summary_lines.append(line.strip())
    
    if not summary_lines and lines:
        # Take first paragraph as summary
        for line in lines[:5]:
            if line.strip() and len(line.strip()) > 20:
                summary_lines.append(line.strip())
                break
    
    return ' '.join(summary_lines)[:300]

# ============================================
# MAIN FUNCTION
# ============================================

def extract_sections(text: str) -> Dict[str, Any]:
    """
    Ekstraksi semua section dari CV.
    Output: dictionary lengkap berisi semua informasi CV.
    """
    return {
        # Skills
        "skills": extract_all_skills(text),
        
        # Experience
        "experience": extract_experience(text),
        
        # Education
        "education": extract_education(text),
        
        # Summary
        "summary": extract_summary(text),
        
        # Additional sections
        "certifications": extract_certifications(text),
        "organizations": extract_organizations(text),
        "awards": extract_awards(text),
        "projects": extract_projects(text),
        "publications": extract_publications(text),
        
        # Raw (for debugging)
        "raw_text_preview": text[:300]
    }


def extract_sections_batch(texts: list) -> list:
    """Ekstrak sections untuk banyak teks"""
    return [extract_sections(t) for t in texts]