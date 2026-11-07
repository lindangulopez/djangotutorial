# Django Tutorial: Polls App

My work through the official [Django 6.1 tutorial](https://docs.djangoproject.com/en/6.1/intro/), which builds a small polls application. Parts 1–3 are complete.

## Setup

Requires Python 3.12.

```bash
git clone https://github.com/lindangulopez/djangotutorial.git
cd djangotutorial
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The secret key isn't stored in the repository. Copy the example file and generate a key of your own:

```bash
cp .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Paste the key into `.env` as `DJANGO_SECRET_KEY='...'`. Then create the database and start the server:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/polls/ for the app and http://127.0.0.1:8000/admin/ for the admin site.

## Progress

### Part 1: Requests and responses ✅

[Tutorial part 1](https://docs.djangoproject.com/en/6.1/intro/tutorial01/)

| File | What was done |
|---|---|
| `mysite/` | Created the project with `django-admin startproject` |
| `polls/` | Created the app with `python manage.py startapp polls` |
| `polls/views.py` | Added a first `index` view returning "Hello, world. You're at the polls index." |
| `polls/urls.py` | Created the app's URLconf, routing `""` to `index` |
| `mysite/urls.py` | Included `polls.urls` under `polls/` |

### Part 2: Models and the admin site ✅

[Tutorial part 2](https://docs.djangoproject.com/en/6.1/intro/tutorial02/)

| File | What was done |
|---|---|
| `polls/models.py` | Added the `Question` and `Choice` models, `__str__()` methods, and `was_published_recently()` |
| `mysite/settings.py` | Added `polls.apps.PollsConfig` to `INSTALLED_APPS` |
| `polls/migrations/0001_initial.py` | Created with `makemigrations polls` and applied with `migrate` |
| `polls/admin.py` | Registered `Question` with the admin site |

I also explored the database API in `python manage.py shell` and created a superuser.

### Part 3: Views and templates ✅

[Tutorial part 3](https://docs.djangoproject.com/en/6.1/intro/tutorial03/)

| File | What was done |
|---|---|
| `polls/views.py` | `index` and `detail` use `render()` and `get_object_or_404()`; `results` and `vote` are still simple placeholders |
| `polls/urls.py` | Added the `detail`, `results` and `vote` routes and the `app_name = "polls"` namespace |
| `polls/templates/polls/index.html` | Lists the five latest questions, with links built by `{% url 'polls:detail' question.id %}` |
| `polls/templates/polls/detail.html` | Shows a question and its choices |

Each page returns the expected response:

| Page | Result |
|---|---|
| `/polls/` | 200: list of the latest questions |
| `/polls/1/` | 200: question 1 and its choices |
| `/polls/99/` | 404: no such question |
| `/polls/1/results/` | 200: placeholder text |
| `/polls/1/vote/` | 200: placeholder text |

The tutorial's example of changing the detail URL to `specifics/<int:question_id>/` was left out. It demonstrates how `{% url %}` decouples templates from URL paths, and isn't a required step.

### Parts 4–8 ⏳

Not started: [forms and generic views](https://docs.djangoproject.com/en/6.1/intro/tutorial04/), [testing](https://docs.djangoproject.com/en/6.1/intro/tutorial05/), [static files](https://docs.djangoproject.com/en/6.1/intro/tutorial06/), [customizing the admin](https://docs.djangoproject.com/en/6.1/intro/tutorial07/) and [third-party packages](https://docs.djangoproject.com/en/6.1/intro/tutorial08/).

## Changes from the tutorial

- **Secret key in `.env`:** `SECRET_KEY` is loaded from a git-ignored `.env` file with [python-dotenv](https://pypi.org/project/python-dotenv/), so the key isn't published.
- **Not committed:** `.venv/`, `db.sqlite3` and `.env` are git-ignored, so each clone creates its own database and key.
