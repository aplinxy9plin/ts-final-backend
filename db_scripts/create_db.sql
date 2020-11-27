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