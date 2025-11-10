from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import Recipe


# PUBLIC_INTERFACE
class Command(BaseCommand):
    """Seed the database with demo users and recipes for local testing."""

    help = "Seeds demo users and recipes."

    def handle(self, *args, **options):
        User = get_user_model()
        user, _ = User.objects.get_or_create(username="demo")
        if not user.has_usable_password():
            user.set_password("DemoPassword123!")
            user.save()
        created = 0
        for i in range(1, 6):
            title = f"Demo Recipe {i}"
            obj, was_created = Recipe.objects.get_or_create(
                title=title,
                defaults={
                    "description": "A tasty demo recipe.",
                    "ingredients": "Sugar\nSpice\nEverything Nice",
                    "steps": "Combine ingredients.\nCook well.\nServe hot.",
                    "author": user,
                },
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Seed complete. Created {created} recipes (user=demo)."))
