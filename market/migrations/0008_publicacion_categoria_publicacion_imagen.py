from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("market", "0007_publicacion_maximo_por_venta"),
    ]

    operations = [
        migrations.AddField(
            model_name="publicacion",
            name="categoria",
            field=models.CharField(blank=True, default="", max_length=20),
        ),
        migrations.AddField(
            model_name="publicacion",
            name="imagen",
            field=models.FileField(blank=True, null=True, upload_to="publicaciones/"),
        ),
    ]