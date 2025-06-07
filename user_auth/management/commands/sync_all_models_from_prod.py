from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction

class Command(BaseCommand):
    help = "Sync all model data from production PostgreSQL to local SQLite"

    def handle(self, *args, **kwargs):
        all_models = apps.get_models()
        skipped = []
        
        for model in all_models:
            model_name = f"{model._meta.app_label}.{model.__name__}"
            self.stdout.write(f"\n📦 Syncing {model_name}...")

            try:
                # Pull from prod
                records = model.objects.using('prod').all()

                # Insert into default DB
                with transaction.atomic(using='default'):
                    for record in records:
                        record.pk = None
                        record.save(using='default')

                self.stdout.write(f"✅ Synced {records.count()} records.")
            except Exception as e:
                skipped.append((model_name, str(e)))
                self.stdout.write(f"❌ Skipped {model_name}: {e}")

        self.stdout.write("\n✅✅ All done.\n")

        if skipped:
            self.stdout.write("⚠️ The following models failed to sync:")
            for model, reason in skipped:
                self.stdout.write(f"- {model}: {reason}")
