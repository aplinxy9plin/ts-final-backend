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
CREATE TABLE statuses_candidate(
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
    status_id int REFERENCES public.statuses_vacancy(id),
    is_testing boolean
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

CREATE TABLE candidates(
    id BIGSERIAL PRIMARY KEY,
    firstname text,
    lastname text,
    number_phone text,
    link_social_network text,
    resume text,
    status_id int REFERENCES public.statuses_candidate(id) DEFAULT 1,
    vacancy_id int REFERENCES public.vacancy(id)
);

CREATE TABLE answer_on_question_candidate(
    id BIGSERIAL PRIMARY KEY,
    candidate_id int REFERENCES public.candidates(id) ON DELETE CASCADE,
    question_id bigint REFERENCES public.questons(id),
    answer_id bigint REFERENCES public.answers_on_question(id),
    result boolean
);
-- Отношения полей
CREATE TABLE skills_for_a_vacancy(
    id BIGSERIAL PRIMARY KEY,
    vacancy_id int REFERENCES public.vacancy(id) ON DELETE CASCADE,
    skill_id int REFERENCES public.skills(id)
);
CREATE TABLE type_employment_for_a_vacancy(
    id BIGSERIAL PRIMARY KEY,
    vacancy_id int REFERENCES public.vacancy(id) ON DELETE CASCADE,
    type_employment_id int REFERENCES public.type_employment(id)
);
CREATE TABLE working_condition_for_a_vacancy(
    id BIGSERIAL PRIMARY KEY,
    vacancy_id int REFERENCES public.vacancy(id) ON DELETE CASCADE,
    working_condition_id int REFERENCES public.working_conditions(id)
);
CREATE TABLE job_responsibilities_for_a_vacancy(
    id BIGSERIAL PRIMARY KEY,
    vacancy_id int REFERENCES public.vacancy(id) ON DELETE CASCADE,
    job_responsibilities_id int REFERENCES public.job_responsibilities(id)
);
CREATE TABLE special_advantage_for_a_vacancy(
    id BIGSERIAL PRIMARY KEY,
    vacancy_id int REFERENCES public.vacancy(id) ON DELETE CASCADE,
    special_advantage_id int REFERENCES public.special_advantages(id)
);
CREATE TABLE soft_requirement_for_a_vacancy(
    id BIGSERIAL PRIMARY KEY,
    vacancy_id int REFERENCES public.vacancy(id) ON DELETE CASCADE,
    soft_requirement_id int REFERENCES public.soft_requirements(id)
);
CREATE TABLE technologies_and_tools_for_a_vacancy(
    id BIGSERIAL PRIMARY KEY,
    vacancy_id int REFERENCES public.vacancy(id) ON DELETE CASCADE,
    technologies_and_tools_id int REFERENCES public.technologies_and_tools(id)
);
CREATE TABLE skills_for_a_candidate(
    id BIGSERIAL PRIMARY KEY,
    candidate_id int REFERENCES public.candidates(id) ON DELETE CASCADE,
    skill_id int REFERENCES public.skills(id)
);
CREATE TABLE technologies_and_tools_for_a_candidate(
    id BIGSERIAL PRIMARY KEY,
    candidate_id int REFERENCES public.candidates(id) ON DELETE CASCADE,
    technologies_and_tools_id int REFERENCES public.technologies_and_tools(id)
);
--

-- Наполенение справочников стандартынми данными
INSERT INTO public.question_types (id, title, description) VALUES (1, 'One', 'Выбор одного варианта ответа');
INSERT INTO public.question_types (id, title, description) VALUES (2, 'Multi', 'Выбор нескольких вариантов ответа');
INSERT INTO public.question_types (id, title, description) VALUES (3, 'Free form', 'Вопрос со свободным ответом');

INSERT INTO public.statuses_vacancy (id, title) VALUES (1,'Согласование на вакансию');
INSERT INTO public.statuses_vacancy (id, title) VALUES (2,'Публикация');
INSERT INTO public.statuses_vacancy (id, title) VALUES (3,'Приостоновлено');

INSERT INTO public.statuses_candidate (id, title) VALUES (1,'Анализ кандидата');
INSERT INTO public.statuses_candidate (id, title) VALUES (2,'Приглашён на собеседование');
INSERT INTO public.statuses_candidate (id, title) VALUES (3,'Выдан оффер');
INSERT INTO public.statuses_candidate (id, title) VALUES (4,'Подготовка к выходу на работу');
INSERT INTO public.statuses_candidate (id, title) VALUES (5,'Окончание испытательного срока');
INSERT INTO public.statuses_candidate (id, title) VALUES (6,'Отложено');
--


-- Функция для расчёта ценности сотрудника
CREATE OR REPLACE FUNCTION get_score_candidate(candidate_id_ bigint)
RETURNS int AS
$score$
   DECLARE
        count_true_answers smallint;
        count_adjacent_skills smallint;
        count_adjacent_technologies_and_tools smallint;
        is_resume smallint;
   BEGIN
        count_true_answers = (SELECT count(*) FROM answer_on_question_candidate WHERE candidate_id=candidate_id_ and result=true) * 5;
        count_adjacent_skills = (SELECT count(*)
                                    FROM candidates c
                                        LEFT JOIN skills_for_a_candidate sfac on c.id = sfac.candidate_id
                                        LEFT JOIN skills_for_a_vacancy sfav on c.vacancy_id = sfav.vacancy_id
                                    WHERE c.id=candidate_id_ and sfac.skill_id=sfav.skill_id) * 21;
        count_adjacent_technologies_and_tools = (SELECT count(*)
                                    FROM candidates c
                                        LEFT JOIN technologies_and_tools_for_a_candidate tatfac on c.id = tatfac.candidate_id
                                        LEFT JOIN technologies_and_tools_for_a_vacancy tatfav on c.vacancy_id = tatfav.vacancy_id
                                    WHERE c.id=candidate_id_ and tatfac.technologies_and_tools_id=tatfav.technologies_and_tools_id) * 14;
        is_resume = (SELECT count(*) FROM candidates WHERE resume is not null) * 20;
      RETURN count_true_answers + count_adjacent_skills + count_adjacent_technologies_and_tools + is_resume;
   END;
$score$
    LANGUAGE plpgsql;
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