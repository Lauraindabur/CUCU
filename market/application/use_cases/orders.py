from __future__ import annotations

from ...domain.services import AcceptOrderService, OrderService


class CreateOrderUseCase:
    def __init__(self, *, order_service: OrderService | None = None):
        self._order_service = order_service or OrderService()

    def execute(self, *, user, **payload):
        return self._order_service.create_order(user=user, **payload)


class GetOrderForUserUseCase:
    def __init__(self, *, order_service: OrderService | None = None):
        self._order_service = order_service or OrderService()

    def execute(self, *, user, pedido_id: int):
        return self._order_service.get_order_for_user(user=user, pedido_id=pedido_id)


class MarkOrderDeliveredUseCase:
    def __init__(self, *, order_service: OrderService | None = None):
        self._order_service = order_service or OrderService()

    def execute(self, *, user, pedido_id: int):
        return self._order_service.mark_order_delivered(user=user, pedido_id=pedido_id)


class ListOrdersForUserUseCase:
    def __init__(self, *, order_service: OrderService | None = None):
        self._order_service = order_service or OrderService()

    def execute(self, *, user):
        return self._order_service.list_orders_for_user(user=user)


class AcceptOrderUseCase:
    def __init__(self, *, accept_order_service: AcceptOrderService | None = None):
        self._accept_order_service = accept_order_service or AcceptOrderService()

    def execute(self, *, user, pedido_id: int):
        return self._accept_order_service.accept_order(user=user, pedido_id=pedido_id)