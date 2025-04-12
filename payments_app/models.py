# import uuid
# import logging
# from decimal import Decimal
#
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from rest_framework.exceptions import ValidationError
# from django.contrib.auth import get_user_model
# from django_fsm import FSMField, transition
#
# from goods_app.models import Product
# from .tasks import notify_user_task
# from .services.payment_currency import PaymentCurrency
# from orders_app.models import Order
#
# User = get_user_model()
#
# logger = logging.getLogger(__name__)
#
#
# class PaymentMethod(models.TextChoices):
#     FONDY = 'fondy', _('Fondy')
#
#
# class PaymentStatus(models.TextChoices):
#     PENDING = 'pending', _('Ожидается')
#     PAID = 'paid', _('Оплачен')
#     PARTIALLY_PAID = 'partially_paid', _('Частично оплачен')
#     COMPLETED = 'completed', _('Завершен')
#     FAILED = 'failed', _('Неудача')
#     REFUNDED = 'refunded', _('Возвращен')
#     CANCELLED = 'cancelled', _('Отменен')
#     DISPUTED = 'disputed', _('Оспаривается')
#     # EXPIRED = 'expired', _('Истек срок действия')
#
#
#
# class Payment(models.Model):
#     transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name=_('Заказ'))
#     amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Сумма'))
#     payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.FONDY, verbose_name=_('Метод оплаты'))
#     status = FSMField(default=PaymentStatus.PENDING, choices=PaymentStatus.choices, verbose_name=_('Статус платежа'))
#     transaction_error = models.TextField(null=True, blank=True, verbose_name=_('Ошибка транзакции'))
#     currency = models.CharField(max_length=3, choices=PaymentCurrency.choices, verbose_name=_('Валюта'), default=PaymentCurrency.USD)
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлено'))
#
#     class Meta:
#         db_table = 'payment'
#         verbose_name = _('Оплата')
#         verbose_name_plural = _('Оплаты')
#
#         indexes = [
#             models.Index(fields=['transaction_id']),
#             models.Index(fields=['status']),
#             models.Index(fields=['user']),
#         ]
#
#     def __str__(self) -> str:
#         return f'Платеж {self.transaction_id} - {self.status}'
#
#     def update_total_price(self) -> None:
#         if self.order and self.order.total_price:
#             self.amount = self.order.total_price
#             self.save()
#
#     def notify_user(self, message: str) -> None:
#         """Уведомление пользователя о статусе платежа."""
#         notify_user_task.delay(self.user.id, message)
#
#     def notify_status_change(self) -> None:
#         """Уведомление пользователя при изменении статуса платежа."""
#         message = f'The status of your payment has been updated to {self.status}'
#         self.notify_user(message)
#
#     @transition(field=status, source=PaymentStatus.PENDING, target=PaymentStatus.PAID)
#     def pending_payment(self):
#         self.status = PaymentStatus.PAID
#         self.notify_status_change()
#         self.save()
#         logger.info(f"Payment {self.transaction_id} completed successfully.")
#
#     @transition(field=status, source=PaymentStatus.PENDING, target=PaymentStatus.FAILED)
#     def failed_payment(self, error_message: str) -> None:
#         self.status = PaymentStatus.FAILED
#         self.notify_status_change()
#         self.transaction_error = error_message
#         self.save(update_fields=['transaction_error'])
#         self.save()
#         logger.error(f"Payment {self.transaction_id} failed: {error_message}")
#
#     @transition(field=status, source=PaymentStatus.PENDING, target=PaymentStatus.PARTIALLY_PAID)
#     def partially_paid_payment(self) -> None:
#         self.status = PaymentStatus.PARTIALLY_PAID
#         self.notify_status_change()
#         self.save()
#         logger.info(f"Частичная оплата: {self.transaction_id} Успешно! ")
#
#     @transition(field=status, source=PaymentStatus.FAILED, target=PaymentStatus.REFUNDED)
#     def refunded_payment(self) -> None:
#         self.status = PaymentStatus.REFUNDED
#         self.notify_status_change()
#         self.save()
#         logger.info(f"Payment {self.transaction_id} has been refunded.")
#
#     # @transition(field=status, source=PaymentStatus.FAILED, target=PaymentStatus.EXPIRED)
#     # def expired_payment(self) -> None:
#     #     logger.info(f"Payment {self.transaction_id} has been refunded.")
#     #     self.notify_status_change()
#
#     @transition(field=status, source=[PaymentStatus.PAID, PaymentStatus.REFUNDED], target=PaymentStatus.DISPUTED)
#     def dispute_payment(self):
#         self.status = PaymentStatus.DISPUTED
#         self.notify_status_change()
#         self.save()
#         logger.warning(f"Payment {self.transaction_id} has been disputed.")
#
#     @transition(field=status, source=PaymentStatus.PENDING, target=PaymentStatus.CANCELLED)
#     def cancelled_payment(self) -> None:
#         self.status = PaymentStatus.CANCELLED
#         self.notify_status_change()
#         self.save()
#         logger.info(f"Платеж: {self.transaction_id} Отменен успешно. ")
#
#     # Логика Выбора между платежной системой
#     def process_payment(self) -> None:
#         if self.payment_method == PaymentMethod.FONDY:
#             self._process_fondy_payment()
#         else:
#             raise ValidationError(_('Unsupported payment method.'))
#
#     def _process_fondy_payment(self) -> None:
#         from .services.payment_service import PaymentService
#
#         logger.info(f"Processing Fondy payment for transaction {self.transaction_id}.")
#         try:
#             items_data = [{
#                 "payment": item.payment,
#                 "product": item.product,
#                 "quantity": item.quantity,
#                 "total_price": Decimal(item.total_price)
#             } for item in self.payment_items.all()]
#
#             service = PaymentService({'amount': self.amount, 'order': self.order}, items_data=items_data)
#             payment_url = service.create_payment()
#             logger.info(f"Payment URL: {payment_url}")
#         except Exception as e:
#             logger.error(f"Error during Fondy payment processing: {e}")
#             self.status = PaymentStatus.FAILED
#             self.transaction_error = str(e)
#             self.save()
#             raise ValidationError(f'Платеж для заказа {self.order.id} уже существует')
#
#     def save(self, *args, **kwargs):
#         if not self.pk and Payment.objects.filter(order=self.order).exists():
#             raise ValidationError(f'Платеж для заказа {self.order.id} уже существует')
#         super().save(*args, **kwargs)
#
#
# class PaymentItem(models.Model):
#     payment = models.ForeignKey(
#         Payment,
#         on_delete=models.CASCADE,
#         related_name="payment_items",
#         verbose_name=_('Платеж')
#     )
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='payment_item_product', verbose_name=_('Оплаченный товар'))
#     quantity = models.PositiveIntegerField(verbose_name=_('Количество Платежа'))
#     total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Итоговая сумма'))
#
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлено'))
#
#     class Meta:
#         db_table = 'payment_item'
#         verbose_name = _('Платежный элемент')
#         verbose_name_plural = _('Платежные элементы')
#
#         indexes = [
#             models.Index(fields=['payment']),
#         ]
#
#     def save(self, *args, **kwargs):
#         """
#         Рассчитывает итоговую сумму при сохранении.
#         """
#         if self.payment and self.quantity:
#             self.total_price = self.payment.amount * self.quantity
#         super().save(*args, **kwargs)
#
#     def __str__(self):
#         return f'({self.quantity} x {self.total_price})'
#
#
