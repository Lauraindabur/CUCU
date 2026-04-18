from __future__ import annotations

import sqlite3
from pathlib import Path

from ..models import Payment


class SQLitePaymentRepository:
    def __init__(self, database_path: str) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS payments (
                    id TEXT PRIMARY KEY,
                    pedido_id TEXT NOT NULL,
                    usuario_id INTEGER NOT NULL,
                    monto REAL NOT NULL,
                    moneda TEXT NOT NULL,
                    metodo_pago TEXT NOT NULL,
                    estado TEXT NOT NULL,
                    mensaje_estado TEXT NOT NULL,
                    creado_en TEXT NOT NULL,
                    actualizado_en TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def create(self, payment: Payment) -> Payment:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO payments (
                    id,
                    pedido_id,
                    usuario_id,
                    monto,
                    moneda,
                    metodo_pago,
                    estado,
                    mensaje_estado,
                    creado_en,
                    actualizado_en
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payment.id,
                    payment.pedido_id,
                    payment.usuario_id,
                    payment.monto,
                    payment.moneda,
                    payment.metodo_pago,
                    payment.estado,
                    payment.mensaje_estado,
                    payment.creado_en,
                    payment.actualizado_en,
                ),
            )
            connection.commit()
        return payment

    def get_by_id(self, payment_id: str) -> Payment | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    pedido_id,
                    usuario_id,
                    monto,
                    moneda,
                    metodo_pago,
                    estado,
                    mensaje_estado,
                    creado_en,
                    actualizado_en
                FROM payments
                WHERE id = ?
                """,
                (payment_id,),
            ).fetchone()

        if row is None:
            return None

        return self._map_row(row)

    def update_status(
        self,
        payment_id: str,
        *,
        estado: str,
        mensaje_estado: str,
        actualizado_en: str,
    ) -> Payment | None:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE payments
                SET estado = ?, mensaje_estado = ?, actualizado_en = ?
                WHERE id = ?
                """,
                (estado, mensaje_estado, actualizado_en, payment_id),
            )
            connection.commit()

        if cursor.rowcount == 0:
            return None

        return self.get_by_id(payment_id)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _map_row(row: sqlite3.Row) -> Payment:
        return Payment(
            id=row["id"],
            pedido_id=row["pedido_id"],
            usuario_id=row["usuario_id"],
            monto=row["monto"],
            moneda=row["moneda"],
            metodo_pago=row["metodo_pago"],
            estado=row["estado"],
            mensaje_estado=row["mensaje_estado"],
            creado_en=row["creado_en"],
            actualizado_en=row["actualizado_en"],
        )
