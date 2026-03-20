# 🎬 FastAPI Movie Ticket Booking System

## 📌 Project Overview

This project is a **Movie Ticket Booking Backend System** built using **FastAPI**.
It simulates a real-world cinema booking application where users can browse movies, book tickets, and manage seat reservations.
⭐ This project demonstrates real-world backend workflow similar to BookMyShow.

## 🚀 Features Implemented

### 🟢 Day 1 — Basic GET APIs

* Home route
* Get all movies
* Get movie by ID
* Get bookings
* Movies summary endpoint

### 🟡 Day 2 — POST APIs with Pydantic Validation

* Booking creation using request body
* Field validations (min length, constraints)
* Error handling for invalid inputs

### 🟠 Day 3 — Helper Functions

* `find_movie()` → Find movie by ID
* `calculate_ticket_cost()` → Cost calculation with seat type & promo
* `filter_movies_logic()` → Filtering logic


### 🔵 Day 4 — CRUD Operations

* Add new movie (POST)
* Update movie (PUT)
* Delete movie (DELETE with business rule)


### 🟣 Day 5 — Multi-Step Workflow

* Seat Hold → Temporary reservation
* Seat Confirm → Convert hold to booking
* Seat Release → Cancel hold


### 🔴 Day 6 — Advanced APIs

* Movie search (multi-field)
* Sorting (price, duration, seats)
* Pagination
* Combined browsing API (search + filter + sort + paginate)


## 🧠 Key Concepts Covered

* FastAPI routing
* Pydantic models & validation
* CRUD operations
* Helper functions
* Multi-step workflows
* Query parameters
* Search, Sorting & Pagination



## 🛠️ Tech Stack

* Python
* FastAPI
* Uvicorn


## 💼 Use Case

This project demonstrates how backend systems handle:

* Ticket booking logic
* Seat availability management
* Real-time workflows
* API-based architecture


##  Tech Stack
* Backend: FastAPI
* Data Validation: Pydantic
* Server: Uvicorn


##  To install dependencies:
pip install fastapi uvicorn

##  To run the server:
uvicorn main:app --reload

##  To open in browser:
http://127.0.0.1:8000/

## 🔗 Author

**Arjun Naluvala**
