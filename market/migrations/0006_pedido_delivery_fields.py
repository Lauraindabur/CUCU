from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("market", "0005_publicacion_ingredientes_stock"),
    ]

    operations = [
        migrations.AddField(
            model_name="pedido",
            name="direccion_entrega",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="pedido",
            name="direccion_entrega_detalles",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="pedido",
            name="direccion_entrega_latitud",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name="pedido",
            name="direccion_entrega_longitud",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
    ]