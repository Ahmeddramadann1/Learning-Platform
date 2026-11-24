PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL COLLATE NOCASE UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    video_url TEXT ,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id)
);

BEGIN;

INSERT INTO courses (title)
SELECT 'Introduction to Programming'
WHERE NOT EXISTS (
    SELECT 1 FROM courses WHERE title = 'Introduction to Programming'
);

INSERT INTO chapters (course_id, title)
SELECT courses.id, 'Python Basics'
FROM courses
WHERE courses.title = 'Introduction to Programming'
  AND NOT EXISTS (
      SELECT 1 FROM chapters
      WHERE course_id = courses.id AND title = 'Python Basics'
  );

INSERT INTO lessons (chapter_id, title, video_url)
SELECT chapters.id, 'Variables in Python', '/videos/python-variables.mp4'
FROM chapters
JOIN courses ON courses.id = chapters.course_id
WHERE courses.title = 'Introduction to Programming'
  AND chapters.title = 'Python Basics'
  AND NOT EXISTS (
      SELECT 1 FROM lessons
      WHERE chapter_id = chapters.id AND title = 'Variables in Python'
  );

UPDATE lessons
SET video_url = '/videos/python-variables.mp4'
WHERE title = 'Variables in Python'
  AND (video_url IS NULL OR video_url = '')
  AND chapter_id IN (
      SELECT chapters.id
      FROM chapters
      JOIN courses ON courses.id = chapters.course_id
      WHERE courses.title = 'Introduction to Programming'
        AND chapters.title = 'Python Basics'
  );
COMMIT;