# Impara Tutor API Documentation

Base URL: `http://localhost:7000`

---

## Table of Contents

- [OpenAI Endpoints](#openai-endpoints)
- [Translation Endpoints](#translation-endpoints)
- [User Endpoints](#user-endpoints)
- [Language Endpoints](#language-endpoints)
- [Course Endpoints](#course-endpoints)
- [Lesson Endpoints](#lesson-endpoints)
- [Dictionary Entry Endpoints](#dictionary-entry-endpoints)
- [Dictionary Sense Endpoints](#dictionary-sense-endpoints)
- [Dictionary Translation Endpoints](#dictionary-translation-endpoints)
- [Dictionary Example Endpoints](#dictionary-example-endpoints)
- [User Sense State Endpoints](#user-sense-state-endpoints)

---

## OpenAI Endpoints

### Get OpenAI Models

```http
GET /openAiModels
```

Returns a list of available OpenAI models.

**Response:**
```json
["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
```

---

### OpenAI Interpretation

```http
POST /openAi
Content-Type: application/json
```

**Request Body:**
```json
{
  "model": "gpt-4o-mini",
  "system": "You are a helpful assistant.",
  "prompt": "Hello, how are you?"
}
```

**Response:**
```json
{
  "id": "chatcmpl-xxx",
  "model": "gpt-4o-mini",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  },
  "message": "I'm doing well, thank you!"
}
```

---

### OpenAI Respond

```http
POST /api/openai/respond
Content-Type: application/json
```

**Request Body:**
```json
{
  "model": "gpt-4o-mini",
  "system": "You are a helpful assistant.",
  "prompt": "Explain quantum computing"
}
```

**Response:**
```json
{
  "raw": "Quantum computing is a type of computing that uses quantum mechanics..."
}
```

---

## Translation Endpoints

### Translate Text

```http
POST /api/translate
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "Hello, world!",
  "to": "de",
  "from": "en"
}
```

| Parameter | Type   | Required | Description                    |
|-----------|--------|----------|--------------------------------|
| text      | string | Yes      | Text to translate              |
| to        | string | Yes      | Target language code           |
| from      | string | No       | Source language code (default: auto-detect) |

**Response:**
```json
{
  "translated_text": "Hallo, Welt!",
  "source_language": "en",
  "target_language": "de"
}
```

---

## User Endpoints

### List All Users

```http
GET /api/user
```

**Response:**
```json
[
  {
    "id": 1,
    "display_name": "John Doe",
    "email": "john@example.com",
    "bio": "Language learner",
    "avatar_path": "/avatars/john.png",
    "created_at": "2024-01-15T10:30:00",
    "last_active_at": "2024-03-04T08:00:00"
  }
]
```

---

### Get User by ID

```http
GET /api/user/{user_id}
```

**Response:**
```json
{
  "id": 1,
  "display_name": "John Doe",
  "email": "john@example.com",
  "bio": "Language learner",
  "avatar_path": "/avatars/john.png",
  "created_at": "2024-01-15T10:30:00",
  "last_active_at": "2024-03-04T08:00:00"
}
```

---

### Create User

```http
POST /api/user
Content-Type: application/json
```

**Request Body:**
```json
{
  "display_name": "Jane Smith",
  "email": "jane@example.com",
  "bio": "Polyglot",
  "avatar_path": "/avatars/jane.png",
  "created_at": "2024-03-04T12:00:00",
  "last_active_at": null
}
```

| Field          | Type   | Required | Description              |
|----------------|--------|----------|--------------------------|
| display_name   | string | Yes      | User's display name      |
| email          | string | No       | User's email address     |
| bio            | string | No       | User's biography         |
| avatar_path    | string | No       | Path to avatar image     |
| created_at     | string | Yes      | ISO 8601 timestamp       |
| last_active_at | string | No       | ISO 8601 timestamp       |

**Response:** Returns the created user object.

---

### Update User

```http
PUT /api/user
Content-Type: application/json
```

**Request Body:**
```json
{
  "id": 1,
  "display_name": "John Updated",
  "email": "john.updated@example.com",
  "bio": "Updated bio",
  "avatar_path": "/avatars/john-new.png",
  "created_at": "2024-01-15T10:30:00",
  "last_active_at": "2024-03-04T14:00:00"
}
```

**Response:** Returns the updated user object.

---

### Delete User

```http
DELETE /api/user/{user_id}
```

**Response:**
```json
{
  "message": "User with id 1 deleted"
}
```

---

## Language Endpoints

### List All Available Languages

```http
GET /api/languages
```

**Response:**
```json
[
  {"code": "en", "name": "English"},
  {"code": "de", "name": "German"},
  {"code": "ru", "name": "Russian"}
]
```

---

### List User Languages

```http
GET /api/language/{user_id}
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "source_language": "en",
    "target_language": "de",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

---

### Add Language for User

```http
POST /api/language
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": 1,
  "source_language": "en",
  "target_language": "de",
  "created_at": "2024-03-04T12:00:00"
}
```

| Field           | Type   | Required | Description                 |
|-----------------|--------|----------|-----------------------------|
| user_id         | int    | Yes      | ID of the user              |
| source_language | string | Yes      | Source language code        |
| target_language | string | Yes      | Target language code        |
| created_at      | string | Yes      | ISO 8601 timestamp          |

**Response:** Returns the list of user languages.

---

## Course Endpoints

### List All Courses

```http
GET /api/courses
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "target_language": "de",
    "title": "German Basics",
    "description": "Learn German from scratch",
    "source_link": "https://example.com",
    "tags": "beginner,grammar,vocabulary",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

---

### List Courses by User

```http
GET /api/courses/user/{user_id}
```

---

### List Courses by Target Language

```http
GET /api/courses/target-language/{target_language}
```

---

### Get Course by ID

```http
GET /api/course/{course_id}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "target_language": "de",
  "title": "German Basics",
  "description": "Learn German from scratch",
  "source_link": "https://example.com",
  "tags": "beginner,grammar,vocabulary",
  "created_at": "2024-01-15T10:30:00"
}
```

---

### Create Course

```http
POST /api/course
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": 1,
  "target_language": "de",
  "title": "German Basics",
  "description": "Learn German from scratch",
  "source_link": "https://example.com",
  "tags": "beginner,grammar,vocabulary",
  "created_at": "2024-03-04T12:00:00"
}
```

| Field           | Type   | Required | Description                    |
|-----------------|--------|----------|--------------------------------|
| user_id         | int    | Yes      | ID of the user                 |
| target_language | string | Yes      | Target language code           |
| title           | string | Yes      | Course title                   |
| description     | string | No       | Course description             |
| source_link     | string | No       | Link to source material        |
| tags            | string | No       | Comma-separated tags           |
| created_at      | string | Yes      | ISO 8601 timestamp             |

**Response:** Returns the created course object.

---

### Update Course

```http
PUT /api/course/{course_id}
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "German Basics Updated",
  "description": "Updated description"
}
```

**Response:** Returns the updated course object.

---

### Delete Course

```http
DELETE /api/course/{course_id}
```

**Response:**
```json
{
  "message": "Course with id 1 deleted"
}
```

---

## Lesson Endpoints

### List All Lessons

```http
GET /api/lessons
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "course_id": 1,
    "parent_lesson_id": null,
    "title": "Introduction",
    "description": "Welcome to the course",
    "text": "Lesson content here...",
    "source_link": "https://example.com",
    "tags": "intro,basics",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

---

### List Lessons by User

```http
GET /api/lessons/user/{user_id}
```

---

### List Lessons by Course

```http
GET /api/lessons/course/{course_id}
```

---

### List Top-Level Lessons (No Parent)

```http
GET /api/lessons/top-level/course/{course_id}
```

---

### Get Lesson by ID

```http
GET /api/lesson/{lesson_id}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "course_id": 1,
  "parent_lesson_id": null,
  "title": "Introduction",
  "description": "Welcome to the course",
  "text": "Lesson content here...",
  "source_link": "https://example.com",
  "tags": "intro,basics",
  "created_at": "2024-01-15T10:30:00"
}
```

---

### Create Lesson

```http
POST /api/lesson
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": 1,
  "course_id": 1,
  "parent_lesson_id": null,
  "title": "Introduction",
  "description": "Welcome to the course",
  "text": "Lesson content here...",
  "source_link": "https://example.com",
  "tags": "intro,basics",
  "created_at": "2024-03-04T12:00:00"
}
```

| Field           | Type    | Required | Description                    |
|-----------------|---------|----------|--------------------------------|
| user_id         | int     | Yes      | ID of the user                 |
| course_id       | int     | Yes      | ID of the parent course        |
| parent_lesson_id| int?    | No       | ID of parent lesson (for sub-lessons) |
| title           | string  | Yes      | Lesson title                   |
| description     | string  | No       | Lesson description             |
| text            | string  | No       | Lesson content/text            |
| source_link     | string  | No       | Link to source material        |
| tags            | string  | No       | Comma-separated tags           |
| created_at      | string  | Yes      | ISO 8601 timestamp             |

**Response:** Returns the created lesson object.

---

### Update Lesson

```http
PUT /api/lesson/{lesson_id}
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Updated Introduction",
  "text": "Updated content"
}
```

**Response:** Returns the updated lesson object.

---

### Delete Lesson

```http
DELETE /api/lesson/{lesson_id}
```

**Response:**
```json
{
  "message": "Lesson with id 1 deleted"
}
```

---

## Dictionary Entry Endpoints

### List All Dictionary Entries

```http
GET /api/dict-entries
```

**Response:**
```json
[
  {
    "id": 1,
    "language": "ru",
    "lemma": "привет",
    "normalized": "привет",
    "ipa": "prʲɪˈvʲet",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

---

### List Dictionary Entries by Language

```http
GET /api/dict-entries/language/{language}
```

---

### Get Dictionary Entry by Lemma

```http
GET /api/dict-entry/lemma/{language}/{lemma}
```

**Response:**
```json
{
  "id": 1,
  "language": "ru",
  "lemma": "привет",
  "normalized": "привет",
  "ipa": "prʲɪˈvʲet",
  "created_at": "2024-01-15T10:30:00"
}
```

---

### Get Dictionary Entry by ID

```http
GET /api/dict-entry/{entry_id}
```

---

### Create Dictionary Entry

```http
POST /api/dict-entry
Content-Type: application/json
```

**Request Body:**
```json
{
  "language": "ru",
  "lemma": "привет",
  "normalized": "привет",
  "ipa": "prʲɪˈvʲet",
  "created_at": "2024-03-04T12:00:00"
}
```

| Field       | Type   | Required | Description              |
|-------------|--------|----------|--------------------------|
| language    | string | Yes      | Language code            |
| lemma       | string | Yes      | Word/lemma form          |
| normalized  | string | No       | Normalized form          |
| ipa         | string | No       | IPA pronunciation        |
| created_at  | string | Yes      | ISO 8601 timestamp       |

**Response:** Returns the created dictionary entry object.

---

### Update Dictionary Entry

```http
PUT /api/dict-entry/{entry_id}
Content-Type: application/json
```

**Request Body:**
```json
{
  "normalized": "updated normalized",
  "ipa": "updated ipa"
}
```

**Response:** Returns the updated dictionary entry object.

---

### Delete Dictionary Entry

```http
DELETE /api/dict-entry/{entry_id}
```

**Response:**
```json
{
  "message": "DictEntry with id 1 deleted"
}
```

---

## Dictionary Sense Endpoints

### List All Dictionary Senses

```http
GET /api/dict-senses
```

**Response:**
```json
[
  {
    "id": 1,
    "entry_id": 1,
    "pos": "noun",
    "gloss": "a greeting",
    "note": "informal",
    "sense_order": 1
  }
]
```

---

### List Dictionary Senses by Entry

```http
GET /api/dict-senses/entry/{entry_id}
```

---

### Get Dictionary Sense by ID

```http
GET /api/dict-sense/{sense_id}
```

**Response:**
```json
{
  "id": 1,
  "entry_id": 1,
  "pos": "noun",
  "gloss": "a greeting",
  "note": "informal",
  "sense_order": 1
}
```

---

### Create Dictionary Sense

```http
POST /api/dict-sense
Content-Type: application/json
```

**Request Body:**
```json
{
  "entry_id": 1,
  "pos": "noun",
  "gloss": "a greeting",
  "note": "informal",
  "sense_order": 1
}
```

| Field       | Type   | Required | Description                    |
|-------------|--------|----------|--------------------------------|
| entry_id    | int    | Yes      | ID of the dictionary entry     |
| pos         | string | No       | Part of speech                 |
| gloss       | string | No       | Definition/gloss               |
| note        | string | No       | Additional notes               |
| sense_order | int    | No       | Order of sense within entry    |

**Response:** Returns the created dictionary sense object.

---

### Update Dictionary Sense

```http
PUT /api/dict-sense/{sense_id}
Content-Type: application/json
```

**Request Body:**
```json
{
  "gloss": "updated gloss",
  "note": "updated note"
}
```

**Response:** Returns the updated dictionary sense object.

---

### Delete Dictionary Sense

```http
DELETE /api/dict-sense/{sense_id}
```

**Response:**
```json
{
  "message": "DictSense with id 1 deleted"
}
```

---

## Dictionary Translation Endpoints

### List All Dictionary Translations

```http
GET /api/dict-translations
```

**Response:**
```json
[
  {
    "id": 1,
    "sense_id": 1,
    "target_language": "en",
    "translation": "hello",
    "note": "common greeting"
  }
]
```

---

### List Dictionary Translations by Sense

```http
GET /api/dict-translations/sense/{sense_id}
```

---

### List Dictionary Translations by Language

```http
GET /api/dict-translations/language/{target_language}
```

---

### Get Dictionary Translation by ID

```http
GET /api/dict-translation/{translation_id}
```

**Response:**
```json
{
  "id": 1,
  "sense_id": 1,
  "target_language": "en",
  "translation": "hello",
  "note": "common greeting"
}
```

---

### Create Dictionary Translation

```http
POST /api/dict-translation
Content-Type: application/json
```

**Request Body:**
```json
{
  "sense_id": 1,
  "target_language": "en",
  "translation": "hello",
  "note": "common greeting"
}
```

| Field           | Type   | Required | Description                    |
|-----------------|--------|----------|--------------------------------|
| sense_id        | int    | Yes      | ID of the dictionary sense     |
| target_language | string | Yes      | Target language code           |
| translation     | string | Yes      | Translation text               |
| note            | string | No       | Additional notes               |

**Response:** Returns the created dictionary translation object.

---

### Update Dictionary Translation

```http
PUT /api/dict-translation/{translation_id}
Content-Type: application/json
```

**Request Body:**
```json
{
  "translation": "hi",
  "note": "updated note"
}
```

**Response:** Returns the updated dictionary translation object.

---

### Delete Dictionary Translation

```http
DELETE /api/dict-translation/{translation_id}
```

**Response:**
```json
{
  "message": "DictTranslation with id 1 deleted"
}
```

---

## Dictionary Example Endpoints

### List All Dictionary Examples

```http
GET /api/dict-examples
```

**Response:**
```json
[
  {
    "id": 1,
    "sense_id": 1,
    "example": "Привет, как дела?",
    "translation": "Hello, how are you?",
    "source": "Common usage"
  }
]
```

---

### List Dictionary Examples by Sense

```http
GET /api/dict-examples/sense/{sense_id}
```

---

### Get Dictionary Example by ID

```http
GET /api/dict-example/{example_id}
```

**Response:**
```json
{
  "id": 1,
  "sense_id": 1,
  "example": "Привет, как дела?",
  "translation": "Hello, how are you?",
  "source": "Common usage"
}
```

---

### Create Dictionary Example

```http
POST /api/dict-example
Content-Type: application/json
```

**Request Body:**
```json
{
  "sense_id": 1,
  "example": "Привет, как дела?",
  "translation": "Hello, how are you?",
  "source": "Common usage"
}
```

| Field       | Type   | Required | Description                    |
|-------------|--------|----------|--------------------------------|
| sense_id    | int    | Yes      | ID of the dictionary sense     |
| example     | string | Yes      | Example sentence               |
| translation | string | No       | Translation of example         |
| source      | string | No       | Source of the example          |

**Response:** Returns the created dictionary example object.

---

### Update Dictionary Example

```http
PUT /api/dict-example/{example_id}
Content-Type: application/json
```

**Request Body:**
```json
{
  "translation": "Hi, how's it going?",
  "source": "Updated source"
}
```

**Response:** Returns the updated dictionary example object.

---

### Delete Dictionary Example

```http
DELETE /api/dict-example/{example_id}
```

**Response:**
```json
{
  "message": "DictExample with id 1 deleted"
}
```

---

## User Sense State Endpoints

### List User Sense States by User

```http
GET /api/user-sense-states/user/{user_id}
```

**Response:**
```json
[
  {
    "user_id": 1,
    "sense_id": 1,
    "srs_level": 3,
    "last_seen_at": "2024-03-01T10:00:00",
    "next_due_at": "2024-03-10T10:00:00"
  }
]
```

---

### List User Sense States by Sense

```http
GET /api/user-sense-states/sense/{sense_id}
```

---

### Get User Sense State

```http
GET /api/user-sense-state/{user_id}/{sense_id}
```

**Response:**
```json
{
  "user_id": 1,
  "sense_id": 1,
  "srs_level": 3,
  "last_seen_at": "2024-03-01T10:00:00",
  "next_due_at": "2024-03-10T10:00:00"
}
```

---

### Create User Sense State

```http
POST /api/user-sense-state
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": 1,
  "sense_id": 1,
  "srs_level": 0,
  "last_seen_at": "2024-03-04T12:00:00",
  "next_due_at": "2024-03-05T12:00:00"
}
```

| Field        | Type   | Required | Description                    |
|--------------|--------|----------|--------------------------------|
| user_id      | int    | Yes      | ID of the user                 |
| sense_id     | int    | Yes      | ID of the dictionary sense     |
| srs_level    | int    | Yes      | SRS (Spaced Repetition) level  |
| last_seen_at | string | No       | ISO 8601 timestamp             |
| next_due_at  | string | No       | ISO 8601 timestamp             |

**Response:** Returns the created user sense state object.

---

### Update User Sense State

```http
PUT /api/user-sense-state/{user_id}/{sense_id}
Content-Type: application/json
```

**Request Body:**
```json
{
  "srs_level": 4,
  "last_seen_at": "2024-03-04T14:00:00",
  "next_due_at": "2024-03-15T14:00:00"
}
```

**Response:** Returns the updated user sense state object.

---

### Delete User Sense State

```http
DELETE /api/user-sense-state/{user_id}/{sense_id}
```

**Response:**
```json
{
  "message": "UserSenseState deleted for user 1 and sense 1"
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error message details"
}
```

---

## Notes

- All timestamps should be in ISO 8601 format (e.g., `2024-03-04T12:00:00`)
- Language codes follow the ISO 639-1 standard (e.g., `en`, `de`, `ru`)
- The `UserSenseState` uses a composite primary key (`user_id`, `sense_id`)
