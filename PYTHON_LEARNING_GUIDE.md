# Python Learning App - Topics, Levels, Exercises & Quizzes Guide

## Overview

Your Python learning application now includes a comprehensive curriculum with:
- **4 Skill Levels**: Beginner, Intermediate, Advanced, Expert
- **20+ Python Topics**: From basics to advanced concepts
- **15+ Exercises**: Progressive difficulty levels with solutions
- **2 Quizzes**: Beginner-level Python knowledge assessments

## Database Structure

### New Models Added

#### 1. **Level Model** (`levels` table)
```python
- id: Primary key
- name: Level name (Beginner, Intermediate, Advanced, Expert)
- description: Level description
- order: Display order
```

#### 2. **Topic Model** (`topics` table)
```python
- id: Primary key
- name: Topic name
- description: Topic description
- level_id: Foreign key to Level
- order: Display order
- learning_objectives: JSON array of learning goals
- resources: JSON array of resource links
```

#### 3. **Quiz Model** (`quizzes` table)
```python
- id: Primary key
- title: Quiz title
- description: Quiz description
- topic_id: Foreign key to Topic
- level_id: Foreign key to Level
- passing_score: Required percentage (default: 70)
- time_limit_minutes: Time limit for quiz
- shuffle_questions: Randomize question order
```

#### 4. **QuizQuestion Model** (`quiz_questions` table)
```python
- id: Primary key
- quiz_id: Foreign key to Quiz
- question_text: Question content
- question_type: multiple_choice, true_false, short_answer, code
- options: JSON array of options
- correct_answer: Correct answer (JSON for flexibility)
- explanation: Answer explanation
- points: Points for this question
```

#### 5. **QuizSubmission Model** (`quiz_submissions` table)
```python
- id: Primary key
- student_id: Foreign key to Student
- quiz_id: Foreign key to Quiz
- started_at: When quiz started
- completed_at: When quiz completed
- score: Final score (0-100)
- passed: Whether passing score achieved
```

#### 6. **QuizAnswer Model** (`quiz_answers` table)
```python
- id: Primary key
- submission_id: Foreign key to QuizSubmission
- question_id: Foreign key to QuizQuestion
- answer_text: Student's answer (JSON)
- is_correct: Whether answer is correct
- points_earned: Points earned for this answer
```

## Available Topics

### Beginner Level (10 topics)
1. Introduction to Python
2. Variables and Data Types
3. Operators and Expressions
4. Control Flow - If Statements
5. Loops - For and While
6. Lists and Indexing
7. Functions Basics
8. Strings and Text Processing
9. Dictionaries and Tuples
10. Input and Output

### Intermediate Level (7 topics)
11. List Comprehensions
12. File Handling
13. Exception Handling
14. Object-Oriented Programming Basics
15. Inheritance and Polymorphism
16. Working with Modules and Packages
17. Lambda Functions and Map/Filter

### Advanced Level (3 topics)
18. Decorators
19. Generators and Iterators
20. Regular Expressions

## API Endpoints

### Topics Management

**Get all levels:**
```
GET /api/topics/levels
```

**Create a new level:**
```
POST /api/topics/levels
Content-Type: application/json

{
  "name": "Expert",
  "description": "Become a Python expert",
  "order": 4
}
```

**Get all topics:**
```
GET /api/topics/?level_id=1&skip=0&limit=100
```

**Create a topic:**
```
POST /api/topics/
Content-Type: application/json

{
  "name": "Introduction to Python",
  "description": "Learn Python basics",
  "level_id": 1,
  "order": 1,
  "learning_objectives": [
    "Understand Python fundamentals",
    "Set up development environment"
  ],
  "resources": [
    {
      "title": "Python Documentation",
      "url": "https://docs.python.org/3/"
    }
  ]
}
```

**Get a specific topic:**
```
GET /api/topics/{topic_id}
```

**Update a topic:**
```
PUT /api/topics/{topic_id}
Content-Type: application/json

{
  "name": "Updated Topic Name",
  "order": 2
}
```

**Delete a topic:**
```
DELETE /api/topics/{topic_id}
```

### Quizzes Management

**Get all quizzes:**
```
GET /api/quizzes/?topic_id=1&level_id=1&skip=0&limit=100
```

**Create a quiz with questions:**
```
POST /api/quizzes/
Content-Type: application/json

{
  "title": "Python Basics Quiz",
  "description": "Test your Python fundamentals",
  "topic_id": 1,
  "level_id": 1,
  "passing_score": 70,
  "time_limit_minutes": 15,
  "shuffle_questions": true,
  "questions": [
    {
      "question_text": "What is the output of print(5 + 3)?",
      "question_type": "multiple_choice",
      "options": ["8", "5", "3", "Error"],
      "correct_answer": "8",
      "explanation": "5 + 3 = 8",
      "points": 1
    }
  ]
}
```

**Get a specific quiz:**
```
GET /api/quizzes/{quiz_id}
```

**Update a quiz:**
```
PUT /api/quizzes/{quiz_id}
Content-Type: application/json

{
  "title": "Updated Quiz Title",
  "passing_score": 75
}
```

**Start a quiz (create submission):**
```
POST /api/quizzes/{quiz_id}/start?student_id=1
```

**Submit an answer:**
```
POST /api/quizzes/{quiz_id}/submissions/{submission_id}/answer
Content-Type: application/json

{
  "question_id": 1,
  "answer_text": "8"
}
```

**Complete a quiz:**
```
POST /api/quizzes/{quiz_id}/submissions/{submission_id}/complete
```

**Get a submission:**
```
GET /api/quizzes/{quiz_id}/submissions/{submission_id}
```

**Delete a quiz:**
```
DELETE /api/quizzes/{quiz_id}
```

## Seeding Data

To populate the database with all Python topics, exercises, and quizzes:

```bash
# From the backend directory
python seed_python_content.py
```

This will create:
- 4 skill levels
- 20 Python topics with learning objectives and resources
- 15+ exercises with solutions and test cases
- 2 comprehensive quizzes

## Exercises

Each exercise includes:
- **Title**: Exercise name
- **Description**: What students need to do
- **Difficulty Level**: easy, medium, hard
- **Starter Code**: Template to get started
- **Expected Output**: What the output should be
- **Test Cases**: Automated testing
- **Hints**: Help for students
- **Solution Code**: Complete solution

### Exercise Difficulty Levels
- **Easy**: Basic concepts, straightforward problems
- **Medium**: Intermediate concepts, requires more thinking
- **Hard**: Advanced concepts, complex problems

## Quiz Features

### Question Types
1. **Multiple Choice**: Select one correct answer from options
2. **True/False**: Binary answer type
3. **Short Answer**: Text answer (case-insensitive comparison)
4. **Code**: Write code to solve a problem (future enhancement)

### Quiz Scoring
- Each question has points
- Correct answers earn points
- Final score = (total points earned / max points) × 100
- Passing score is customizable (default: 70%)

### Quiz Features
- Time limit support
- Question shuffling for randomization
- Multiple attempts tracking
- Detailed feedback with explanations

## Integration with Frontend

### Display Topics by Level
```javascript
GET /api/topics/?level_id=1
```

### Display Exercises
```javascript
GET /api/exercises/?topic=Introduction%20to%20Python&difficulty=easy
```

### Quiz Flow
1. Get available quizzes: `GET /api/quizzes/?topic_id=1`
2. Start quiz: `POST /api/quizzes/1/start?student_id=1`
3. Display questions from quiz (include in response)
4. Submit each answer: `POST /api/quizzes/1/submissions/1/answer`
5. Complete quiz: `POST /api/quizzes/1/submissions/1/complete`
6. Get results: `GET /api/quizzes/1/submissions/1`

## Progress Tracking

The system tracks:
- Student progress on each exercise
- Quiz submissions and scores
- Best scores achieved
- Completion status

## Next Steps

1. **Update Frontend**: Create UI components for topics, exercises, and quizzes
2. **Add More Content**: Expand topics and exercises
3. **Advanced Question Types**: Implement code execution for code questions
4. **Adaptive Learning**: Recommend content based on performance
5. **Analytics**: Track learning patterns and progress

## File References

- Models: [backend/app/models/models.py](backend/app/models/models.py)
- Schemas: [backend/app/schemas/schemas.py](backend/app/schemas/schemas.py)
- Topics Routes: [backend/app/routes/topics.py](backend/app/routes/topics.py)
- Quizzes Routes: [backend/app/routes/quizzes.py](backend/app/routes/quizzes.py)
- Main App: [backend/main.py](backend/main.py)
- Seed Script: [backend/seed_python_content.py](backend/seed_python_content.py)
