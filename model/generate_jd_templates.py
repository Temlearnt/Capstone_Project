import pandas as pd
import json
import re

def generate_templates():
    input_file = 'job_postings_raw.csv'
    output_file = 'jd_templates.json'

    # 1. Baca file CSV
    print(f"Membaca dataset {input_file}...")
    try:
        df = pd.read_csv(input_file, encoding='utf-8')
    except Exception as e:
        print(f"Gagal membaca file: {e}")
        return

    if 'title_clean' not in df.columns:
        print("Kolom 'title_clean' tidak ditemukan dalam dataset!")
        return

    # Buang baris yang title_clean-nya kosong
    df = df.dropna(subset=['title_clean'])

    # Filter kata kunci yang tidak diinginkan (hanya ambil role murni)
    exclude_keywords = ['senior', 'contract', 'freelance', 'praktikant', 'werkstudent', 'intern', 'lead', 'head', 'principal', 'student']
    pattern = '|'.join(exclude_keywords)
    df = df[~df['title_clean'].str.contains(pattern, case=False, na=False)]

    # Daftar kata potong (case-insensitive)
    cut_phrases = [
        "we offer:",
        "what we offer:",
        "benefits:",
        "perks and benefits:",
        "you will receive:",
        "our offer:",
        "why join us:",
        "what you get:"
    ]
    # Bangun pola regex: cocokkan salah satu dari cut_phrases dan ambil semuanya setelahnya
    pattern_str = r'(?i)(' + '|'.join(map(re.escape, cut_phrases)) + r')'
    regex_pattern = re.compile(pattern_str)

    templates = {}

    # 2. Kelompokkan berdasarkan title_clean
    grouped = df.groupby('title_clean')

    for title, group in grouped:
        # Menghindari error tipe data float (NaN) untuk title
        if not isinstance(title, str):
            continue
            
        # -- Proses Skills --
        # Menambahkan Domain Knowledge Override agar skill relevan dengan industri nyata
        ideal_skills = {
            "analytics_engineer": ["SQL", "dbt", "Python", "Git", "BigQuery", "Snowflake", "Looker", "Airflow"],
            "bi_engineer": ["SQL", "Python", "Power BI", "Tableau", "Airflow", "dbt", "Git", "Azure"],
            "business_intelligence_analyst": ["SQL", "Power BI", "Tableau", "Excel", "Python", "Looker", "Cognos", "SSRS"],
            "data_analyst": ["SQL", "Excel", "Python", "Tableau", "Power BI", "Pandas", "NumPy", "Jupyter"],
            "data_architect": ["AWS", "Azure", "GCP", "SQL", "Spark", "Kafka", "Hadoop", "Snowflake"],
            "data_engineer": ["Python", "SQL", "Spark", "Airflow", "AWS", "Docker", "Kubernetes", "Kafka"],
            "data_scientist": ["Python", "SQL", "Machine Learning", "Scikit-learn", "Pandas", "TensorFlow", "Jupyter", "PyTorch"],
            "ml_engineer": ["Python", "Machine Learning", "TensorFlow", "PyTorch", "Docker", "AWS", "Kubeflow", "FastAPI"]
        }

        # Format key (lowercase dan spasi menjadi underscore)
        safe_key = re.sub(r'\W+', '_', title.lower()).strip('_')

        if safe_key in ideal_skills:
            sorted_skills = sorted(ideal_skills[safe_key])
        else:
            from collections import Counter
            skill_counter = Counter()
            for skills_str in group['skills_extracted'].dropna():
                if not isinstance(skills_str, str):
                    continue
                parts = [s.strip() for s in skills_str.split(';') if s.strip()]
                for part in parts:
                    skill_counter[part] += 1
            top_skills = [skill for skill, count in skill_counter.most_common(8)]
            sorted_skills = sorted(top_skills)
            
        # Format menjadi "Skill", "Skill2"
        skills_formatted = ", ".join([f'"{s}"' for s in sorted_skills])

        # -- Proses Deskripsi --
        description = ""
        # Cari deskripsi pertama yang tidak kosong
        for desc in group['description_clean'].dropna():
            if isinstance(desc, str) and desc.strip():
                description = desc.strip()
                break
        
        # Bersihkan deskripsi menggunakan regex cut_phrases
        if description:
            # Gunakan regex split untuk memotong bagian setelah frasa pemotong
            split_result = regex_pattern.split(description, maxsplit=1)
            description = split_result[0].strip()

        # Format key (lowercase dan spasi menjadi underscore)
        # Menghapus karakter non-alphanumeric selain underscore
        safe_key = re.sub(r'\W+', '_', title.lower()).strip('_')
        
        # Simpan ke dictionary
        templates[safe_key] = {
            "title": title,
            "skills": skills_formatted,
            "description": description
        }

    # 4. Simpan dictionary ke JSON
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(templates, f, indent=2, ensure_ascii=False)
        print(f"Sukses! Berhasil memproses dan menyimpan {len(templates)} role pekerjaan ke {output_file}.")
    except Exception as e:
        print(f"Gagal menyimpan JSON: {e}")

if __name__ == "__main__":
    generate_templates()
