# Django Banking API Project

This is a Django-based API for a fake financial institution. The API allows users to create accounts, make deposits, withdrawals, and transfers, and view transaction history.

## Setup Instructions

Follow these steps to set up the project on your local machine.

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtualenv (optional but recommended)
- Source code on your machine
- Install all dependencies as specify in `requirements.txt`

Then run `python manage.py runserver`

The project will be available at http://127.0.0.1:8000/.

## API Endpoints

API documentation is generated using Swagger and is available at:

http://127.0.0.1:8000/swagger/

### Authentication
- POST /register/: Create User to obtain token
- POST /token/: Obtain JWT token pair (access and refresh tokens).
- POST token/refresh/: Refresh JWT access token.

##### Endpoints below require authorization, please specify `Authorization: Bearer {token}` in the header, or `Bearer {token}` in the Authorize field in Swagger

### Accounts
- GET /api/accounts/: List all accounts.
- POST /api/accounts/: Create a new account.
- GET /api/accounts/{id}/: Retrieve account details.
- PUT /api/accounts/{id}/: Update account details.
- DELETE /api/accounts/{id}/: Delete an account.
- POST /api/accounts/{id}/deposit/: Deposit an amount into an account.
- POST /api/accounts/{id}/withdraw/: Withdraw an amount from an account.
- POST /api/accounts/{id}/transfer/: Transfer an amount from one account to another.

### Transactions
- GET /api/transactions/: List all transactions.
- GET /api/transactions/{id}/: Retrieve transaction details.