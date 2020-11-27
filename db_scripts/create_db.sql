CREATE TABLE public.version (version bigint DEFAULT 0);

CREATE TABLE logs_bad_query(
    id bigserial PRIMARY KEY,
    query text,
    text_error text,
    time timestamp without time zone
);

CREATE TABLE users(
    id uuid PRIMARY KEY,
    username varchar(255) UNIQUE,
    email text,
    password bytea,
    firstname varchar(255),
    lastname varchar(255),
    patronymic varchar(255),
    photo bytea,
    role int,
    status_active boolean DEFAULT true,
    last_login timestamp without time zone
);

CREATE TABLE users_salt(
    id bigserial PRIMARY KEY,
    user_id uuid REFERENCES public.users(id) ON DELETE CASCADE,
    salt text
);

-- Справочники для вакансии
CREATE TABLE professional_area(
    id SERIAL PRIMARY KEY,
    title text UNIQUE
);
CREATE TABLE specializations(
    id SERIAL PRIMARY KEY,
    title text UNIQUE,
    description text,
    professional_area_id int REFERENCES public.professional_area(id)
);
CREATE TABLE grade(
    id SERIAL PRIMARY KEY,
    title text UNIQUE,
    description text
);
CREATE TABLE skills(
    id SERIAL PRIMARY KEY,
    title text UNIQUE
);
CREATE TABLE work_address(
    id SERIAL PRIMARY KEY,
    title text UNIQUE
);
CREATE TABLE type_employment(
    id SERIAL PRIMARY KEY,
    title text UNIQUE
);
CREATE TABLE working_conditions(
    id SERIAL PRIMARY KEY,
    title text UNIQUE,
    description text
);
CREATE TABLE job_responsibilities(
    id SERIAL PRIMARY KEY,
    title text UNIQUE,
    description text
);
--

CREATE TABLE vacancy(
    id SERIAL PRIMARY KEY,
    specializations_id int REFERENCES public.specializations(id),
    grade_id int REFERENCES public.grade(id),
    work_address_id int REFERENCES public.work_address(id)
);

-- Отношения полей вакансии по отношению к вакансии
CREATE TABLE skills_for_a_vacancy(
    id BIGSERIAL PRIMARY KEY,
    vacancy_id int REFERENCES public.vacancy(id),
    skill_id int REFERENCES public.skills(id)
);
CREATE TABLE type_employment_for_a_vacancy(
    id BIGSERIAL PRIMARY KEY,
    vacancy_id int REFERENCES public.vacancy(id),
    type_employment_id int REFERENCES public.type_employment(id)
);
CREATE TABLE working_condition_for_a_vacancy(
    id BIGSERIAL PRIMARY KEY,
    vacancy_id int REFERENCES public.vacancy(id),
    working_condition_id int REFERENCES public.working_conditions(id)
);
CREATE TABLE job_responsibilities_for_a_vacancy(
    id BIGSERIAL PRIMARY KEY,
    vacancy_id int REFERENCES public.vacancy(id),
    job_responsibilities_id int REFERENCES public.job_responsibilities(id)
);
--
