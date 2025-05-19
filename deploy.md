# SecureScout Deployment Guide

This document provides instructions for deploying and running the SecureScout security testing platform.

## Backend Deployment

### Prerequisites
- Python 3.8+
- Redis (for task queue in production)
- Internet connection

### Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/securescout.git
cd securescout
```

2. Create and activate a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install backend dependencies:
```
pip install -r requirements.txt
```

4. Create necessary directories:
```
mkdir -p logs reports data
```

5. Configure the application by creating a `.env` file:
```
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
SECURESCOUT_ENV=development  # Change to 'production' for production deployment
```

### Running the Backend

For development:
```
cd backend
python app.py
```

For quick demonstration with the demo backend:
```
python demo_backend.py
```

For production, use a WSGI server like Gunicorn:
```
gunicorn -w 4 -b 0.0.0.0:8001 backend.app:app
```

## Frontend Deployment

### Prerequisites
- Node.js 16+
- npm or yarn

### Installation

1. Navigate to the frontend directory:
```
cd frontend
```

2. Install frontend dependencies:
```
npm install --legacy-peer-deps
```

3. Configure the API URL by creating a `.env` file:
```
REACT_APP_API_URL=http://localhost:8001
PORT=8002
```

### Running the Frontend

For development:
```
npm start
```

For production build:
```
npm run build
```

Then serve the built files from the `build` directory using a web server like Nginx or serve:
```
npx serve -s build
```

## Docker Deployment

For containerized deployment, use the included Dockerfile and docker-compose.yml:

```
docker-compose up -d
```

This will start both the backend and frontend services, as well as Redis for task queuing.

## Security Considerations

1. Always change default keys and secrets in production
2. Set up proper firewall rules to restrict access
3. Run the application behind a reverse proxy with SSL termination
4. Consider rate limiting to prevent abuse
5. Regularly update dependencies

## Troubleshooting

If you encounter issues with the scan engine:

1. Check logs in the `logs` directory
2. Ensure all dependencies are installed
3. Verify connectivity to the target application
4. Check permissions for report and data directories

For API connectivity issues:

1. Verify CORS settings in the backend
2. Check API URL configuration in frontend
3. Test API endpoints using curl or Postman