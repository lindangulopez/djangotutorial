==================
django-polls usage
==================

Pages
-----

``/polls/``
    The five latest published questions, as links.

``/polls/<id>/``
    The voting form for one question.

``/polls/<id>/results/``
    Vote counts for each choice.

Adding questions and choices
----------------------------

Log in to the Django admin, open **Questions**, and add or edit a question.
Choices are edited in the table at the bottom of the question page.

Running the tests
-----------------

From a project that has ``django_polls`` installed::

    python manage.py test django_polls
