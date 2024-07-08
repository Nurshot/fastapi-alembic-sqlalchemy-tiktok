A backend written for my mobile application to fetch TikTok profiles. It finds the profiles, downloads their pictures, usernames, and descriptions, and writes them to a database.


It was created using FastAPI and PostgreSQL. On the ORM side, SQLAlchemy was used, but since it is an older project, the SQL part does not work asynchronously.
