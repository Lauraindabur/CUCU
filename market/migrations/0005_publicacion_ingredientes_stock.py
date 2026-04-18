from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("market", "0004_backfill_publicacion_ubicacion_medellin"),
    ]

    operations = [
        migrations.AddField(
            model_name="publicacion",
            name="ingredientes",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="publicacion",
            name="stock",
            field=models.PositiveIntegerField(default=10),
        ),
    ]