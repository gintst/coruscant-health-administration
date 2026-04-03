from django.db import migrations, models


def copy_completed_to_status(apps, schema_editor):
    Order = apps.get_model("core", "Order")
    for order in Order.objects.all():
        order.status = "completed" if getattr(order, "completed", False) else "pending"
        order.result = ""
        order.completed_at = None
        order.save(update_fields=["status", "result", "completed_at"])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_emergencyservice_department_administrator"),
    ]

    operations = [
        migrations.AddField(
            model_name="patient",
            name="is_approved",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="doctor",
            name="is_approved",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="document",
            name="original_name",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="order",
            name="completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="result",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("in_progress", "In progress"),
                    ("completed", "Completed"),
                ],
                default="pending",
                max_length=16,
            ),
        ),
        migrations.RunPython(copy_completed_to_status, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="order",
            name="completed",
        ),
    ]
