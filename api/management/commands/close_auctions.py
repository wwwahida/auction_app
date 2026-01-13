from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Max
from django.utils.timezone import now

from api.models import AuctionListing

class Command(BaseCommand):
    help = "Closes ended auctions and emails the winner."

    def add_arguments(self, parser):
        parser.add_argument("--listing-id", type=int, help="Only process a single AuctionListing id")


    def handle(self, *args, **options):
        ended = AuctionListing.objects.filter(
            finishTime__lte=now(),
            winner_notified=False,
        )

        count = 0

        for listing in ended:
            with transaction.atomic():
                # re-fetch with lock to avoid double processing
                listing = AuctionListing.objects.select_for_update().get(pk=listing.pk)
                if listing.winner_notified:
                    continue

                highest = listing.bids.aggregate(mx=Max("amount"))["mx"]

                # No bids → mark as processed so cron doesn’t keep re-checking
                if highest is None:
                    listing.winner_notified = True
                    listing.save(update_fields=["winner_notified"])
                    continue

                winning_bid = listing.bids.order_by("-amount", "id").first()
                if winning_bid is None:
                    listing.winner_notified = True
                    listing.save(update_fields=["winner_notified"])
                    continue

                winner = winning_bid.user
                listing.winner = winner
                listing.winner_notified = True
                listing.save(update_fields=["winner", "winner_notified"])

                send_mail(
                    subject=f"You won the auction: {listing.title}",
                    message=(
                        f"Hi {winner.username},\n\n"
                        f"Congrats — you won the auction for '{listing.title}'.\n"
                        f"Winning bid: £{winning_bid.amount}\n\n"
                        f"Please proceed to purchase the item.\n"
                    ),
                    from_email=None,  # uses DEFAULT_FROM_EMAIL
                    recipient_list=[winner.email],
                    fail_silently=False,
                )

                count += 1

        self.stdout.write(self.style.SUCCESS(f"Emailed winners for {count} auction(s)."))
