#  FastAPI Movie Ticket Booking System

##  Project Overview
This project is a backend application built using FastAPI.  
It allows users to browse movies, book tickets, manage seat availability, and perform advanced operations like search, sorting, and pagination.

---

##  Features

### Day 1 — GET APIs
- Home route
- Get all movies
- Get movie by ID
- Movies summary
- Get all bookings

###  Day 2 — POST + Pydantic
- Booking API with request validation
- Field constraints (min length, limits)

###  Day 3 — Helper Functions
- find_movie()
- calculate_ticket_cost()
- Filter movies with query parameters

###  Day 4 — CRUD Operations
- Add new movie
- Update movie details
- Delete movie (with booking check)

###  Day 5 — Multi-Step Workflow
- Seat hold system
- Confirm booking
- Release hold

###  Day 6 — Advanced APIs
- Search movies (keyword-based)
- Sort movies
- Pagination
- Combined browse API

---

##  Tech Stack
- Python
- FastAPI
- Uvicorn

---

##  Project Structure
fastapi-movie-ticket-booking/
│


├── main.py


├── requirements.txt


├── README.md


└── screenshots/
 How to Run the Project
Install dependencies:
pip install -r requirements.txt

Run the server:
uvicorn main --reload

Open Swagger UI:
http://127.0.0.1:8000/docs

 Screenshots
All 20 API endpoints (Q1–Q20) are tested using Swagger UI.
Screenshots are stored inside the screenshots/ folder.

 Key Highlights
REST API development using FastAPI

Pydantic validation for request bodies

CRUD operations implementation

Multi-step booking workflow

Search, sorting, and pagination

Clean and structured backend design



