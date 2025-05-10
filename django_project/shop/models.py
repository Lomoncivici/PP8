from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.CharField("Название", max_length=100)
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField("Название", max_length=50)
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Product(models.Model):
    name        = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True)
    price       = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    image       = models.ImageField("Картинка", upload_to='products/%Y/%m/%d', blank=True, null=True)
    created_at  = models.DateTimeField("Время создания", auto_now_add=True)
    updated_at  = models.DateTimeField("Время изменения", auto_now=True)
    is_deleted  = models.BooleanField("Удалён", default=False)
    category    = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.PROTECT, related_name='products')
    tags        = models.ManyToManyField(Tag, verbose_name="Теги", blank=True, related_name='products')

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Order(models.Model):
    order_number = models.CharField("Номер заказа", max_length=20, unique=True)
    created_at   = models.DateTimeField("Дата создания", auto_now_add=True)
    address      = models.CharField("Адрес доставки", max_length=255)
    phone        = models.CharField("Телефон клиента", max_length=20)
    full_name    = models.CharField("ФИО клиента", max_length=150)
    products     = models.ManyToManyField(Product, through='OrderItem', related_name='orders')

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.order_number}"


class OrderItem(models.Model):
    order             = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product           = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity          = models.PositiveIntegerField("Количество", default=1)
    discount_per_item = models.DecimalField("Скидка за единицу", max_digits=8, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"