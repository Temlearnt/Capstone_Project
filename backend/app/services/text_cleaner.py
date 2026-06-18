# backend/app/services/text_cleaner.py
import re
import string

# Stopwords Bahasa Indonesia (lebih lengkap)
STOPWORDS = set([
    # Bahasa Indonesia
    'yang', 'dan', 'di', 'dari', 'dengan', 'untuk', 'pada', 'ke',
    'dalam', 'ini', 'itu', 'adalah', 'juga', 'sebagai', 'dapat',
    'akan', 'telah', 'bisa', 'jika', 'atau', 'karena', 'namun',
    'demikian', 'karena', 'tersebut', 'merupakan', 'yaitu', 'yakni',
    'oleh', 'para', 'bagi', 'per', 'upaya', 'saja', 'sangat',
    'begitu', 'tanpa', 'setelah', 'sebelum', 'sudah', 'belum',
    'apakah', 'bagaimana', 'kenapa', 'mengapa', 'kapan', 'dimana',
    'selain', 'sambil', 'selama', 'sementara', 'sehingga',
    
    # English
    'the', 'and', 'of', 'to', 'a', 'in', 'for', 'on', 'with',
    'by', 'is', 'are', 'be', 'at', 'from', 'as', 'an', 'so',
    'or', 'but', 'not', 'can', 'will', 'was', 'were', 'have',
    'has', 'had', 'that', 'this', 'these', 'those', 'there',
    'their', 'they', 'we', 'you', 'she', 'he', 'it', 'them'
])

# Skill yang mengandung angka (jangan dihapus angkanya)
NUMERIC_SKILLS = {
    'python3', 'c++', 'c#', 'asp.net', 'node.js', '.net',
    'web3', 'ai2', 'golang1', 'rust2021', 'java17', 'jdk11'
}

def clean_text(text: str, remove_numbers: bool = False) -> str:
    """
    Membersihkan teks CV.
    
    Args:
        text: Teks yang akan dibersihkan
        remove_numbers: Jika True, hapus angka (default False)
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Hapus karakter khusus tapi pertahankan skill dengan angka
    if not remove_numbers:
        # Simpan sementara skill numerik
        for skill in NUMERIC_SKILLS:
            if skill in text:
                text = text.replace(skill, skill.replace('.', 'DOTMARK').replace('+', 'PLUSMARK'))
    
    # Hapus tanda baca
    text = re.sub(f'[{re.escape(string.punctuation)}]', ' ', text)
    
    # Kembalikan skill numerik
    if not remove_numbers:
        text = text.replace('DOTMARK', '.').replace('PLUSMARK', '+')
    
    # Hapus angka (opsional)
    if remove_numbers:
        text = re.sub(r'\d+', ' ', text)
    
    # Tokenisasi
    words = text.split()
    
    # Hapus stopwords dan kata pendek (kecuali skill)
    cleaned_words = []
    for w in words:
        if len(w) < 2:
            continue
        if w in STOPWORDS:
            continue
        # Jangan hapus skill yang penting
        if w in NUMERIC_SKILLS:
            cleaned_words.append(w)
        else:
            cleaned_words.append(w)
    
    # Gabung kembali
    clean = ' '.join(cleaned_words)
    
    # Hapus whitespace berlebih
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    return clean


def clean_text_for_skill_extraction(text: str) -> str:
    """Bersihkan teks khusus untuk ekstraksi skill (tidak hapus angka)"""
    return clean_text(text, remove_numbers=False)


def clean_text_for_similarity(text: str) -> str:
    """Bersihkan teks untuk similarity matching (boleh hapus angka)"""
    return clean_text(text, remove_numbers=True)


def clean_batch(texts: list, remove_numbers: bool = False) -> list:
    """Bersihkan banyak teks sekaligus"""
    return [clean_text(t, remove_numbers) for t in texts]
    
def detect_language(text: str) -> str:
    """Deteksi apakah teks dominan Indonesia atau Inggris"""
    text_lower = text.lower()
    id_words = sum(1 for w in INDONESIAN_STOPWORDS if w in text_lower)
    en_words = sum(1 for w in ENGLISH_STOPWORDS if w in text_lower)
    return "id" if id_words > en_words else "en"