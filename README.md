\# Banking API (FastAPI)



A backend banking system built using FastAPI that supports secure user operations, balance management, and atomic money transfers.



\---



\##  Features



\* User Registration \& Login (secure password hashing)

\* JWT-based Authentication

\* Deposit Money

\* Transfer Money between users

\* Atomic Transactions (ensures consistency)

\* Transaction History tracking

\* Input Validation and Error Handling



\---



\##  Key Concepts Implemented



\* \*\*Atomic Transactions\*\* → Ensures money is never lost during transfer

\* \*\*JWT Authentication\*\* → Secures endpoints and user identity

\* \*\*Database Relationships\*\* → Users and Transactions linked via foreign keys

\* \*\*Validation \& Error Handling\*\* → Prevents invalid operations



\---



\##  Tech Stack



\* \*\*Backend:\*\* FastAPI

\* \*\*Database:\*\* SQLite

\* \*\*ORM:\*\* SQLAlchemy

\* \*\*Authentication:\*\* JWT (python-jose)

\* \*\*Security:\*\* Passlib (bcrypt)



\---



\##  Project Structure



```

BankingAPI/

│

├── main.py          # API routes \& business logic

├── models.py        # Database models

├── database.py      # DB connection setup

├── init\_db.py       # DB initialization

├── requirements.txt

└── README.md

```



\---



\##  Run Locally



```bash

pip install -r requirements.txt

python init\_db.py

python -m uvicorn main:app --reload

```



\---



\##  API Endpoints



\### Auth



\* `POST /register`

\* `POST /login`



\### Banking



\* `GET /balance`

\* `POST /deposit`

\* `POST /transfer`



\### Transactions



\* `GET /transactions`



\---



\##  API Docs



Swagger UI available at:



```

http://127.0.0.1:8000/docs

```



\---



\##  Future Improvements



\* Add PostgreSQL for production

\* Implement role-based access

\* Add rate limiting

\* Add email/SMS notifications



\---



\##  Author



Built as part of backend engineering preparation focusing on real-world system design and scalable architecture.



