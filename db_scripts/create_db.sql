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
CREATE TABLE soft_requirements(
    id SERIAL PRIMARY KEY,
    title text UNIQUE
);
CREATE TABLE technologies_and_tools(
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
CREATE TABLE special_advantages(
    id SERIAL PRIMARY KEY,
    title text UNIQUE,
    description text
);
CREATE TABLE question_types(
    id SERIAL PRIMARY KEY,
    title text UNIQUE,
    description text
);
CREATE TABLE statuses_vacancy(
    id SERIAL PRIMARY KEY,
    title text UNIQUE
);
--

CREATE TABLE vacancy(
    id SERIAL PRIMARY KEY,
    specializations_id int REFERENCES public.specializations(id),
    grade_id int REFERENCES public.grade(id),
    work_address_id int REFERENCES public.work_address(id),
    create_user_id uuid REFERENCES public.users(id),
    create_date date,
    status_id int REFERENCES public.statuses_vacancy(id)
);

CREATE TABLE questons(
    id BIGSERIAL PRIMARY KEY,
    question_type_id int REFERENCES public.question_types(id),
    grade_id int REFERENCES public.grade(id),
    skill_id int REFERENCES public.skills(id),
    title varchar(255),
    question text
);

CREATE TABLE answers_on_question(
    id BIGSERIAL PRIMARY KEY,
    question_id bigint REFERENCES public.questons(id),
    answer text,
    is_true boolean DEFAULT false
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
CREATE TABLE special_advantage_for_a_vacancy(
    id BIGSERIAL PRIMARY KEY,
    vacancy_id int REFERENCES public.vacancy(id),
    special_advantage_id int REFERENCES public.special_advantages(id)
);
CREATE TABLE soft_requirement_for_a_vacancy(
    id BIGSERIAL PRIMARY KEY,
    vacancy_id int REFERENCES public.vacancy(id),
    soft_requirement_id int REFERENCES public.soft_requirements(id)
);
CREATE TABLE technologies_and_tools_for_a_vacancy(
    id BIGSERIAL PRIMARY KEY,
    vacancy_id int REFERENCES public.vacancy(id),
    technologies_and_tools_id int REFERENCES public.technologies_and_tools(id)
);
--

-- Наполенение справочников стандартынми данными
INSERT INTO public.question_types (id, title, description) VALUES (1, 'Одиночный', 'Выбор одного варианта ответа');
INSERT INTO public.question_types (id, title, description) VALUES (2, 'Множественный', 'Выбор нескольких вариантов ответа');
INSERT INTO public.question_types (id, title, description) VALUES (3, 'Свободная форма', 'Вопрос со свободным ответом');

INSERT INTO public.statuses_vacancy (id, title) VALUES (1,'Согласование на вакансию');
INSERT INTO public.statuses_vacancy (id, title) VALUES (2,'Согласование');
INSERT INTO public.statuses_vacancy (id, title) VALUES (3,'Публикация');
INSERT INTO public.statuses_vacancy (id, title) VALUES (4,'Приостоновлено');
--



DELETE FROM skills_for_a_vacancy;
DELETE FROM type_employment_for_a_vacancy;
DELETE FROM working_condition_for_a_vacancy;
DELETE FROM job_responsibilities_for_a_vacancy;
DELETE FROM special_advantage_for_a_vacancy;
DELETE FROM vacancy;
DELETE FROM specializations;
DELETE FROM professional_area;
DELETE FROM grade;
DELETE FROM skills;
DELETE FROM work_address;
DELETE FROM type_employment;
DELETE FROM working_conditions;
DELETE FROM job_responsibilities;
DELETE FROM special_advantages;