from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()


#  DATA


movies = [
    {"id": 1, "title": "Gabbar Singh", "genre": "Action", "language": "Telugu", "duration_mins": 180, "ticket_price": 200, "seats_available": 50},
    {"id": 2, "title": "KGF", "genre": "Action", "language": "Kannada", "duration_mins": 170, "ticket_price": 180, "seats_available": 40},
    {"id": 3, "title": "Jawan", "genre": "Drama", "language": "Hindi", "duration_mins": 160, "ticket_price": 220, "seats_available": 60},
    {"id": 4, "title": "Leo", "genre": "Action", "language": "Tamil", "duration_mins": 150, "ticket_price": 210, "seats_available": 30},
    {"id": 5, "title": "Kantara", "genre": "Drama", "language": "Kannada", "duration_mins": 140, "ticket_price": 190, "seats_available": 35},
    {"id": 6, "title": "Avengers", "genre": "Action", "language": "English", "duration_mins": 180, "ticket_price": 250, "seats_available": 45},
]

bookings = []
booking_counter = 1

holds = []
hold_counter = 1


#  DAY 1 — GET APIs


@app.get("/")
def home():
    return {"message": "Welcome to CineStar Booking"}

@app.get("/movies")
def get_movies():
    total_seats = sum(m["seats_available"] for m in movies)
    return {"movies": movies, "total": len(movies), "total_seats_available": total_seats}

@app.get("/bookings")
def get_bookings():
    total_revenue = sum(b["total_cost"] for b in bookings)
    return {"bookings": bookings, "total": len(bookings), "total_revenue": total_revenue}

@app.get("/movies/summary")
def movies_summary():
    genre_count = {}
    for m in movies:
        genre_count[m["genre"]] = genre_count.get(m["genre"], 0) + 1

    return {
        "total_movies": len(movies),
        "most_expensive": max(movies, key=lambda x: x["ticket_price"])["ticket_price"],
        "cheapest": min(movies, key=lambda x: x["ticket_price"])["ticket_price"],
        "total_seats": sum(m["seats_available"] for m in movies),
        "genre_count": genre_count
    }


#  DAY 2 — PYDANTIC


class BookingRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    movie_id: int = Field(..., gt=0)
    seats: int = Field(..., gt=0, le=10)
    phone: str = Field(..., min_length=10)
    seat_type: str = "standard"
    promo_code: str = ""

class NewMovie(BaseModel):
    title: str = Field(..., min_length=2)
    genre: str = Field(..., min_length=2)
    language: str = Field(..., min_length=2)
    duration_mins: int = Field(..., gt=0)
    ticket_price: int = Field(..., gt=0)
    seats_available: int = Field(..., gt=0)


#  DAY 3 — HELPERS


def find_movie(movie_id):
    for m in movies:
        if m["id"] == movie_id:
            return m
    return None

def calculate_ticket_cost(base_price, seats, seat_type, promo_code):
    multiplier = 1
    if seat_type == "premium":
        multiplier = 1.5
    elif seat_type == "recliner":
        multiplier = 2

    original = base_price * seats * multiplier

    discount = 0
    if promo_code == "SAVE10":
        discount = original * 0.1
    elif promo_code == "SAVE20":
        discount = original * 0.2

    final = original - discount
    return original, final

def filter_movies_logic(genre, language, max_price, min_seats):
    result = movies

    if genre is not None:
        result = [m for m in result if m["genre"].lower() == genre.lower()]
    if language is not None:
        result = [m for m in result if m["language"].lower() == language.lower()]
    if max_price is not None:
        result = [m for m in result if m["ticket_price"] <= max_price]
    if min_seats is not None:
        result = [m for m in result if m["seats_available"] >= min_seats]

    return result


#  DAY 2 — POST BOOKING


@app.post("/bookings", status_code=201)
def create_booking(data: BookingRequest):
    global booking_counter

    movie = find_movie(data.movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    if movie["seats_available"] < data.seats:
        raise HTTPException(status_code=400, detail="Not enough seats")

    original, final = calculate_ticket_cost(
        movie["ticket_price"], data.seats, data.seat_type, data.promo_code
    )

    movie["seats_available"] -= data.seats

    booking = {
        "booking_id": booking_counter,
        "movie_id": data.movie_id,
        "customer": data.customer_name,
        "seats": data.seats,
        "seat_type": data.seat_type,
        "total_cost": final
    }

    bookings.append(booking)
    booking_counter += 1

    return {"booking": booking, "original_cost": original, "final_cost": final}


#  DAY 3 — FILTER


@app.get("/movies/filter")
def filter_movies(
    genre: Optional[str] = None,
    language: Optional[str] = None,
    max_price: Optional[int] = None,
    min_seats: Optional[int] = None
):
    return filter_movies_logic(genre, language, max_price, min_seats)


#  DAY 4 — CRUD


@app.post("/movies", status_code=201)
def add_movie(movie: NewMovie):
    for m in movies:
        if m["title"].lower() == movie.title.lower():
            raise HTTPException(status_code=400, detail="Duplicate movie")

    new_movie = movie.dict()
    new_movie["id"] = len(movies) + 1
    movies.append(new_movie)
    return new_movie

@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, ticket_price: Optional[int] = None, seats_available: Optional[int] = None):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Not found")

    if ticket_price is not None:
        movie["ticket_price"] = ticket_price
    if seats_available is not None:
        movie["seats_available"] = seats_available

    return movie

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Not found")

    for b in bookings:
        if b["movie_id"] == movie_id:
            raise HTTPException(status_code=400, detail="Movie has bookings")

    movies.remove(movie)
    return {"message": "Deleted successfully"}

#  DAY 5 — WORKFLOW


@app.post("/seat-hold")
def seat_hold(customer_name: str, movie_id: int, seats: int):
    global hold_counter

    movie = find_movie(movie_id)
    if not movie or movie["seats_available"] < seats:
        raise HTTPException(status_code=400, detail="Not enough seats")

    movie["seats_available"] -= seats

    hold = {
        "hold_id": hold_counter,
        "customer": customer_name,
        "movie_id": movie_id,
        "seats": seats
    }

    holds.append(hold)
    hold_counter += 1
    return hold

@app.get("/seat-hold")
def view_holds():
    return holds

@app.post("/seat-confirm/{hold_id}")
def confirm_seat(hold_id: int):
    global booking_counter

    for h in holds:
        if h["hold_id"] == hold_id:
            movie = find_movie(h["movie_id"])

            booking = {
                "booking_id": booking_counter,
                "movie_id": h["movie_id"],
                "seats": h["seats"],
                "total_cost": movie["ticket_price"] * h["seats"]
            }

            bookings.append(booking)
            holds.remove(h)
            booking_counter += 1
            return booking

    raise HTTPException(status_code=404, detail="Hold not found")

@app.delete("/seat-release/{hold_id}")
def release_seat(hold_id: int):
    for h in holds:
        if h["hold_id"] == hold_id:
            movie = find_movie(h["movie_id"])
            movie["seats_available"] += h["seats"]
            holds.remove(h)
            return {"message": "Seat released"}

    raise HTTPException(status_code=404, detail="Hold not found")


#  DAY 6 — MOVIES ADVANCED


@app.get("/movies/search")
def search_movies(keyword: str):
    result = [
        m for m in movies
        if keyword.lower() in m["title"].lower()
        or keyword.lower() in m["genre"].lower()
        or keyword.lower() in m["language"].lower()
    ]

    if not result:
        return {"message": "No movies found"}

    return {"results": result, "total_found": len(result)}

@app.get("/movies/sort")
def sort_movies(sort_by: str = "ticket_price", order: str = "asc"):
    valid_fields = ["ticket_price", "title", "duration_mins", "seats_available"]

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Order must be asc or desc")

    reverse = True if order == "desc" else False

    return sorted(movies, key=lambda x: x[sort_by], reverse=reverse)

@app.get("/movies/page")
def paginate_movies(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    end = start + limit
    total_pages = (len(movies) + limit - 1) // limit

    return {"total": len(movies), "total_pages": total_pages, "data": movies[start:end]}


#  Q19 — BOOKINGS ADVANCED


@app.get("/bookings/search")
def search_bookings(customer_name: str):
    result = [b for b in bookings if customer_name.lower() in b["customer"].lower()]

    if not result:
        return {"message": "No bookings found"}

    return {"results": result, "total": len(result)}

@app.get("/bookings/sort")
def sort_bookings(sort_by: str = "total_cost", order: str = "asc"):
    valid_fields = ["total_cost", "seats"]

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail="Invalid field")

    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Order must be asc or desc")

    reverse = True if order == "desc" else False

    return sorted(bookings, key=lambda x: x[sort_by], reverse=reverse)

@app.get("/bookings/page")
def paginate_bookings(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    end = start + limit
    total_pages = (len(bookings) + limit - 1) // limit

    return {"total": len(bookings), "total_pages": total_pages, "data": bookings[start:end]}


#  Q20 — COMBINED BROWSE


@app.get("/movies/browse")
def browse_movies(
    keyword: Optional[str] = None,
    genre: Optional[str] = None,
    language: Optional[str] = None,
    sort_by: str = "ticket_price",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    result = movies

    if keyword:
        result = [m for m in result if keyword.lower() in m["title"].lower()]

    if genre:
        result = [m for m in result if m["genre"].lower() == genre.lower()]

    if language:
        result = [m for m in result if m["language"].lower() == language.lower()]

    valid_fields = ["ticket_price", "title", "duration_mins", "seats_available"]

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    start = (page - 1) * limit
    end = start + limit

    return {"total": len(result), "data": result[start:end]}


#  VARIABLE ROUTE LAST


@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie
