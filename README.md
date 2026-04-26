# Django Backend Scaffold

This folder contains a Django backend scaffold that preserves the current frontend API contract.

## What is included

- JWT registration and login endpoints
- enrollment submission endpoint
- admin enrollment listing and deletion
- custom user model with roles
- admin token compatibility via `x-admin-token`
- CORS configuration for the frontend

## Main API routes

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/python`
- `GET /api/admin/enrollments`
- `DELETE /api/admin/enrollments/<id>`
- `GET /api/health`

## Next step

Run migrations, connect PostgreSQL if needed, then replace the old Node backend in the deployment pipeline.
