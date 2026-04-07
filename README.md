# Cloud Job Tracker

A full-stack, serverless job application tracking platform built with AWS and React, designed to demonstrate production-level cloud architecture, authentication, and secure API design.

---

## Overview

Cloud Job Tracker is a modern web application that allows users to manage and track their job applications through a secure, cloud-native system.

Users can create, update, and organize job applications while viewing real-time analytics through a personalized dashboard. The application enforces authentication and per-user data isolation using AWS Cognito and JWT-based authorization.

This project demonstrates real-world backend architecture, frontend integration, and cloud deployment practices.

---

## Features

* Secure user authentication (Sign up, Confirm account, Sign in)
* JWT-protected API endpoints
* Full CRUD functionality for job applications
* Real-time dashboard analytics
* Per-user data isolation
* Light mode / Dark mode toggle
* Input validation and sanitization (frontend + backend)
* API rate limiting via API Gateway
* Serverless infrastructure (no traditional servers)

---

## Architecture

```
                ┌──────────────────────┐
                │      React App       │
                │  (Frontend - SPA)    │
                └─────────┬────────────┘
                          │ HTTPS (JWT)
                          ▼
                ┌──────────────────────┐
                │   API Gateway        │
                │  (REST Endpoints)    │
                └─────────┬────────────┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
     ┌──────────┐  ┌──────────┐  ┌──────────┐
     │ Lambda   │  │ Lambda   │  │ Lambda   │
     │ (Create) │  │ (Update) │  │ (Delete) │
     └──────────┘  └──────────┘  └──────────┘
            │
            ▼
     ┌──────────────────────┐
     │     DynamoDB         │
     │  (User Data Store)   │
     └──────────────────────┘

                ┌──────────────────────┐
                │     Cognito          │
                │ (Auth & JWT Tokens)  │
                └──────────────────────┘
```

---

## Tech Stack

### Frontend

* React
* JavaScript (ES6+)
* CSS (custom styling with theme support)

### Backend

* Python 3.12
* AWS Lambda
* Amazon API Gateway
* Amazon DynamoDB

### Authentication & Security

* Amazon Cognito (User Pools)
* JWT authentication
* Input validation and sanitization
* API Gateway throttling (rate limiting)

### DevOps / Infrastructure

* AWS SAM (Infrastructure as Code)
* AWS CLI
* Git / GitHub

---

## API Endpoints

| Method | Endpoint      | Description             |
| ------ | ------------- | ----------------------- |
| GET    | /dashboard    | Retrieve job analytics  |
| GET    | /jobs         | Retrieve all user jobs  |
| GET    | /jobs/{jobId} | Retrieve a specific job |
| POST   | /jobs         | Create a new job        |
| PUT    | /jobs/{jobId} | Update a job            |
| DELETE | /jobs/{jobId} | Delete a job            |

All endpoints require a valid JWT token.

---


## Security Highlights

* No sensitive API keys exposed in frontend
* Authentication handled via Amazon Cognito
* JWT required for all API requests
* Backend validation and sanitization enforced
* User data strictly isolated by identity (`userId`)
* API Gateway throttling prevents abuse

---

## Project Structure

```
Cloud Job Tracker/
├── backend/
│   ├── src/
│   │   ├── create_job.py
│   │   ├── get_jobs.py
│   │   ├── get_job.py
│   │   ├── update_job.py
│   │   ├── delete_job.py
│   │   ├── dashboard.py
│   │   └── utils.py
│   └── template.yaml
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.js
│   └── package.json
```

---

## Deployment

### Backend (AWS SAM)

```bash
sam build
sam deploy
```

### Frontend (local)

```bash
cd frontend
npm install
npm start
```

### (Planned) Production Deployment

* Frontend: Amazon S3 + CloudFront
* Backend: AWS Lambda + API Gateway
* Domain: Route 53 (optional)

---

## Key Concepts Demonstrated

* Serverless architecture
* RESTful API design
* Secure authentication and authorization
* Infrastructure as Code (IaC)
* Full-stack development
* Cloud-native application design
* Data validation and sanitization

---

## Future Improvements

* Add filtering and sorting for job applications
* Implement pagination for scalability
* Add notifications/reminders for follow-ups
* Improve session handling (HTTP-only cookies)
* Add AWS WAF for enhanced security
* Introduce analytics or insights dashboard

---

## Author

Tim MacDonald
AWS Certified Developer – Associate
Cloud & Backend Developer

GitHub: https://github.com/CodeByTM
LinkedIn: https://linkedin.com/in/timmacdonaldd

---

## Summary

This project demonstrates the ability to design and implement a secure, scalable, and production-ready cloud application using AWS services and modern frontend technologies. It reflects strong understanding of serverless architecture, authentication, and full-stack development practices.
