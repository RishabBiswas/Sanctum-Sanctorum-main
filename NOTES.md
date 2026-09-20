# Sanctum Sanctorum — Implementation Notes

Live application: https://sanctum-sanctorum-main-o2a0.onrender.com
API docs: https://sanctum-sanctorum-main-o2a0.onrender.com/docs

## Implementation

Implemented:

- Book catalogue CRUD
- ISBN-13 normalization and checksum validation
- Book search, filtering, sorting and pagination
- Member creation and member operations
- Member statistics
- Order creation and stock reservation
- Tier-based discounts
- Order payment and cancellation
- Loan borrowing and returns
- Loan limits and restricted-book access
- Overdue status and late fees
- Top-books reporting
- FastAPI application wiring
- PostgreSQL deployment


## Architecture

The application follows a layered FastAPI architecture:

- Routers handle HTTP requests and responses.
- Services contain business logic.
- SQLAlchemy models represent database entities.
- Pydantic schemas handle request/response validation.
- SQLite is used by default for local development and tests.
- PostgreSQL is used in the deployed environment.

The deployed application runs FastAPI on Render and uses Supabase PostgreSQL through SQLAlchemy and psycopg.


## Deployment

The application is deployed as a Render Web Service.

Database:
- Supabase PostgreSQL
- Session Pooler connection

The database URL is provided through the `SANCTUM_DATABASE_URL`
environment variable and is not committed to the repository.

The application creates the database tables during startup and
seeds the database when it is empty.



## Trade-offs

- SQLite remains the default local database so the test suite can run
  without external services.
- PostgreSQL is used for the deployed environment because deployed
  application instances should not rely on local SQLite persistence.
- Database tables are created with SQLAlchemy `create_all()` during
  application startup rather than using a migration framework. This
  keeps the take-home implementation simple, but a production system
  would normally use migrations.
- The Render free instance may spin down after inactivity, so the first
  request after a period of inactivity can be slower.


## AI Usage

AI assistance was used during implementation for:
- Understanding the starter code and assignment requirements.
- Debugging implementation issues.
- Discussing SQLAlchemy/FastAPI design decisions.
- Generating implementation suggestions that were then tested locally.

All suggested changes were reviewed and verified using the project's
test suite.

### Example where AI was incorrect

During member implementation, an AI-generated validator suggestion was
placed at the wrong indentation level, so it was not actually part of
the `MemberCreate` model. I detected this by directly constructing a
`MemberCreate` instance and checking whether the email was normalized.
I corrected the indentation and reran the relevant tests.

I also verified the application independently rather than assuming
that AI-generated code was correct.