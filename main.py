from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# ---------------- DATA ----------------

movies = [
    {"id": 1, "title": "Inception", "genre": "Action", "language": "English", "duration_mins": 148, "ticket_price": 200, "seats_available": 50},
    {"id": 2, "title": "Avatar", "genre": "Action", "language": "English", "duration_mins": 162, "ticket_price": 250, "seats_available": 40},
    {"id": 3, "title": "RRR", "genre": "Action", "language": "Telugu", "duration_mins": 180, "ticket_price": 180, "seats_available": 60},
    {"id": 4, "title": "Jailer", "genre": "Drama", "language": "Tamil", "duration_mins": 150, "ticket_price": 170, "seats_available": 45},
    {"id": 5, "title": "KGF", "genre": "Action", "language": "Kannada", "duration_mins": 155, "ticket_price": 190, "seats_available": 55},
    {"id": 6, "title": "Pushpa", "genre": "Drama", "language": "Telugu", "duration_mins": 160, "ticket_price": 210, "seats_available": 50}
]

bookings = []
booking_counter = 1

holds = []
hold_counter = 1

# ---------------- MODELS ----------------

class BookingRequest(BaseModel):
    customer_name: str = Field(min_length=2)
    movie_id: int = Field(gt=0)
    seats: int = Field(gt=0, le=10)
    phone: str = Field(min_length=10)
    seat_type: str = "standard"
    promo_code: str = ""

class NewMovie(BaseModel):
    title: str = Field(min_length=2)
    genre: str = Field(min_length=2)
    language: str = Field(min_length=2)
    duration_mins: int = Field(gt=0)
    ticket_price: int = Field(gt=0)
    seats_available: int = Field(gt=0)

# ---------------- HELPERS ----------------

def find_movie(movie_id):
    for m in movies:
        if m["id"] == movie_id:
            return m
    return None

def calculate_ticket_cost(price, seats, seat_type, promo_code):
    multiplier = 1
    if seat_type == "premium":
        multiplier = 1.5
    elif seat_type == "recliner":
        multiplier = 2

    total = price * seats * multiplier

    discount = 0
    if promo_code == "SAVE10":
        discount = total * 0.1
    elif promo_code == "SAVE20":
        discount = total * 0.2

    final = total - discount
    return total, final

# ---------------- Q1 ----------------

@app.get("/")
def home():
    return {"message": "Welcome to CineStar Booking"}

# ---------------- Q2 ----------------

@app.get("/movies")
def get_movies():
    total_seats = sum(m["seats_available"] for m in movies)
    return {"movies": movies, "total": len(movies), "total_seats_available": total_seats}

# ---------------- FIXED ROUTES ----------------

@app.get("/movies/summary")
def summary():
    prices = [m["ticket_price"] for m in movies]
    genre_count = {}
    for m in movies:
        genre_count[m["genre"]] = genre_count.get(m["genre"], 0) + 1

    return {
        "total_movies": len(movies),
        "max_price": max(prices),
        "min_price": min(prices),
        "total_seats": sum(m["seats_available"] for m in movies),
        "movies_by_genre": genre_count
    }

@app.get("/movies/filter")
def filter_movies(genre: Optional[str] = None, language: Optional[str] = None,
                  max_price: Optional[int] = None, min_seats: Optional[int] = None):

    result = movies

    if genre is not None:
        result = [m for m in result if m["genre"] == genre]

    if language is not None:
        result = [m for m in result if m["language"] == language]

    if max_price is not None:
        result = [m for m in result if m["ticket_price"] <= max_price]

    if min_seats is not None:
        result = [m for m in result if m["seats_available"] >= min_seats]

    return result

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

    return {"total_found": len(result), "movies": result}

@app.get("/movies/sort")
def sort_movies(sort_by: str = "ticket_price", order: str = "asc"):
    valid = ["ticket_price", "title", "duration_mins", "seats_available"]

    if sort_by not in valid:
        return {"error": "Invalid field"}

    reverse = True if order == "desc" else False
    return sorted(movies, key=lambda x: x[sort_by], reverse=reverse)

@app.get("/movies/page")
def paginate_movies(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    end = start + limit
    total_pages = (len(movies) + limit - 1) // limit

    return {"page": page, "total_pages": total_pages, "movies": movies[start:end]}

# ---------------- BOOKINGS BASIC ----------------

@app.get("/bookings")
def get_bookings():
    total_revenue = sum(b["final_cost"] for b in bookings) if bookings else 0
    return {"bookings": bookings, "total": len(bookings), "total_revenue": total_revenue}

@app.post("/bookings")
def create_booking(req: BookingRequest):
    global booking_counter

    movie = find_movie(req.movie_id)
    if not movie:
        return {"error": "Movie not found"}

    if movie["seats_available"] < req.seats:
        return {"error": "Not enough seats"}

    original, final = calculate_ticket_cost(
        movie["ticket_price"], req.seats, req.seat_type, req.promo_code
    )

    movie["seats_available"] -= req.seats

    booking = {
        "booking_id": booking_counter,
        "customer_name": req.customer_name,
        "movie": movie["title"],
        "seats": req.seats,
        "seat_type": req.seat_type,
        "original_cost": original,
        "final_cost": final
    }

    bookings.append(booking)
    booking_counter += 1

    return booking

# ---------------- Q19 (IMPORTANT) ----------------

@app.get("/bookings/search")
def search_bookings(name: str):
    return [b for b in bookings if name.lower() in b["customer_name"].lower()]

@app.get("/bookings/sort")
def sort_bookings():
    return sorted(bookings, key=lambda x: x["final_cost"])

@app.get("/bookings/page")
def paginate_bookings(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    end = start + limit
    return bookings[start:end]

# ---------------- Q14-15 ----------------

@app.post("/seat-hold")
def hold_seats(customer_name: str, movie_id: int, seats: int):
    global hold_counter

    movie = find_movie(movie_id)
    if not movie:
        return {"error": "Movie not found"}

    if movie["seats_available"] < seats:
        return {"error": "Not enough seats"}

    movie["seats_available"] -= seats

    hold = {
        "hold_id": hold_counter,
        "customer_name": customer_name,
        "movie_id": movie_id,
        "seats": seats
    }

    holds.append(hold)
    hold_counter += 1

    return hold

@app.get("/seat-hold")
def get_holds():
    return holds

@app.post("/seat-confirm/{hold_id}")
def confirm_hold(hold_id: int):
    global booking_counter

    for h in holds:
        if h["hold_id"] == hold_id:
            movie = find_movie(h["movie_id"])

            original, final = calculate_ticket_cost(
                movie["ticket_price"], h["seats"], "standard", ""
            )

            booking = {
                "booking_id": booking_counter,
                "customer_name": h["customer_name"],
                "movie": movie["title"],
                "seats": h["seats"],
                "seat_type": "standard",
                "original_cost": original,
                "final_cost": final
            }

            bookings.append(booking)
            holds.remove(h)
            booking_counter += 1

            return booking

    return {"error": "Hold not found"}

@app.delete("/seat-release/{hold_id}")
def release_hold(hold_id: int):
    for h in holds:
        if h["hold_id"] == hold_id:
            movie = find_movie(h["movie_id"])
            movie["seats_available"] += h["seats"]
            holds.remove(h)
            return {"message": "Released"}

    return {"error": "Hold not found"}

# ---------------- CRUD ----------------

@app.post("/movies", status_code=201)
def add_movie(movie: NewMovie):
    for m in movies:
        if m["title"].lower() == movie.title.lower():
            return {"error": "Movie already exists"}

    new_movie = movie.dict()
    new_movie["id"] = len(movies) + 1
    movies.append(new_movie)
    return new_movie

@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, ticket_price: int = None, seats_available: int = None):
    movie = find_movie(movie_id)
    if not movie:
        return {"error": "Movie not found"}

    if ticket_price is not None:
        movie["ticket_price"] = ticket_price

    if seats_available is not None:
        movie["seats_available"] = seats_available

    return movie

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    movie = find_movie(movie_id)
    if not movie:
        return {"error": "Movie not found"}

    for b in bookings:
        if b["movie"] == movie["title"]:
            return {"error": "Cannot delete, bookings exist"}

    movies.remove(movie)
    return {"message": "Movie deleted"}

# ---------------- FINAL ----------------

@app.get("/movies/browse")
def browse_movies(keyword: Optional[str] = None, sort_by: str = "ticket_price",
                  order: str = "asc", page: int = 1, limit: int = 3,
                  genre: Optional[str] = None, language: Optional[str] = None):

    result = movies

    if keyword:
        result = [m for m in result if keyword.lower() in m["title"].lower()
                  or keyword.lower() in m["genre"].lower()
                  or keyword.lower() in m["language"].lower()]

    if genre:
        result = [m for m in result if m["genre"] == genre]

    if language:
        result = [m for m in result if m["language"] == language]

    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    start = (page - 1) * limit
    end = start + limit

    return {"total": len(result), "movies": result[start:end]}

# ---------------- LAST ----------------

@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    movie = find_movie(movie_id)
    if not movie:
        return {"error": "Movie not found"}
    return movie