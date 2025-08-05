# HTTP URL Shortener
## Abstract
This project implements a lightweight HTTP URL Shortener microservice with optional custom shortcodes, expiry time, redirection, and analytics.
It integrates a mandatory remote logging middleware to send request, response, and event logs to a central evaluation service.
The service supports creating shortened URLs, redirecting to original URLs, and retrieving usage statistics, making it suitable for quick deployment in production-like environments.
## Problem Statement And  Objective
#### Problem Statement:
Long URLs are inconvenient for sharing and can be visually unappealing. There is a need for a service that shortens URLs, tracks their usage, and ensures time-based expiry while maintaining proper logging for observability.
#### Objectives:
Provide REST endpoints to shorten URLs with optional custom codes and expiry times.
Support HTTP redirection for shortened URLs.
Maintain analytics: click count, timestamps, referrer, IP address.
Implement remote logging middleware for observability.
Ensure robust error handling for invalid or expired links.
## System Architecture

### Client (Postman) ---> FastAPI App ---> In Memory Store ---> Remote Loggin API

## Tech Stack
#### Backend Framework: 
          FastAPI (Python) – for fast REST API development.
#### Logging: 
          Remote logging service via HTTP POST (provided token & URL).
#### Storage: 
          In-memory Python dictionary (or SQLite for persistence).
#### Language: 
          Python
#### Testing Tools:
           Swagger UI (/docs), Postman Collection.

##  Logging Middleware
Purpose: Send all request & response logs to the evaluation logging API.
Log Fields:
stack – "backend"
level – info / error / fatal
package – module name (shortener, redirect, stats)
message – event description
Integration:
Middleware logs every request and response.
Manual logs inside endpoints for events and errors.
## Error Handling
400 Bad Request – Shortcode already exists.
404 Not Found – Shortcode not found.
410 Gone – Link expired.
500 Internal Server Error – Unexpected issues, logged with fatal severity.
## Testing
Swagger UI: http://localhost:8000/docs for manual API testing.
Postman Collection:
Create Short URL
Redirect
Get Stats
Negative Cases:
Duplicate shortcode creation
Access expired link
Access unknown shortcode
## Future Enhancements
Persistent database storage (PostgreSQL, MongoDB).
User authentication for managing URLs.
Bulk URL shortening.
QR code generation for short links.
Caching for faster redirection.
## Conclusion
The implemented microservice fulfills the core requirements for an HTTP URL Shortener with remote logging middleware.
It ensures observability, robust error handling, and API usability while remaining lightweight enough to be implemented within the evaluation timeframe.
The modular design allows for future scalability, such as switching from in-memory storage to a database without major code changes.
