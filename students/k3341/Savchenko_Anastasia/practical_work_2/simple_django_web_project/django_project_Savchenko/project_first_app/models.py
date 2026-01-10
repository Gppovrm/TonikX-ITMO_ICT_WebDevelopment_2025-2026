from django.db import models


class CarOwner(models.Model):
    id_owner = models.AutoField(primary_key=True)
    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    class Meta:
        verbose_name = "Автовладелец"
        verbose_name_plural = "Автовладельцы"


class Car(models.Model):
    id_car = models.AutoField(primary_key=True)
    state_number = models.CharField(max_length=15)
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    color = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.state_number})"

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"


class Ownership(models.Model):
    id_owner_car = models.AutoField(primary_key=True)
    id_owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE, null=True)
    id_car = models.ForeignKey(Car, on_delete=models.CASCADE, null=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.id_owner} - {self.id_car}"

    class Meta:
        verbose_name = "Владение"
        verbose_name_plural = "Владения"
        ordering = ['-start_date']


class DriversLicense(models.Model):
    LICENSE_TYPES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]

    id_license = models.AutoField(primary_key=True)
    id_owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=10)
    type = models.CharField(max_length=10, choices=LICENSE_TYPES)
    issue_date = models.DateField()

    def __str__(self):
        return f"{self.license_number} ({self.type})"

    class Meta:
        verbose_name = "Водительское удостоверение"
        verbose_name_plural = "Водительские удостоверения"


# ✅ Создали виртуальное окружение tutorial-env
#
# ✅ Установили Django
#
# ✅ Создали проект django_project_Savchenko
#
# ✅ Создали приложение project_first_app
#
# ✅ Добавили приложение в settings.py
#
# ✅ Создали модели в models.py ( по схеме)
#
# ✅ Создали миграции (makemigrations)
#
# ✅ Применили миграции (migrate)
#
# ✅ Создали базу данных db.sqlite3