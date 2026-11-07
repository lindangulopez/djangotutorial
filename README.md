# Django Tutorial: Polls App

My work through the official [Django 6.1 tutorial](https://docs.djangoproject.com/en/6.1/intro/), which builds a small polls application. Parts 1–7 are complete.

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

Open <http://127.0.0.1:8000/polls/> for the app and <http://127.0.0.1:8000/admin/> for the admin site.

## Using the app

| Page | What it shows |
| --- | --- |
| `/polls/` | The five latest questions, as links. There are no vote options on this page. |
| `/polls/<id>/` | One question's voting form, with a radio button for each choice |
| `/polls/<id>/results/` | Vote counts for each choice, shown after you vote |

To vote, click a question on `/polls/`, pick a choice and press **Vote**.

A question with no choices shows only the **Vote** button. To add choices, open the admin site at `/admin/`, go to **Questions**, click the question, and fill in the **Choices** rows at the bottom of the page. Three empty rows are shown each time. Press **Save**, then refresh the question's page to see the new options.

## Progress

### Part 1: Requests and responses ✅

[Tutorial part 1](https://docs.djangoproject.com/en/6.1/intro/tutorial01/)

| File | What was done |
| --- | --- |
| `mysite/` | Created the project with `django-admin startproject` |
| `polls/` | Created the app with `python manage.py startapp polls` |
| `polls/views.py` | Added a first `index` view returning "Hello, world. You're at the polls index." |
| `polls/urls.py` | Created the app's URLconf, routing `""` to `index` |
| `mysite/urls.py` | Included `polls.urls` under `polls/` |

### Part 2: Models and the admin site ✅

[Tutorial part 2](https://docs.djangoproject.com/en/6.1/intro/tutorial02/)

| File | What was done |
| --- | --- |
| `polls/models.py` | Added the `Question` and `Choice` models, `__str__()` methods, and `was_published_recently()` |
| `mysite/settings.py` | Added `polls.apps.PollsConfig` to `INSTALLED_APPS` |
| `polls/migrations/0001_initial.py` | Created with `makemigrations polls` and applied with `migrate` |
| `polls/admin.py` | Registered `Question` with the admin site |

I also explored the database API in `python manage.py shell` and created a superuser.

### Part 3: Views and templates ✅

[Tutorial part 3](https://docs.djangoproject.com/en/6.1/intro/tutorial03/)

| File | What was done |
| --- | --- |
| `polls/views.py` | `index` and `detail` use `render()` and `get_object_or_404()`; `results` and `vote` are simple placeholders |
| `polls/urls.py` | Added the `detail`, `results` and `vote` routes and the `app_name = "polls"` namespace |
| `polls/templates/polls/index.html` | Lists the five latest questions, with links built by `{% url 'polls:detail' question.id %}` |
| `polls/templates/polls/detail.html` | Shows a question and its choices |

The tutorial's example of changing the detail URL to `specifics/<int:question_id>/` was left out. It demonstrates how `{% url %}` decouples templates from URL paths, and isn't a required step.

### Part 4: Forms and generic views ✅

[Tutorial part 4](https://docs.djangoproject.com/en/6.1/intro/tutorial04/)

| File | What was done |
| --- | --- |
| `polls/templates/polls/detail.html` | Replaced with a voting form: one radio button per choice, `{% csrf_token %}`, and an error message when no choice is picked |
| `polls/views.py` | `vote` records the vote with an `F("votes") + 1` expression and redirects to the results page; `index`, `detail` and `results` are now the generic views `IndexView`, `DetailView` and `ResultsView` |
| `polls/templates/polls/results.html` | New: shows each choice's vote count and a "Vote again?" link |
| `polls/urls.py` | Routes point to the generic views, and the `detail` and `results` URLs capture `pk` instead of `question_id` |

Each page and the voting flow return the expected response:

| Request | Result |
| --- | --- |
| `GET /polls/` | 200: list of the latest questions |
| `GET /polls/1/` | 200: voting form for question 1 |
| `GET /polls/99/` | 404: no such question |
| `GET /polls/1/results/` | 200: vote counts for question 1 |
| `POST /polls/1/vote/` with a choice | 302: vote counted, redirect to `/polls/1/results/` |
| `POST /polls/1/vote/` without a choice | 200: form shown again with "You didn't select a choice." |

### Part 5: Automated tests ✅

[Tutorial part 5](https://docs.djangoproject.com/en/6.1/intro/tutorial05/)

| File | What was done |
| --- | --- |
| `polls/models.py` | Fixed `was_published_recently()`, which returned `True` for questions dated in the future; it now only returns `True` for the past 24 hours |
| `polls/views.py` | `IndexView`, `DetailView` and `ResultsView` filter on `pub_date__lte=timezone.now()`, so questions with a future publication date are hidden from the list and return 404 on their detail and results pages |
| `polls/tests.py` | Added 12 tests across `QuestionModelTests`, `QuestionIndexViewTests`, `QuestionDetailViewTests` and `QuestionResultsViewTests`, with a `create_question()` helper |

Run the tests with:

```bash
python manage.py test polls
```

All 12 tests pass. The `ResultsView` filter and its two tests follow the tutorial's optional suggestion; the tutorial gives no code for them, so they're modeled on the `DetailView` versions.

### Part 6: Static files ✅

[Tutorial part 6](https://docs.djangoproject.com/en/6.1/intro/tutorial06/)

| File | What was done |
| --- | --- |
| `polls/static/polls/style.css` | New stylesheet: green question links and a background image in the top-left corner |
| `polls/static/polls/images/background.png` | Background image; this one is a generated placeholder of green diagonal stripes, since the tutorial says any image will do |
| `polls/templates/polls/index.html` | Loads the stylesheet with `{% load static %}` and `{% static 'polls/style.css' %}` |

With the server running, `/static/polls/style.css` and `/static/polls/images/background.png` are both served, and the 12 tests still pass.

### Part 7: Customizing the admin site ✅

[Tutorial part 7](https://docs.djangoproject.com/en/6.1/intro/tutorial07/)

| File | What was done |
| --- | --- |
| `polls/admin.py` | Added `QuestionAdmin`: the question form has a collapsible "Date information" section, and choices are edited inline in a table (`ChoiceInline`, three blank rows). The question list shows the text, publication date and "Published recently?", with a date filter and a search box. |
| `polls/models.py` | `was_published_recently()` uses `@admin.display`, so the list shows it as a ✔/✘ icon, sortable by date |
| `mysite/settings.py` | `TEMPLATES` `DIRS` now includes the project-level `templates/` folder |
| `templates/admin/base_site.html` | Copied from Django's admin templates, with the header changed to "Polls Administration" |

The admin home page, the question list, and the question add and edit pages all load with these changes, and the 12 tests still pass.

### Part 8 ⏳

Not started: [third-party packages](https://docs.djangoproject.com/en/6.1/intro/tutorial08/).

## Changes from the tutorial

- **Secret key in `.env`:** `SECRET_KEY` is loaded from a git-ignored `.env` file with [python-dotenv](https://pypi.org/project/python-dotenv/), so the key isn't published.
- **Not committed:** `.venv/`, `db.sqlite3` and `.env` are git-ignored, so each clone creates its own database and key.
