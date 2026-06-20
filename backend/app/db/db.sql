-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.job_roles (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  name character varying NOT NULL UNIQUE,
  category character varying,
  default_skills ARRAY,
  description text,
  created_at timestamp without time zone DEFAULT now(),
  suggested_jd text,
  CONSTRAINT job_roles_pkey PRIMARY KEY (id)
);
CREATE TABLE public.companies (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  name character varying NOT NULL,
  email character varying NOT NULL UNIQUE,
  phone character varying,
  address text,
  logo_url text,
  website character varying,
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  CONSTRAINT companies_pkey PRIMARY KEY (id)
);
CREATE TABLE public.users (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  company_id uuid,
  email character varying NOT NULL UNIQUE,
  full_name character varying NOT NULL,
  password_hash character varying,
  role character varying DEFAULT 'hr'::character varying,
  is_active boolean DEFAULT true,
  last_login timestamp without time zone,
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  avatar_url text,
  phone character varying,
  CONSTRAINT users_pkey PRIMARY KEY (id),
  CONSTRAINT users_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id)
);
CREATE TABLE public.screening_sessions (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  company_id uuid,
  user_id uuid,
  job_role_id uuid,
  job_description text NOT NULL,
  custom_skills ARRAY,
  status character varying DEFAULT 'pending'::character varying,
  total_cvs integer DEFAULT 0,
  progress integer DEFAULT 0,
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  completed_at timestamp without time zone,
  weights jsonb DEFAULT '{"skills": 40, "education": 30, "experience": 30}'::jsonb,
  CONSTRAINT screening_sessions_pkey PRIMARY KEY (id),
  CONSTRAINT screening_sessions_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id),
  CONSTRAINT screening_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id),
  CONSTRAINT screening_sessions_job_role_id_fkey FOREIGN KEY (job_role_id) REFERENCES public.job_roles(id)
);
CREATE TABLE public.candidates (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  screening_id uuid,
  name character varying,
  email character varying,
  phone character varying,
  skills ARRAY,
  experience text,
  education text,
  match_score double precision,
  rank integer,
  original_filename character varying,
  original_cv_url text,
  created_at timestamp without time zone DEFAULT now(),
  summary text,
  certifications jsonb DEFAULT '[]'::jsonb,
  organizations jsonb DEFAULT '[]'::jsonb,
  awards jsonb DEFAULT '[]'::jsonb,
  publications jsonb DEFAULT '[]'::jsonb,
  projects jsonb DEFAULT '[]'::jsonb,
  experience_years double precision DEFAULT 0,
  score_breakdown jsonb DEFAULT '{}'::jsonb,
  matched_skills ARRAY DEFAULT '{}'::text[],
  missing_skills ARRAY DEFAULT '{}'::text[],
  viewed boolean DEFAULT false,
  CONSTRAINT candidates_pkey PRIMARY KEY (id),
  CONSTRAINT candidates_screening_id_fkey FOREIGN KEY (screening_id) REFERENCES public.screening_sessions(id)
);
CREATE TABLE public.candidate_notes (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  candidate_id uuid,
  user_id uuid,
  note text,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT candidate_notes_pkey PRIMARY KEY (id),
  CONSTRAINT candidate_notes_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidates(id),
  CONSTRAINT candidate_notes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
