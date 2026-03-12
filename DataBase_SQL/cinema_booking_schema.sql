-- ============================================================
--  CINEMA TICKET BOOKING SYSTEM
--  Database Schema (SQL Server / T-SQL)
-- ============================================================

-- ============================================================
-- 1. CUSTOMER
-- ============================================================
CREATE TABLE Customer (
    customer_id     INT             IDENTITY(1,1) PRIMARY KEY,
    first_name      VARCHAR(50)     NOT NULL,
    last_name       VARCHAR(50)     NOT NULL,
    email           VARCHAR(100)    NOT NULL UNIQUE,
    phone           VARCHAR(15),
    date_of_birth   DATE,
    password_hash   VARCHAR(255)    NOT NULL,
    created_at      DATETIME        DEFAULT GETDATE()
);

-- ============================================================
-- 2. MOVIE
-- ============================================================
CREATE TABLE Movie (
    movie_id        INT             IDENTITY(1,1) PRIMARY KEY,
    title           VARCHAR(150)    NOT NULL,
    description     TEXT,
    duration_min    INT             NOT NULL,
    genre           VARCHAR(50),
    language        VARCHAR(30),
    rating          VARCHAR(10),
    release_date    DATE,
    poster_url      VARCHAR(255)
);

-- ============================================================
-- 3. CINEMA
-- ============================================================
CREATE TABLE Cinema (
    cinema_id       INT             IDENTITY(1,1) PRIMARY KEY,
    name            VARCHAR(100)    NOT NULL,
    address         VARCHAR(255),
    city            VARCHAR(50),
    phone           VARCHAR(15)
);

-- ============================================================
-- 4. HALL
-- ============================================================
CREATE TABLE Hall (
    hall_id         INT             IDENTITY(1,1) PRIMARY KEY,
    cinema_id       INT             NOT NULL,
    hall_name       VARCHAR(50)     NOT NULL,
    total_seats     INT             NOT NULL,
    hall_type       VARCHAR(30),

    CONSTRAINT fk_hall_cinema
        FOREIGN KEY (cinema_id) REFERENCES Cinema(cinema_id)
        ON DELETE CASCADE
);

-- ============================================================
-- 5. SEAT
-- ============================================================
CREATE TABLE Seat (
    seat_id         INT             IDENTITY(1,1) PRIMARY KEY,
    hall_id         INT             NOT NULL,
    row_label       CHAR(2)         NOT NULL,
    seat_number     INT             NOT NULL,
    seat_type       VARCHAR(20)     DEFAULT 'Regular',

    CONSTRAINT fk_seat_hall
        FOREIGN KEY (hall_id) REFERENCES Hall(hall_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_seat_position UNIQUE (hall_id, row_label, seat_number)
);

-- ============================================================
-- 6. SHOWTIME
-- ============================================================
CREATE TABLE Showtime (
    showtime_id     INT             IDENTITY(1,1) PRIMARY KEY,
    movie_id        INT             NOT NULL,
    hall_id         INT             NOT NULL,
    start_time      DATETIME        NOT NULL,
    end_time        DATETIME        NOT NULL,
    price_standard  DECIMAL(6,2)    NOT NULL,
    price_vip       DECIMAL(6,2)    NOT NULL,

    CONSTRAINT fk_showtime_movie
        FOREIGN KEY (movie_id) REFERENCES Movie(movie_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_showtime_hall
        FOREIGN KEY (hall_id) REFERENCES Hall(hall_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_hall_time UNIQUE (hall_id, start_time)
);

-- ============================================================
-- 7. BOOKING
-- ============================================================
CREATE TABLE Booking (
    booking_id      INT             IDENTITY(1,1) PRIMARY KEY,
    customer_id     INT             NOT NULL,
    showtime_id     INT             NOT NULL,
    booking_date    DATETIME        DEFAULT GETDATE(),
    total_amount    DECIMAL(8,2)    NOT NULL,
    status          VARCHAR(20)     DEFAULT 'Confirmed',

    CONSTRAINT fk_booking_customer
        FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_booking_showtime
        FOREIGN KEY (showtime_id) REFERENCES Showtime(showtime_id)
        ON DELETE CASCADE
);

-- ============================================================
-- 8. TICKET
-- ============================================================
CREATE TABLE Ticket (
    ticket_id       INT             IDENTITY(1,1) PRIMARY KEY,
    booking_id      INT             NOT NULL,
    seat_id         INT             NOT NULL,
    price           DECIMAL(6,2)    NOT NULL,
    ticket_status   VARCHAR(20)     DEFAULT 'Active',

    CONSTRAINT fk_ticket_booking
        FOREIGN KEY (booking_id) REFERENCES Booking(booking_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_ticket_seat
        FOREIGN KEY (seat_id) REFERENCES Seat(seat_id),

    CONSTRAINT uq_ticket_seat_booking UNIQUE (booking_id, seat_id)
);

-- ============================================================
-- 9. PAYMENT
-- ============================================================
CREATE TABLE Payment (
    payment_id      INT             IDENTITY(1,1) PRIMARY KEY,
    booking_id      INT             NOT NULL UNIQUE,
    payment_method  VARCHAR(30),
    payment_date    DATETIME        DEFAULT GETDATE(),
    amount_paid     DECIMAL(8,2)    NOT NULL,
    payment_status  VARCHAR(20)     DEFAULT 'Success',

    CONSTRAINT fk_payment_booking
        FOREIGN KEY (booking_id) REFERENCES Booking(booking_id)
        ON DELETE CASCADE
);
