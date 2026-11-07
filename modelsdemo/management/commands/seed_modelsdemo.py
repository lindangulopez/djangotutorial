"""Fill the models demo with the sample data used in the Django models guide.

Run with ``python manage.py seed_modelsdemo``. It's safe to run more than once:
existing rows are reused, not duplicated.
"""

from datetime import date

from django.core.management.base import BaseCommand

from modelsdemo.models import (
    Album,
    Blog,
    BookReview,
    Car,
    ChildA,
    ChildB,
    Citizen,
    Fruit,
    Group,
    Manufacturer,
    Membership,
    Musician,
    Ox,
    Person,
    Pizza,
    Place,
    Restaurant,
    Runner,
    ShirtOwner,
    Student,
    Supplier,
    Topping,
    VerbosePerson,
)


class Command(BaseCommand):
    help = "Fill the models demo with sample data from the Django models guide."

    def handle(self, *args, **options):
        # Fields and many-to-one
        ella, _ = Musician.objects.get_or_create(
            first_name="Ella", last_name="Fitzgerald", defaults={"instrument": "Voice"}
        )
        album, _ = Album.objects.get_or_create(
            artist=ella,
            name="Ella and Louis",
            defaults={"release_date": date(1956, 10, 1), "num_stars": 5},
        )
        VerbosePerson.objects.get_or_create(
            first_name="Louis", last_name="Armstrong", defaults={"favourite_album": album}
        )

        # Choices
        ShirtOwner.objects.get_or_create(name="Fred Flintstone", defaults={"shirt_size": "L"})
        Runner.objects.get_or_create(name="Usain", defaults={"medal": Runner.MedalType.GOLD})
        Runner.objects.get_or_create(name="Florence", defaults={"medal": Runner.MedalType.SILVER})

        # primary_key
        Fruit.objects.update_or_create(name="Apple", defaults={"color": "Red"})
        Fruit.objects.update_or_create(name="Pear", defaults={"color": "Green"})

        maker, _ = Manufacturer.objects.get_or_create(name="Citroën")
        for name in ["2CV", "DS"]:
            Car.objects.get_or_create(manufacturer=maker, name=name)

        # Many-to-many
        toppings = [Topping.objects.get_or_create(name=n)[0] for n in ["Cheese", "Tomato", "Basil"]]
        pizza, _ = Pizza.objects.get_or_create(name="Margherita")
        pizza.toppings.set(toppings)

        # Many-to-many with a through model: the Beatles
        beatles, _ = Group.objects.get_or_create(name="The Beatles")
        for name, joined, reason in [
            ("John Lennon", date(1957, 7, 6), "Founded the band."),
            ("Paul McCartney", date(1960, 8, 1), "Wanted to form a band."),
            ("George Harrison", date(1958, 2, 6), "Played guitar."),
            ("Ringo Starr", date(1962, 8, 16), "Needed a new drummer."),
        ]:
            person, _ = Person.objects.get_or_create(name=name)
            Membership.objects.get_or_create(
                person=person,
                group=beatles,
                defaults={"date_joined": joined, "invite_reason": reason},
            )

        # Meta options
        for length in [40, 15, 25]:
            Ox.objects.get_or_create(horn_length=length)

        # Model methods and proxies
        for first, last, born in [
            ("Grace", "Hopper", date(1906, 12, 9)),
            ("Margaret", "Hamilton", date(1936, 8, 17)),
            ("Linus", "Torvalds", date(1969, 12, 28)),
            ("Steve", "Wozniak", date(1950, 8, 11)),
        ]:
            Citizen.objects.get_or_create(
                first_name=first, last_name=last, defaults={"birth_date": born}
            )

        # save() overrides; "Yoko Ono's blog" is refused by Blog.save()
        if not Blog.objects.filter(name="My Django Notes").exists():
            Blog.objects.create(name="My Django Notes", tagline="Learning the ORM")
        Blog(name="Yoko Ono's blog").save()

        # Abstract base classes
        Student.objects.get_or_create(name="Zoë", defaults={"age": 20, "home_group": "B1"})
        Student.objects.get_or_create(name="Adam", defaults={"age": 21, "home_group": "A2"})
        if not ChildA.objects.exists():
            ChildA.objects.create().toppings.set(toppings[:2])
        if not ChildB.objects.exists():
            ChildB.objects.create().toppings.set(toppings[2:])

        # Multi-table inheritance
        cafe = Restaurant.objects.filter(name="Bob's Cafe").first()
        if cafe is None:
            cafe = Restaurant.objects.create(
                name="Bob's Cafe", address="1 Main Street", serves_hot_dogs=True
            )
        Place.objects.get_or_create(name="Town Hall", defaults={"address": "2 Main Street"})
        supplier = Supplier.objects.filter(name="Fresh Foods").first()
        if supplier is None:
            supplier = Supplier.objects.create(name="Fresh Foods", address="3 Market Road")
        supplier.customers.add(cafe)

        # Multiple inheritance
        if not BookReview.objects.exists():
            BookReview.objects.create(title="Dune", headline="A desert classic")

        if options["verbosity"]:
            self.stdout.write(self.style.SUCCESS("Models demo data is ready."))
