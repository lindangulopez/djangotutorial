from django.shortcuts import render

from .models import (
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
    MyCitizen,
    OrderedCitizen,
    Ox,
    Pizza,
    Place,
    Restaurant,
    Runner,
    ShirtOwner,
    Student,
    Supplier,
    VerbosePerson,
)


def index(request):
    context = {
        "albums": Album.objects.select_related("artist"),
        "shirt_owners": ShirtOwner.objects.all(),
        "runners": Runner.objects.all(),
        "fruits": Fruit.objects.order_by("name"),
        "verbose_fields": [
            VerbosePerson._meta.get_field(name)
            for name in ["first_name", "last_name", "favourite_album"]
        ],
        "manufacturers": Manufacturer.objects.prefetch_related("car_set"),
        "cars": Car.objects.select_related("manufacturer"),
        "pizzas": Pizza.objects.prefetch_related("toppings"),
        "groups": Group.objects.prefetch_related("members"),
        "memberships": Membership.objects.select_related("person", "group").order_by(
            "date_joined"
        ),
        "oxen": Ox.objects.all(),
        "ox_meta": Ox._meta,
        "citizens": Citizen.objects.order_by("birth_date"),
        "blogs": Blog.objects.all(),
        "students": Student.objects.all(),
        "student_table": Student._meta.db_table,
        "child_as": ChildA.objects.prefetch_related("toppings"),
        "child_bs": ChildB.objects.prefetch_related("toppings"),
        "places": Place.objects.select_related("restaurant", "supplier"),
        "restaurants": Restaurant.objects.all(),
        "suppliers": Supplier.objects.prefetch_related("customers"),
        "my_citizens": MyCitizen.objects.order_by("first_name"),
        "ordered_citizens": OrderedCitizen.objects.all(),
        "reviews": BookReview.objects.all(),
    }
    return render(request, "modelsdemo/index.html", context)
