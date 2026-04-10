from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("market", "0006_pedido_delivery_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="publicacion",
            name="maximo_por_venta",
            field=models.PositiveIntegerField(default=5),
        ),
    ]