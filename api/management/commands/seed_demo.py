from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import AuctionListing, User
from pathlib import Path
from django.conf import settings
from django.core.files import File



DEMO_USERS = [
    {
        "username": "testuser1",
        "email": "testuser1@auction.test",
        "password": "Password123!",
        "firstName": "Aisha",
        "lastName": "Khan",
        "dob": date(2001, 2, 14),

    },
    {
        "username": "testuser2",
        "email": "testuser2@auction.test",
        "password": "Password123!",
        "firstName": "Ben",
        "lastName": "Taylor",
        "dob": date(2000, 6, 3),
    },
    {
        "username": "testuser3",
        "email": "testuser3@auction.test",
        "password": "Password123!",
        "firstName": "Chloe",
        "lastName": "Wright",
        "dob": date(2002, 11, 22),
    },
    {
        "username": "testuser4",
        "email": "testuser4@auction.test",
        "password": "Password123!",
        "firstName": "Daniel",
        "lastName": "Singh",
        "dob": date(1999, 9, 9),
    },
    {
        "username": "testuser5",
        "email": "testuser5@auction.test",
        "password": "Password123!",
        "firstName": "Emma",
        "lastName": "Jones",
        "dob": date(2001, 1, 30),
    },
]

DEMO_LISTINGS = [
    {
        "title": "Oak Coffee Table",
        "description": "Solid oak coffee table. Minor surface scuffs, very sturdy.",
        "startingPrice": Decimal("25.00"),
        "days_from_now": 7,
        "owner": "testuser1",
        "image": "oak coffee table.jpg",
    },
    {
        "title": "Dining Table (6-seater)",
        "description": "Large dining table. Seats 6. A couple of marks but good condition.",
        "startingPrice": Decimal("60.00"),
        "days_from_now": 10,
        "owner": "testuser2",
        "image": "dining table.jpeg",
    },
    {
        "title": "Desk Lamp - Adjustable",
        "description": "LED desk lamp with adjustable arm and brightness modes.",
        "startingPrice": Decimal("8.50"),
        "days_from_now": 5,
        "owner": "testuser3",
        "image": "desk lamp.jpeg",
    },
    {
        "title": "Bluetooth Speaker",
        "description": "Portable speaker with good bass. Battery lasts ~8 hours.",
        "startingPrice": Decimal("15.00"),
        "days_from_now": 6,
        "owner": "testuser4",
        "image": "speaker.jpeg",
    },
    {
        "title": "Gaming Chair",
        "description": "Comfortable chair, reclines fully. Slight wear on armrests.",
        "startingPrice": Decimal("35.00"),
        "days_from_now": 9,
        "owner": "testuser5",
        "image": "chair.jpeg",
    },
    {
        "title": "Mechanical Keyboard",
        "description": "Mechanical keyboard (blue switches). Clean and fully working.",
        "startingPrice": Decimal("20.00"),
        "days_from_now": 8,
        "owner": "testuser1",
        "image": "keyboard.jpeg",
    },
    {
        "title": "Wireless Mouse",
        "description": "Ergonomic wireless mouse. Includes USB receiver.",
        "startingPrice": Decimal("7.00"),
        "days_from_now": 4,
        "owner": "testuser2",
        "image": "mouse.jpeg",
    },
    {
        "title": "Side Table (Small)",
        "description": "Small side table perfect for bedside use. Light scratches.",
        "startingPrice": Decimal("12.00"),
        "days_from_now": 7,
        "owner": "testuser3",
        "image": "bedside table.jpeg",
    },
    {
        "title": "Coffee Machine",
        "description": "Filter coffee machine. Works well, comes with reusable filter.",
        "startingPrice": Decimal("18.00"),
        "days_from_now": 11,
        "owner": "testuser4",
        "image": "coffee machine.jpeg",
    },
    {
        "title": "Backpack - 30L",
        "description": "30L backpack, multiple compartments. Great for commuting.",
        "startingPrice": Decimal("10.00"),
        "days_from_now": 6,
        "owner": "testuser5",
        "image": "backpack.jpeg",
    },
]


class Command(BaseCommand):
    help = "Create demo users + auction listings for local development."

    def handle(self, *args, **options):
        # create demo users + listings
        user_map: dict[str, User] = {}

        for u in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=u["username"],
                defaults={
                    "email": u["email"],
                    "firstName": u["firstName"],
                    "lastName": u["lastName"],
                    "dob": u["dob"],
                },
            )

            # Ensure fields + password are set even if user already existed
            user.email = u["email"]
            user.firstName = u["firstName"]
            user.lastName = u["lastName"]
            user.dob = u["dob"]
            user.set_password(u["password"])
            user.save()

            user_map[u["username"]] = user
            msg = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{msg} user: {u['username']}"))

        # Create demo listings (idempotent: won’t duplicate)
        now_dt = timezone.now()
        created_count = 0

        for l in DEMO_LISTINGS:
            owner = user_map[l["owner"]]
            finish_time = now_dt + timedelta(days=int(l["days_from_now"]))

            listing, created = AuctionListing.objects.get_or_create(
                title=l["title"],
                user=owner,
                defaults={
                    "description": l["description"],
                    "startingPrice": l["startingPrice"],
                    "finishTime": finish_time,
                },
            )

            if created:
                created_count += 1

        seed_dir = Path(settings.BASE_DIR) / "api" / "seed_images"

        for l in DEMO_LISTINGS:
            owner = user_map[l["owner"]]
            finish_time = now_dt + timedelta(days=int(l["days_from_now"]))

            listing, created = AuctionListing.objects.get_or_create(
                title=l["title"],
                user=owner,
                defaults={
                    "description": l["description"],
                    "startingPrice": l["startingPrice"],
                    "finishTime": finish_time,
                },
            )

            # Attach picture if listing is new OR missing a picture
            image_name = l.get("image")
            if image_name and (created or not listing.picture):
                img_path = seed_dir / image_name
                if img_path.exists():
                    with img_path.open("rb") as f:
                        listing.picture.save(img_path.name, File(f), save=False)
                    listing.save()
                else:
                    self.stdout.write(self.style.WARNING(f"Missing seed image: {img_path}"))
            

        self.stdout.write(self.style.SUCCESS(f"Demo listings created: {created_count}"))
        self.stdout.write(self.style.SUCCESS("✅ seed_demo complete"))
