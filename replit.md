# Receita Federal Payment Portal

## Overview

This is a Flask-based web application that simulates a Brazilian Federal Revenue Service (Receita Federal) portal for tax payment regularization. The application handles customer data retrieval, generates payment requests via PIX (Brazilian instant payment system), and integrates with the For4Payments API for payment processing.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Session Management**: Flask sessions with environment-based secret key
- **Logging**: Python's built-in logging module configured for debug level
- **HTTP Client**: Requests library for external API communication

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Tailwind CSS (CDN)
- **Icons**: Font Awesome 5.15.3
- **Custom Fonts**: Rawline font family with multiple weights
- **JavaScript**: Vanilla JavaScript for countdown timers and form interactions

### API Integration
- **Customer Data API**: External lead database at `api-lista-leads.replit.app`
- **Payment Processing**: For4Payments API integration for PIX payments

## Key Components

### 1. Main Application (`app.py`)
- Flask application setup with session management
- Customer data retrieval from external API
- UTM parameter handling for SMS campaigns
- Route handling for different pages

### 2. Payment Integration (`for4payments.py`)
- For4Payments API wrapper class
- PIX payment creation functionality
- Error handling and validation for payment data
- Authentication token management

### 3. Templates
- **index.html**: Main landing page with customer information display
- **buscar-cpf.html**: CPF search functionality
- **verificar-cpf.html**: CPF verification page

### 4. Static Assets
- **countdown.js**: JavaScript countdown timer functionality
- **fonts/**: Custom Rawline font files in WOFF2 format

## Data Flow

1. **Customer Identification**: 
   - UTM parameters capture customer phone number
   - External API lookup retrieves customer data (name, CPF)
   - Session storage maintains customer information

2. **Payment Processing**:
   - Customer data validation (CPF format, email generation)
   - Payment request creation via For4Payments API
   - PIX payment generation with QR code and payment link

3. **User Interface**:
   - Dynamic content rendering based on customer data
   - Countdown timer for payment urgency
   - Responsive design for mobile compatibility

## External Dependencies

### APIs
- **Lead Database API**: `https://api-lista-leads.replit.app/api/search/{phone}`
- **For4Payments API**: `https://app.for4payments.com.br/api/v1`

### CDN Resources
- Tailwind CSS: `https://cdn.tailwindcss.com`
- Font Awesome: `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css`

### Environment Variables
- `SESSION_SECRET`: Flask session encryption key
- `FOR4PAYMENTS_SECRET_KEY`: API authentication token

## Deployment Strategy

### Development Setup
- Entry point: `main.py` runs Flask development server
- Debug mode enabled for development
- Host: `0.0.0.0`, Port: `5000`

### Production Considerations
- Gunicorn WSGI server (based on log files)
- Environment variable configuration required
- HTTPS recommended for payment processing
- Session security with proper secret key management

### Heroku Deployment
- `.python-version` file specifies Python 3.11
- `Procfile` configures web dyno with Gunicorn
- Required environment variables: `FOR4PAYMENTS_SECRET_KEY`, `SESSION_SECRET`
- Uses uv package manager for dependency management

### Error Handling
- Comprehensive logging for payment processing errors
- Graceful fallback for missing customer data
- Input validation for payment requests

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

- July 07, 2025: Initial setup
- July 07, 2025: Updated CPF search API to new endpoint with token `1285fe4s-e931-4071-a848-3fac8273c55a`
- July 07, 2025: Added dynamic CPF route (/<cpf>) that fetches real user data and displays confirmation form
- July 07, 2025: Replaced news content with user data confirmation when accessed via CPF URL
- July 07, 2025: Fixed Flask session secret key configuration with development fallback
- July 07, 2025: Formatted birth date to dd/mm/yyyy format and simplified confirmation interface
- July 10, 2025: Switched from For4Payments to Cashtime API integration per user request
- July 10, 2025: Created cashtime.py module with PIX payment functionality
- July 10, 2025: Experiencing 500 Internal Server Error from Cashtime API - investigating resolution
- July 10, 2025: Cashtime API restored and fully operational with successful PIX generation
- July 10, 2025: Added Pushcut webhook notification for every Cashtime transaction generated
- July 10, 2025: Updated payment amount from R$ 142,83 to R$ 73,48 per user request
- July 10, 2025: Increased payment amount from R$ 73,48 to R$ 173,48 per user request
- July 10, 2025: Added phone modal before PIX generation with SMS notification via ApisMS API
- July 10, 2025: Implemented SMS sending with operator detection and Brazilian phone formatting