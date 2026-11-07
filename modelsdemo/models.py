"""
Examples from the Django "Models" topic guide:
https://docs.djangoproject.com/en/6.1/topics/db/models/

Each section below matches a heading in the guide. Where the guide reuses a
model name (it has several different ``Person`` models), the model is renamed
here so they can live in one app; the docstring says which example it is.
"""

import datetime

from django.db import models
from django.utils.text import slugify


# --- Quick example / Fields ---------------------------------------------------


class Musician(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    instrument = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Album(models.Model):
    artist = models.ForeignKey(Musician, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    release_date = models.DateField()
    num_stars = models.IntegerField()

    def __str__(self):
        return self.name


# --- Field options: choices ---------------------------------------------------


class ShirtOwner(models.Model):
    """The guide's ``Person`` with ``SHIRT_SIZES`` choices."""

    SHIRT_SIZES = {
        "S": "Small",
        "M": "Medium",
        "L": "Large",
    }
    name = models.CharField(max_length=60)
    shirt_size = models.CharField(max_length=1, choices=SHIRT_SIZES)

    def __str__(self):
        return self.name


class Runner(models.Model):
    MedalType = models.TextChoices("MedalType", "GOLD SILVER BRONZE")
    name = models.CharField(max_length=60)
    medal = models.CharField(blank=True, choices=MedalType, max_length=10)

    def __str__(self):
        return self.name


# --- Field options: primary_key -----------------------------------------------


class Fruit(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    color = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# --- Verbose field names ------------------------------------------------------


class VerbosePerson(models.Model):
    """The guide's verbose-name examples, on one model."""

    first_name = models.CharField("person's first name", max_length=30)
    last_name = models.CharField(max_length=30)
    favourite_album = models.ForeignKey(
        Album,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="the related album",
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# --- Relationships: many-to-one -----------------------------------------------


class Manufacturer(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Car(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# --- Relationships: many-to-many ----------------------------------------------


class Topping(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Pizza(models.Model):
    name = models.CharField(max_length=50)
    toppings = models.ManyToManyField(Topping)

    def __str__(self):
        return self.name


# --- Extra fields on many-to-many relationships -------------------------------


class Person(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=128)
    members = models.ManyToManyField(Person, through="Membership")

    def __str__(self):
        return self.name


class Membership(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date_joined = models.DateField()
    invite_reason = models.CharField(max_length=64)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["person", "group"], name="unique_person_group"
            )
        ]

    def __str__(self):
        return f"{self.person} in {self.group}"


# --- Meta options -------------------------------------------------------------


class Ox(models.Model):
    horn_length = models.IntegerField()

    class Meta:
        ordering = ["horn_length"]
        verbose_name_plural = "oxen"

    def __str__(self):
        return f"Ox with {self.horn_length} cm horns"


# --- Model methods ------------------------------------------------------------


class Citizen(models.Model):
    """The guide's ``Person`` with ``baby_boomer_status()`` and ``full_name``.

    ``birth_date`` is optional here so the proxy-model example below can
    create a person from a first name alone, as the guide does.
    """

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def baby_boomer_status(self):
        "Returns the person's baby-boomer status."
        if self.birth_date is None:
            return "Unknown"
        if self.birth_date < datetime.date(1945, 8, 1):
            return "Pre-boomer"
        elif self.birth_date < datetime.date(1965, 1, 1):
            return "Baby boomer"
        else:
            return "Post-boomer"

    @property
    def full_name(self):
        "Returns the person's full name."
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.full_name


# --- Overriding predefined model methods --------------------------------------


class Blog(models.Model):
    """Combines the guide's ``save()`` overrides: refuse one name, set a slug."""

    name = models.CharField(max_length=100)
    tagline = models.TextField(blank=True)
    slug = models.TextField(blank=True)

    def save(self, **kwargs):
        if self.name == "Yoko Ono's blog":
            return  # Yoko shall never have her own blog!
        self.slug = slugify(self.name)
        if (
            update_fields := kwargs.get("update_fields")
        ) is not None and "name" in update_fields:
            kwargs["update_fields"] = {"slug"}.union(update_fields)
        super().save(**kwargs)  # Call the "real" save() method.

    def __str__(self):
        return self.name


# --- Abstract base classes ----------------------------------------------------


class CommonInfo(models.Model):
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()

    class Meta:
        abstract = True
        ordering = ["name"]


class Student(CommonInfo):
    home_group = models.CharField(max_length=5)

    class Meta(CommonInfo.Meta):
        db_table = "student_info"

    def __str__(self):
        return self.name


class ToppingCollection(models.Model):
    """The guide's abstract ``Base`` with ``%(app_label)s`` and ``%(class)s``."""

    toppings = models.ManyToManyField(
        Topping,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
    )

    class Meta:
        abstract = True


class ChildA(ToppingCollection):
    pass


class ChildB(ToppingCollection):
    pass


# --- Multi-table inheritance --------------------------------------------------


class Place(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=80)

    def __str__(self):
        return self.name


class Restaurant(Place):
    serves_hot_dogs = models.BooleanField(default=False)
    serves_pizza = models.BooleanField(default=False)


class Supplier(Place):
    customers = models.ManyToManyField(Place, related_name="provider")


# --- Proxy models -------------------------------------------------------------


class MyCitizen(Citizen):
    """The guide's ``MyPerson`` proxy."""

    class Meta:
        proxy = True

    def greeting(self):
        return f"Hello, {self.first_name}!"


class OrderedCitizen(Citizen):
    """The guide's ``OrderedPerson`` proxy."""

    class Meta:
        ordering = ["last_name"]
        proxy = True


# --- Multiple inheritance -----------------------------------------------------


class Piece(models.Model):
    pass


class Article(Piece):
    article_piece = models.OneToOneField(
        Piece, on_delete=models.CASCADE, parent_link=True
    )
    headline = models.CharField(max_length=100)


class Book(Piece):
    book_piece = models.OneToOneField(Piece, on_delete=models.CASCADE, parent_link=True)
    title = models.CharField(max_length=100)


class BookReview(Book, Article):
    pass
