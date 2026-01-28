"""
Seed database with Python learning content
"""

from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import SessionLocal
from app.models.models import (
    Level, Topic, Exercise, Quiz, QuizQuestion
)


def seed_levels():
    """Create skill levels"""
    db = SessionLocal()
    
    levels = [
        {
            "name": "Beginner",
            "description": "Start your Python journey with fundamentals",
            "order": 1
        },
        {
            "name": "Intermediate",
            "description": "Build more complex applications",
            "order": 2
        },
        {
            "name": "Advanced",
            "description": "Master advanced Python concepts",
            "order": 3
        },
        {
            "name": "Expert",
            "description": "Become a Python expert",
            "order": 4
        }
    ]
    
    for level_data in levels:
        existing = db.query(Level).filter(Level.name == level_data["name"]).first()
        if not existing:
            level = Level(**level_data)
            db.add(level)
    
    db.commit()
    db.close()


def seed_topics():
    """Create Python topics"""
    db = SessionLocal()
    
    beginner_level = db.query(Level).filter(Level.name == "Beginner").first()
    intermediate_level = db.query(Level).filter(Level.name == "Intermediate").first()
    advanced_level = db.query(Level).filter(Level.name == "Advanced").first()
    
    topics = [
        # Beginner Topics
        {
            "name": "Introduction to Python",
            "description": "Learn what Python is and set up your environment",
            "level_id": beginner_level.id if beginner_level else 1,
            "order": 1,
            "learning_objectives": [
                "Understand what Python is and its applications",
                "Install Python and set up IDE",
                "Write your first Python program",
                "Understand basic Python syntax"
            ],
            "resources": [
                {"title": "Python Official Documentation", "url": "https://docs.python.org/3/"},
                {"title": "Python.org Tutorial", "url": "https://python.org"}
            ]
        },
        {
            "name": "Variables and Data Types",
            "description": "Master variables, strings, numbers, and boolean types",
            "level_id": beginner_level.id if beginner_level else 1,
            "order": 2,
            "learning_objectives": [
                "Understand variables and naming conventions",
                "Work with integers, floats, and strings",
                "Use boolean values and operations",
                "Perform type conversion"
            ]
        },
        {
            "name": "Operators and Expressions",
            "description": "Learn arithmetic, comparison, logical, and assignment operators",
            "level_id": beginner_level.id if beginner_level else 1,
            "order": 3,
            "learning_objectives": [
                "Use arithmetic operators",
                "Understand comparison operators",
                "Work with logical operators",
                "Use assignment operators"
            ]
        },
        {
            "name": "Control Flow - If Statements",
            "description": "Make decisions with if, elif, and else statements",
            "level_id": beginner_level.id if beginner_level else 1,
            "order": 4,
            "learning_objectives": [
                "Write if statements",
                "Use elif for multiple conditions",
                "Implement else clauses",
                "Nest conditional statements"
            ]
        },
        {
            "name": "Loops - For and While",
            "description": "Repeat code with for and while loops",
            "level_id": beginner_level.id if beginner_level else 1,
            "order": 5,
            "learning_objectives": [
                "Create for loops with range()",
                "Iterate over lists and strings",
                "Use while loops",
                "Control loops with break and continue"
            ]
        },
        {
            "name": "Lists and Indexing",
            "description": "Work with lists and access elements by index",
            "level_id": beginner_level.id if beginner_level else 1,
            "order": 6,
            "learning_objectives": [
                "Create and initialize lists",
                "Access list elements by index",
                "Understand negative indexing",
                "Slice lists"
            ]
        },
        {
            "name": "Functions Basics",
            "description": "Create and call functions with parameters and return values",
            "level_id": beginner_level.id if beginner_level else 1,
            "order": 7,
            "learning_objectives": [
                "Define functions",
                "Use parameters and arguments",
                "Return values from functions",
                "Understand variable scope"
            ]
        },
        {
            "name": "Strings and Text Processing",
            "description": "Master string manipulation and formatting",
            "level_id": beginner_level.id if beginner_level else 1,
            "order": 8,
            "learning_objectives": [
                "Create and manipulate strings",
                "Use string methods",
                "Format strings with f-strings",
                "Work with string slicing"
            ]
        },
        {
            "name": "Dictionaries and Tuples",
            "description": "Use dictionaries for key-value pairs and tuples for immutable sequences",
            "level_id": beginner_level.id if beginner_level else 1,
            "order": 9,
            "learning_objectives": [
                "Create dictionaries",
                "Access and modify dictionary values",
                "Create tuples",
                "Understand immutability"
            ]
        },
        {
            "name": "Input and Output",
            "description": "Get user input and display output",
            "level_id": beginner_level.id if beginner_level else 1,
            "order": 10,
            "learning_objectives": [
                "Use input() function",
                "Convert input to appropriate types",
                "Format output with print()",
                "Handle input validation"
            ]
        },
        # Intermediate Topics
        {
            "name": "List Comprehensions",
            "description": "Create lists efficiently with list comprehensions",
            "level_id": intermediate_level.id if intermediate_level else 2,
            "order": 11,
            "learning_objectives": [
                "Understand list comprehension syntax",
                "Create lists with conditions",
                "Use nested list comprehensions",
                "Compare with loops for readability"
            ]
        },
        {
            "name": "File Handling",
            "description": "Read from and write to files",
            "level_id": intermediate_level.id if intermediate_level else 2,
            "order": 12,
            "learning_objectives": [
                "Open and close files",
                "Read file contents",
                "Write to files",
                "Handle file exceptions"
            ]
        },
        {
            "name": "Exception Handling",
            "description": "Handle errors gracefully with try-except blocks",
            "level_id": intermediate_level.id if intermediate_level else 2,
            "order": 13,
            "learning_objectives": [
                "Use try-except blocks",
                "Handle specific exceptions",
                "Use finally clause",
                "Raise custom exceptions"
            ]
        },
        {
            "name": "Object-Oriented Programming Basics",
            "description": "Introduction to classes and objects",
            "level_id": intermediate_level.id if intermediate_level else 2,
            "order": 14,
            "learning_objectives": [
                "Define classes",
                "Create objects",
                "Understand attributes and methods",
                "Use __init__ constructor"
            ]
        },
        {
            "name": "Inheritance and Polymorphism",
            "description": "Reuse code with inheritance and use polymorphism",
            "level_id": intermediate_level.id if intermediate_level else 2,
            "order": 15,
            "learning_objectives": [
                "Create parent and child classes",
                "Override methods",
                "Understand super()",
                "Implement polymorphism"
            ]
        },
        {
            "name": "Working with Modules and Packages",
            "description": "Organize code into modules and packages",
            "level_id": intermediate_level.id if intermediate_level else 2,
            "order": 16,
            "learning_objectives": [
                "Import modules",
                "Use standard library modules",
                "Create your own modules",
                "Understand packages"
            ]
        },
        {
            "name": "Lambda Functions and Map/Filter",
            "description": "Use anonymous functions and functional programming concepts",
            "level_id": intermediate_level.id if intermediate_level else 2,
            "order": 17,
            "learning_objectives": [
                "Write lambda functions",
                "Use map() function",
                "Use filter() function",
                "Combine with list comprehensions"
            ]
        },
        # Advanced Topics
        {
            "name": "Decorators",
            "description": "Modify functions and classes with decorators",
            "level_id": advanced_level.id if advanced_level else 3,
            "order": 18,
            "learning_objectives": [
                "Understand decorator syntax",
                "Create custom decorators",
                "Use decorator arguments",
                "Apply multiple decorators"
            ]
        },
        {
            "name": "Generators and Iterators",
            "description": "Create efficient iterators with generators",
            "level_id": advanced_level.id if advanced_level else 3,
            "order": 19,
            "learning_objectives": [
                "Understand iterators",
                "Create generators with yield",
                "Use generator expressions",
                "Understand lazy evaluation"
            ]
        },
        {
            "name": "Regular Expressions",
            "description": "Pattern matching with regular expressions",
            "level_id": advanced_level.id if advanced_level else 3,
            "order": 20,
            "learning_objectives": [
                "Understand regex patterns",
                "Use re module functions",
                "Create complex patterns",
                "Validate and extract data"
            ]
        }
    ]
    
    for topic_data in topics:
        existing = db.query(Topic).filter(Topic.name == topic_data["name"]).first()
        if not existing:
            topic = Topic(**topic_data)
            db.add(topic)
    
    db.commit()
    db.close()


def seed_exercises():
    """Create Python exercises"""
    db = SessionLocal()
    
    exercises = [
        # Beginner Exercises
        {
            "title": "Hello, World!",
            "description": "Write a Python program that prints 'Hello, World!' to the console.",
            "difficulty_level": "easy",
            "topic": "Introduction to Python",
            "starter_code": "# Write your first Python program\n# Print a greeting message\n",
            "expected_output": "Hello, World!",
            "test_cases": [{"input": "", "expected_output": "Hello, World!"}],
            "hints": [
                "Use the print() function",
                "String literals are enclosed in quotes"
            ],
            "solution_code": "print('Hello, World!')"
        },
        {
            "title": "Create and Print Variables",
            "description": "Create variables for name, age, and city, then print them.",
            "difficulty_level": "easy",
            "topic": "Variables and Data Types",
            "starter_code": "# Create variables\n# name = ???\n# age = ???\n# city = ???\n\n# Print variables\n",
            "expected_output": "Name: John, Age: 25, City: New York",
            "test_cases": [{"input": "", "expected_output": "Name: John, Age: 25, City: New York"}],
            "hints": [
                "Use meaningful variable names",
                "Use f-strings for formatting"
            ],
            "solution_code": "name = 'John'\nage = 25\ncity = 'New York'\nprint(f'Name: {name}, Age: {age}, City: {city}')"
        },
        {
            "title": "Simple Calculator",
            "description": "Create a calculator that adds two numbers.",
            "difficulty_level": "easy",
            "topic": "Operators and Expressions",
            "starter_code": "# Read two numbers\nnum1 = float(input('Enter first number: '))\nnum2 = float(input('Enter second number: '))\n\n# Add them\n",
            "expected_output": "Sum: 15.0",
            "test_cases": [
                {"input": "10\n5", "expected_output": "Sum: 15.0"}
            ],
            "hints": [
                "Use the + operator",
                "Convert inputs to float for decimal numbers"
            ],
            "solution_code": "num1 = float(input('Enter first number: '))\nnum2 = float(input('Enter second number: '))\nsum_result = num1 + num2\nprint(f'Sum: {sum_result}')"
        },
        {
            "title": "Check if Even or Odd",
            "description": "Check if a number is even or odd using if-else.",
            "difficulty_level": "easy",
            "topic": "Control Flow - If Statements",
            "starter_code": "number = int(input('Enter a number: '))\n\n# Check if even or odd\n",
            "expected_output": "Even",
            "test_cases": [
                {"input": "4", "expected_output": "Even"},
                {"input": "7", "expected_output": "Odd"}
            ],
            "hints": [
                "Use the % operator for modulo",
                "If number % 2 == 0, it's even"
            ],
            "solution_code": "number = int(input('Enter a number: '))\nif number % 2 == 0:\n    print('Even')\nelse:\n    print('Odd')"
        },
        {
            "title": "Print Numbers from 1 to 10",
            "description": "Use a for loop to print numbers from 1 to 10.",
            "difficulty_level": "easy",
            "topic": "Loops - For and While",
            "starter_code": "# Write a for loop to print 1 to 10\n",
            "expected_output": "1\n2\n3\n4\n5\n6\n7\n8\n9\n10",
            "test_cases": [{"input": "", "expected_output": "1\n2\n3\n4\n5\n6\n7\n8\n9\n10"}],
            "hints": [
                "Use range(1, 11)",
                "Print each number on a new line"
            ],
            "solution_code": "for i in range(1, 11):\n    print(i)"
        },
        {
            "title": "Access List Elements",
            "description": "Create a list and access elements by index.",
            "difficulty_level": "easy",
            "topic": "Lists and Indexing",
            "starter_code": "fruits = ['apple', 'banana', 'cherry', 'date']\n\n# Print first element\n# Print last element\n# Print second element\n",
            "expected_output": "apple\ndate\nbanana",
            "test_cases": [{"input": "", "expected_output": "apple\ndate\nbanana"}],
            "hints": [
                "Index starts at 0",
                "Use negative index for last element: -1"
            ],
            "solution_code": "fruits = ['apple', 'banana', 'cherry', 'date']\nprint(fruits[0])\nprint(fruits[-1])\nprint(fruits[1])"
        },
        {
            "title": "Sum Function",
            "description": "Create a function that calculates the sum of two numbers.",
            "difficulty_level": "easy",
            "topic": "Functions Basics",
            "starter_code": "# Define a function add that takes two parameters\n\n# Call the function with 5 and 3\n",
            "expected_output": "8",
            "test_cases": [{"input": "", "expected_output": "8"}],
            "hints": [
                "Use def keyword to define function",
                "Use return to return the result"
            ],
            "solution_code": "def add(a, b):\n    return a + b\n\nresult = add(5, 3)\nprint(result)"
        },
        {
            "title": "String Manipulation",
            "description": "Reverse a string and convert it to uppercase.",
            "difficulty_level": "easy",
            "topic": "Strings and Text Processing",
            "starter_code": "text = 'python'\n\n# Reverse the string\n# Convert to uppercase\n",
            "expected_output": "NOHTYP",
            "test_cases": [{"input": "", "expected_output": "NOHTYP"}],
            "hints": [
                "Use [::-1] to reverse",
                "Use upper() method"
            ],
            "solution_code": "text = 'python'\nreversed_text = text[::-1]\nprint(reversed_text.upper())"
        },
        {
            "title": "Dictionary Access",
            "description": "Create a dictionary and access values by key.",
            "difficulty_level": "easy",
            "topic": "Dictionaries and Tuples",
            "starter_code": "student = {'name': 'Alice', 'age': 20, 'grade': 'A'}\n\n# Print the student's name\n# Print the student's grade\n",
            "expected_output": "Alice\nA",
            "test_cases": [{"input": "", "expected_output": "Alice\nA"}],
            "hints": [
                "Use dictionary[key] to access values",
                "Keys are case-sensitive"
            ],
            "solution_code": "student = {'name': 'Alice', 'age': 20, 'grade': 'A'}\nprint(student['name'])\nprint(student['grade'])"
        },
        {
            "title": "User Input Greeting",
            "description": "Get user's name and greet them.",
            "difficulty_level": "easy",
            "topic": "Input and Output",
            "starter_code": "# Get user's name\n# Greet the user\n",
            "expected_output": "Hello, World!",
            "test_cases": [{"input": "World", "expected_output": "Hello, World!"}],
            "hints": [
                "Use input() to get user input",
                "Use f-strings for greeting"
            ],
            "solution_code": "name = input()\nprint(f'Hello, {name}!')"
        },
        # Intermediate Exercises
        {
            "title": "List Comprehension - Squares",
            "description": "Create a list of squares of numbers 1-10 using list comprehension.",
            "difficulty_level": "medium",
            "topic": "List Comprehensions",
            "starter_code": "# Create a list of squares using list comprehension\nsquares = ???\n\nprint(squares)\n",
            "expected_output": "[1, 4, 9, 16, 25, 36, 49, 64, 81, 100]",
            "test_cases": [{"input": "", "expected_output": "[1, 4, 9, 16, 25, 36, 49, 64, 81, 100]"}],
            "hints": [
                "Use [x**2 for x in range(1, 11)]",
                "List comprehension is more concise than loops"
            ],
            "solution_code": "squares = [x**2 for x in range(1, 11)]\nprint(squares)"
        },
        {
            "title": "Read and Count Lines",
            "description": "Read a file and count the number of lines.",
            "difficulty_level": "medium",
            "topic": "File Handling",
            "starter_code": "# Open a file and count lines\nwith open('test.txt', 'r') as file:\n    lines = ???\n\nprint(f'Number of lines: {len(lines)}')\n",
            "expected_output": "Number of lines: 5",
            "test_cases": [{"input": "", "expected_output": "Number of lines: 5"}],
            "hints": [
                "Use readlines() to get all lines",
                "Use len() to count lines"
            ],
            "solution_code": "with open('test.txt', 'r') as file:\n    lines = file.readlines()\n\nprint(f'Number of lines: {len(lines)}')"
        },
        {
            "title": "Try-Except Block",
            "description": "Catch and handle a division by zero error.",
            "difficulty_level": "medium",
            "topic": "Exception Handling",
            "starter_code": "# Handle division by zero\ntry:\n    result = 10 / int(input())\nexcept ???:\n    print('Cannot divide by zero')\n",
            "expected_output": "Cannot divide by zero",
            "test_cases": [{"input": "0", "expected_output": "Cannot divide by zero"}],
            "hints": [
                "Catch ZeroDivisionError",
                "Use except clause"
            ],
            "solution_code": "try:\n    result = 10 / int(input())\nexcept ZeroDivisionError:\n    print('Cannot divide by zero')"
        },
        {
            "title": "Create a Simple Class",
            "description": "Create a Dog class with name and bark method.",
            "difficulty_level": "medium",
            "topic": "Object-Oriented Programming Basics",
            "starter_code": "# Define a Dog class\nclass Dog:\n    def __init__(self, name):\n        self.name = name\n    \n    def bark(self):\n        return f'{self.name} says woof!'\n\ndog = Dog('Buddy')\nprint(dog.bark())\n",
            "expected_output": "Buddy says woof!",
            "test_cases": [{"input": "", "expected_output": "Buddy says woof!"}],
            "hints": [
                "Use class keyword",
                "__init__ is the constructor"
            ],
            "solution_code": "class Dog:\n    def __init__(self, name):\n        self.name = name\n    \n    def bark(self):\n        return f'{self.name} says woof!'\n\ndog = Dog('Buddy')\nprint(dog.bark())"
        },
        {
            "title": "Class Inheritance",
            "description": "Create an Animal parent class and Dog child class.",
            "difficulty_level": "medium",
            "topic": "Inheritance and Polymorphism",
            "starter_code": "# Create Animal class\nclass Animal:\n    def __init__(self, name):\n        self.name = name\n    \n    def speak(self):\n        return f'{self.name} makes a sound'\n\n# Create Dog class that inherits from Animal\nclass Dog(Animal):\n    def speak(self):\n        return f'{self.name} barks'\n\ndog = Dog('Max')\nprint(dog.speak())\n",
            "expected_output": "Max barks",
            "test_cases": [{"input": "", "expected_output": "Max barks"}],
            "hints": [
                "Use class Dog(Animal) for inheritance",
                "Override methods in child class"
            ],
            "solution_code": "class Animal:\n    def __init__(self, name):\n        self.name = name\n    \n    def speak(self):\n        return f'{self.name} makes a sound'\n\nclass Dog(Animal):\n    def speak(self):\n        return f'{self.name} barks'\n\ndog = Dog('Max')\nprint(dog.speak())"
        },
        {
            "title": "Import and Use math Module",
            "description": "Use the math module to calculate square root.",
            "difficulty_level": "medium",
            "topic": "Working with Modules and Packages",
            "starter_code": "# Import math module\nimport math\n\nnumber = int(input())\n\n# Calculate square root\nresult = math.sqrt(number)\nprint(f'Square root of {number} is {result}')\n",
            "expected_output": "Square root of 16 is 4.0",
            "test_cases": [{"input": "16", "expected_output": "Square root of 16 is 4.0"}],
            "hints": [
                "Use import math",
                "Use math.sqrt()"
            ],
            "solution_code": "import math\n\nnumber = int(input())\nresult = math.sqrt(number)\nprint(f'Square root of {number} is {result}')"
        },
        {
            "title": "Lambda and Map",
            "description": "Use lambda with map to square numbers.",
            "difficulty_level": "medium",
            "topic": "Lambda Functions and Map/Filter",
            "starter_code": "numbers = [1, 2, 3, 4, 5]\n\n# Use map and lambda to square numbers\nsquared = list(map(lambda x: ???, numbers))\n\nprint(squared)\n",
            "expected_output": "[1, 4, 9, 16, 25]",
            "test_cases": [{"input": "", "expected_output": "[1, 4, 9, 16, 25]"}],
            "hints": [
                "Lambda creates anonymous functions",
                "map applies function to each element"
            ],
            "solution_code": "numbers = [1, 2, 3, 4, 5]\nsquared = list(map(lambda x: x**2, numbers))\nprint(squared)"
        }
    ]
    
    for exercise_data in exercises:
        existing = db.query(Exercise).filter(Exercise.title == exercise_data["title"]).first()
        if not existing:
            exercise = Exercise(**exercise_data)
            db.add(exercise)
    
    db.commit()
    db.close()


def seed_quizzes():
    """Create Python quizzes"""
    db = SessionLocal()
    
    beginner_level = db.query(Level).filter(Level.name == "Beginner").first()
    intermediate_level = db.query(Level).filter(Level.name == "Intermediate").first()
    
    # Get a beginner topic
    intro_topic = db.query(Topic).filter(Topic.name == "Introduction to Python").first()
    variables_topic = db.query(Topic).filter(Topic.name == "Variables and Data Types").first()
    
    if intro_topic and beginner_level:
        quiz_data = {
            "title": "Python Basics Quiz",
            "description": "Test your knowledge of Python fundamentals",
            "topic_id": intro_topic.id,
            "level_id": beginner_level.id,
            "passing_score": 70,
            "time_limit_minutes": 15,
            "shuffle_questions": True
        }
        
        existing_quiz = db.query(Quiz).filter(Quiz.title == quiz_data["title"]).first()
        if not existing_quiz:
            quiz = Quiz(**quiz_data)
            db.add(quiz)
            db.flush()
            
            questions = [
                {
                    "quiz_id": quiz.id,
                    "question_text": "What is the output of print(5 + 3)?",
                    "question_type": "multiple_choice",
                    "options": ["8", "5", "3", "Error"],
                    "correct_answer": "8",
                    "explanation": "5 + 3 = 8",
                    "order": 1,
                    "points": 1
                },
                {
                    "quiz_id": quiz.id,
                    "question_text": "Which of the following is a valid variable name in Python?",
                    "question_type": "multiple_choice",
                    "options": ["2var", "var_name", "var-name", "var name"],
                    "correct_answer": "var_name",
                    "explanation": "Variable names must start with letter or underscore",
                    "order": 2,
                    "points": 1
                },
                {
                    "quiz_id": quiz.id,
                    "question_text": "Python is dynamically typed language",
                    "question_type": "true_false",
                    "options": ["True", "False"],
                    "correct_answer": "True",
                    "explanation": "Python doesn't require explicit type declaration",
                    "order": 3,
                    "points": 1
                },
                {
                    "quiz_id": quiz.id,
                    "question_text": "What does the len() function do?",
                    "question_type": "multiple_choice",
                    "options": [
                        "Returns the length of an object",
                        "Returns the type of an object",
                        "Converts to integer",
                        "None of the above"
                    ],
                    "correct_answer": "Returns the length of an object",
                    "explanation": "len() returns the number of items in an object",
                    "order": 4,
                    "points": 1
                }
            ]
            
            for q in questions:
                question = QuizQuestion(**q)
                db.add(question)
            
            db.commit()
    
    if variables_topic and beginner_level:
        quiz_data = {
            "title": "Variables and Data Types Quiz",
            "description": "Test your knowledge of Python variables and types",
            "topic_id": variables_topic.id,
            "level_id": beginner_level.id,
            "passing_score": 70,
            "time_limit_minutes": 15,
            "shuffle_questions": True
        }
        
        existing_quiz = db.query(Quiz).filter(Quiz.title == quiz_data["title"]).first()
        if not existing_quiz:
            quiz = Quiz(**quiz_data)
            db.add(quiz)
            db.flush()
            
            questions = [
                {
                    "quiz_id": quiz.id,
                    "question_text": "What is the data type of x = 5?",
                    "question_type": "multiple_choice",
                    "options": ["int", "float", "str", "bool"],
                    "correct_answer": "int",
                    "explanation": "5 is an integer",
                    "order": 1,
                    "points": 1
                },
                {
                    "quiz_id": quiz.id,
                    "question_text": "What is the output of type('hello')?",
                    "question_type": "multiple_choice",
                    "options": ["<class 'str'>", "<class 'int'>", "hello", "string"],
                    "correct_answer": "<class 'str'>",
                    "explanation": "type() returns the class of the object",
                    "order": 2,
                    "points": 1
                },
                {
                    "quiz_id": quiz.id,
                    "question_text": "You can change the value of a variable after it's created",
                    "question_type": "true_false",
                    "options": ["True", "False"],
                    "correct_answer": "True",
                    "explanation": "Variables can be reassigned in Python",
                    "order": 3,
                    "points": 1
                }
            ]
            
            for q in questions:
                question = QuizQuestion(**q)
                db.add(question)
            
            db.commit()
    
    db.close()


def main():
    """Run all seed functions"""
    print("Starting database seeding...")
    
    print("Seeding levels...")
    seed_levels()
    print("[SUCCESS] Levels seeded")
    
    print("Seeding topics...")
    seed_topics()
    print("[SUCCESS] Topics seeded")
    
    print("Seeding exercises...")
    seed_exercises()
    print("[SUCCESS] Exercises seeded")
    
    print("Seeding quizzes...")
    seed_quizzes()
    print("[SUCCESS] Quizzes seeded")
    
    print("\n[SUCCESS] Database seeding completed successfully!")


if __name__ == "__main__":
    main()
