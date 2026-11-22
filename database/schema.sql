PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL COLLATE NOCASE UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE courses (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);

CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(id),
    title TEXT NOT NULL
);

CREATE TABLE lessons (
    id INTEGER PRIMARY KEY,
    chapter_id INTEGER NOT NULL REFERENCES chapters(id),
    title TEXT NOT NULL,
    video_url TEXT
);

INSERT INTO courses (id, title)
VALUES (1, 'Introduction to Programming');

INSERT INTO chapters (id, course_id, title)
VALUES (1, 1, 'Python Basics');

INSERT INTO lessons (id, chapter_id, title)
VALUES (1, 1, 'Variables in Python');

COMMIT;
