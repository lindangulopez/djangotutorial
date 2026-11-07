"""
Tests that replay the examples in the Django "Models" topic guide:
https://docs.djangoproject.com/en/6.1/topics/db/models/
"""

import datetime
from datetime import date

from django.core.management import call_command
from django.db import IntegrityError, connection
from django.test import TestCase
from django.urls import reverse

from .models import (
    Album,
    Article,
    Blog,
    Book,
    BookReview,
    Car,
    ChildA,
    ChildB,
    Citizen,
    CommonInfo,
    Fruit,
    Group,
    Manufacturer,
    Membership,
    Musician,
    MyCitizen,
    OrderedCitizen,
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


class FieldTests(TestCase):
    def test_foreign_key_and_fields(self):
        musician = Musician.objects.create(
            first_name="Ella", last_name="Fitzgerald", instrument="Voice"
        )
        Album.objects.create(
            artist=musician,
            name="Ella and Louis",
            release_date=date(1956, 10, 1),
            num_stars=5,
        )
        self.assertEqual(musician.album_set.get().name, "Ella and Louis")

    def test_choices_dictionary(self):
        p = ShirtOwner(name="Fred Flintstone", shirt_size="L")
        p.save()
        self.assertEqual(p.shirt_size, "L")
        self.assertEqual(p.get_shirt_size_display(), "Large")

    def test_text_choices_enum(self):
        self.assertEqual(Runner.MedalType.choices[0], ("GOLD", "Gold"))
        runner = Runner.objects.create(name="Usain", medal=Runner.MedalType.GOLD)
        self.assertEqual(runner.get_medal_display(), "Gold")

    def test_primary_key_change_creates_new_row(self):
        fruit = Fruit.objects.create(name="Apple", color="Green")
        fruit.name = "Pear"
        fruit.save()
        self.assertEqual(
            list(Fruit.objects.order_by("name").values_list("name", "color")),
            [("Apple", "Green"), ("Pear", "Green")],
        )

    def test_saving_existing_primary_key_updates_row(self):
        Fruit.objects.create(name="Apple", color="Green")
        Fruit.objects.create(name="Pear", color="Green")
        pear = Fruit.objects.get(name="Pear")
        pear.name = "Apple"
        pear.color = "Red"
        pear.save()
        self.assertEqual(
            list(Fruit.objects.order_by("name").values_list("name", "color")),
            [("Apple", "Red"), ("Pear", "Green")],
        )

    def test_automatic_primary_key(self):
        field = Musician._meta.pk
        self.assertEqual(field.name, "id")
        self.assertEqual(field.get_internal_type(), "BigAutoField")

    def test_verbose_names(self):
        meta = VerbosePerson._meta
        self.assertEqual(meta.get_field("first_name").verbose_name, "person's first name")
        self.assertEqual(meta.get_field("last_name").verbose_name, "last name")
        self.assertEqual(
            meta.get_field("favourite_album").verbose_name, "the related album"
        )


class RelationshipTests(TestCase):
    def test_many_to_one(self):
        maker = Manufacturer.objects.create(name="Citroën")
        Car.objects.create(manufacturer=maker, name="2CV")
        Car.objects.create(manufacturer=maker, name="DS")
        self.assertEqual(
            list(maker.car_set.order_by("name").values_list("name", flat=True)),
            ["2CV", "DS"],
        )

    def test_many_to_many(self):
        cheese = Topping.objects.create(name="Cheese")
        basil = Topping.objects.create(name="Basil")
        pizza = Pizza.objects.create(name="Margherita")
        pizza.toppings.add(cheese, basil)
        self.assertEqual(pizza.toppings.count(), 2)
        self.assertEqual(list(cheese.pizza_set.all()), [pizza])


class ThroughModelTests(TestCase):
    """The Beatles example from "Extra fields on many-to-many relationships"."""

    def setUp(self):
        self.ringo = Person.objects.create(name="Ringo Starr")
        self.paul = Person.objects.create(name="Paul McCartney")
        self.beatles = Group.objects.create(name="The Beatles")
        Membership(
            person=self.ringo,
            group=self.beatles,
            date_joined=date(1962, 8, 16),
            invite_reason="Needed a new drummer.",
        ).save()
        Membership.objects.create(
            person=self.paul,
            group=self.beatles,
            date_joined=date(1960, 8, 1),
            invite_reason="Wanted to form a band.",
        )

    def test_members_and_reverse(self):
        self.assertEqual(list(self.beatles.members.all()), [self.ringo, self.paul])
        self.assertEqual(list(self.ringo.group_set.all()), [self.beatles])

    def test_add_create_set_with_through_defaults(self):
        john = Person.objects.create(name="John Lennon")
        self.beatles.members.add(
            john, through_defaults={"date_joined": date(1960, 8, 1)}
        )
        george = self.beatles.members.create(
            name="George Harrison", through_defaults={"date_joined": date(1960, 8, 1)}
        )
        self.beatles.members.set(
            [john, self.paul, self.ringo, george],
            through_defaults={"date_joined": date(1960, 8, 1)},
        )
        self.assertEqual(self.beatles.members.count(), 4)

    def test_unique_constraint_blocks_duplicate_membership(self):
        with self.assertRaises(IntegrityError):
            Membership.objects.create(
                person=self.ringo,
                group=self.beatles,
                date_joined=date(1968, 9, 4),
                invite_reason="You've been gone for a month and we miss you.",
            )

    def test_remove_and_clear_delete_memberships(self):
        self.beatles.members.remove(self.ringo)
        self.assertEqual(list(self.beatles.members.all()), [self.paul])
        self.beatles.members.clear()
        self.assertFalse(Membership.objects.exists())

    def test_queries_across_the_relationship(self):
        self.assertEqual(
            list(Group.objects.filter(members__name__startswith="Paul")),
            [self.beatles],
        )
        self.assertEqual(
            list(
                Person.objects.filter(
                    group__name="The Beatles",
                    membership__date_joined__gt=date(1961, 1, 1),
                )
            ),
            [self.ringo],
        )

    def test_reading_the_intermediate_model(self):
        membership = Membership.objects.get(group=self.beatles, person=self.ringo)
        self.assertEqual(membership.date_joined, datetime.date(1962, 8, 16))
        membership = self.ringo.membership_set.get(group=self.beatles)
        self.assertEqual(membership.invite_reason, "Needed a new drummer.")


class MetaAndMethodTests(TestCase):
    def test_meta_ordering_and_plural_name(self):
        Ox.objects.create(horn_length=30)
        Ox.objects.create(horn_length=10)
        self.assertEqual(
            list(Ox.objects.values_list("horn_length", flat=True)), [10, 30]
        )
        self.assertEqual(Ox._meta.verbose_name_plural, "oxen")

    def test_model_method_and_property(self):
        citizen = Citizen(
            first_name="Grace", last_name="Hopper", birth_date=date(1906, 12, 9)
        )
        self.assertEqual(citizen.baby_boomer_status(), "Pre-boomer")
        self.assertEqual(citizen.full_name, "Grace Hopper")
        self.assertEqual(
            Citizen(birth_date=date(1950, 1, 1)).baby_boomer_status(), "Baby boomer"
        )
        self.assertEqual(
            Citizen(birth_date=date(1990, 1, 1)).baby_boomer_status(), "Post-boomer"
        )

    def test_save_override_sets_slug(self):
        blog = Blog.objects.create(name="My Django Notes")
        self.assertEqual(blog.slug, "my-django-notes")
        blog.name = "Renamed Notes"
        blog.save(update_fields=["name"])
        blog.refresh_from_db()
        self.assertEqual(blog.slug, "renamed-notes")

    def test_save_override_can_refuse(self):
        Blog.objects.create(name="Yoko Ono's blog")
        self.assertFalse(Blog.objects.exists())


class InheritanceTests(TestCase):
    def test_abstract_base_class(self):
        self.assertTrue(CommonInfo._meta.abstract)
        self.assertFalse(hasattr(CommonInfo, "objects"))
        Student.objects.create(name="Zoë", age=20, home_group="B1")
        Student.objects.create(name="Adam", age=21, home_group="A2")
        self.assertEqual(
            list(Student.objects.values_list("name", flat=True)), ["Adam", "Zoë"]
        )
        self.assertEqual(Student._meta.db_table, "student_info")
        self.assertIn("student_info", connection.introspection.table_names())

    def test_related_name_placeholders(self):
        cheese = Topping.objects.create(name="Cheese")
        ChildA.objects.create().toppings.add(cheese)
        ChildB.objects.create().toppings.add(cheese)
        self.assertEqual(cheese.modelsdemo_childa_related.count(), 1)
        self.assertEqual(cheese.modelsdemo_childb_related.count(), 1)
        self.assertEqual(Topping.objects.filter(modelsdemo_childas__isnull=False).count(), 1)

    def test_multi_table_inheritance(self):
        Restaurant.objects.create(name="Bob's Cafe", address="1 Main Street")
        self.assertEqual(Place.objects.filter(name="Bob's Cafe").count(), 1)
        self.assertEqual(Restaurant.objects.filter(name="Bob's Cafe").count(), 1)
        place = Place.objects.get(name="Bob's Cafe")
        self.assertIsInstance(place.restaurant, Restaurant)
        self.assertEqual(Restaurant._meta.pk.name, "place_ptr")

    def test_place_that_is_not_a_restaurant(self):
        place = Place.objects.create(name="Town Hall", address="2 Main Street")
        with self.assertRaises(Restaurant.DoesNotExist):
            place.restaurant

    def test_reverse_relation_needs_related_name(self):
        cafe = Restaurant.objects.create(name="Bob's Cafe", address="1 Main Street")
        supplier = Supplier.objects.create(name="Fresh Foods", address="3 Market Road")
        supplier.customers.add(cafe)
        self.assertEqual(list(cafe.provider.all()), [supplier])

    def test_proxy_models_share_the_table(self):
        Citizen.objects.create(first_name="foobar")
        proxy = MyCitizen.objects.get(first_name="foobar")
        self.assertIsInstance(proxy, MyCitizen)
        self.assertEqual(proxy.greeting(), "Hello, foobar!")
        self.assertEqual(MyCitizen._meta.db_table, Citizen._meta.db_table)

    def test_proxy_model_ordering(self):
        Citizen.objects.create(first_name="Ada", last_name="Lovelace")
        Citizen.objects.create(first_name="Alan", last_name="Turing")
        Citizen.objects.create(first_name="Grace", last_name="Hopper")
        self.assertEqual(
            list(OrderedCitizen.objects.values_list("last_name", flat=True)),
            ["Hopper", "Lovelace", "Turing"],
        )

    def test_multiple_inheritance(self):
        review = BookReview.objects.create(title="Dune", headline="A desert classic")
        self.assertEqual(Book.objects.get().title, "Dune")
        self.assertEqual(Article.objects.get().headline, "A desert classic")
        self.assertEqual(review.book_piece_id, review.article_piece_id)


class DemoPageTests(TestCase):
    def test_empty_page(self):
        response = self.client.get(reverse("modelsdemo:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Models demo")

    def test_seeded_page(self):
        call_command("seed_modelsdemo", verbosity=0)
        response = self.client.get(reverse("modelsdemo:index"))
        self.assertContains(response, "The Beatles")
        self.assertContains(response, "Needed a new drummer.")
        self.assertContains(response, "Baby boomer")

    def test_seed_is_repeatable(self):
        call_command("seed_modelsdemo", verbosity=0)
        call_command("seed_modelsdemo", verbosity=0)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(Membership.objects.count(), 4)
