# Skyrim Alchemy Calculator Web UI

A Django-based web interface for calculating optimal potion combinations in Skyrim, with support for player stats, perks, and comprehensive alchemy datasets.

## Features

- **Calculator**: Interactive interface for selecting player stats, perks, and ingredient inventory
- **Datasets**: Browse and download complete ingredient and effect databases
- **Analysis & Insights**: Advanced analytics and Monte Carlo simulations (coming soon)

## Prerequisites

- Python 3.8 or higher
- Django 5.2.7 (automatically installed with dependencies)

## Running Locally

### Quick Start

From the project root directory, simply run:

```bash
python run_webui.py
```

The web application will start on `http://127.0.0.1:8000`

### Alternative Method

If you prefer to use Django's manage.py directly:

```bash
cd web_ui
python manage.py runserver
```

## Project Structure

```
web_ui/
├── manage.py                 # Django management script
├── skyrim_alchemy/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── calculator/              # Main application
│   ├── views.py            # View logic
│   ├── urls.py             # URL routing
│   ├── templates/          # HTML templates
│   │   └── calculator/
│   │       ├── base.html           # Base template with navigation
│   │       ├── calculator.html     # Calculator interface
│   │       ├── datasets.html       # Dataset viewer
│   │       └── insights.html       # Analytics section
│   └── static/             # Static files (CSS, JS)
└── README.md               # This file
```

## Development

### Database

The application uses SQLite for local development. The database file (`db.sqlite3`) is created automatically on first run.

### Templates

Templates use Django's templating system and are located in `calculator/templates/calculator/`. The base template provides:
- Tab navigation between sections
- Responsive 2-column layout for the calculator
- Dark theme styling

### Static Files

Static files (CSS, JavaScript) are served from `calculator/static/`. Currently, styles are embedded in the base template for simplicity.

## Firebase Deployment (Coming Soon)

The application is designed to be compatible with Firebase backend deployment. Configuration details will be added in a future update.

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, specify a different port:

```bash
cd web_ui
python manage.py runserver 8080
```

### Missing Dependencies

Ensure Django is installed:

```bash
pip install django
```

Or install from the project's requirements file (if available):

```bash
pip install -r requirements.txt
```

## Contributing

Found a bug or have a feature request? Please open an issue on the project's GitHub repository.
