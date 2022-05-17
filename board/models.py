from datetime import datetime

from django.db import models
from home.models import User


class BeneficiaryCategory(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        blank=True, default=None
    )
    cat_description = models.CharField(max_length=250)
    cat_slug = models.SlugField(unique=True, max_length=250)
    cat_status = models.BooleanField(default=False)
    cat_date_created = models.DateTimeField(editable=False)
    cat_date_updated = models.DateTimeField()
    cat_date_deleted = models.DateTimeField(
        null=True, default=None, blank=True
    )

    def __str__(self) -> str:
        return self.cat_description

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.cat_date_created = datetime.now()
        self.cat_date_updated = datetime.now()
        return super().save(*args, **kwargs)


class Beneficiary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    beneficiary_category = models.ForeignKey(
        BeneficiaryCategory, on_delete=models.CASCADE
    )
    ben_name = models.CharField(max_length=250)
    ben_slug = models.SlugField(unique=True, max_length=250)
    ben_status = models.BooleanField(default=False)
    ben_date_created = models.DateTimeField(editable=False)
    ben_date_updated = models.DateTimeField()
    ben_date_deleted = models.DateTimeField(
        null=True, default=None, blank=True
    )

    def __str__(self) -> str:
        return self.ben_name

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.ben_date_created = datetime.now()
        self.ben_date_updated = datetime.now()
        return super().save(*args, **kwargs)


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cat_name = models.CharField(max_length=250)
    cat_slug = models.SlugField(unique=True, max_length=250)
    cat_type = models.SmallIntegerField()
    cat_status = models.BooleanField(default=False)
    cat_date_created = models.DateTimeField(editable=False)
    cat_date_updated = models.DateTimeField()
    cat_date_deleted = models.DateTimeField(
        null=True, default=None, blank=True
    )

    def __str__(self) -> str:
        return self.cat_name

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.cat_date_created = datetime.now()
        self.cat_date_updated = datetime.now()
        return super().save(*args, **kwargs)


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_name = models.CharField(max_length=250)
    sub_slug = models.SlugField(unique=True, max_length=250)
    sub_status = models.BooleanField(default=False)
    sub_date_created = models.DateTimeField(editable=False)
    sub_date_updated = models.DateTimeField()
    sub_date_deleted = models.DateTimeField(
        null=True, default=None, blank=True
    )

    def __str__(self) -> str:
        return self.sub_name

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.sub_date_created = datetime.now()
        self.sub_date_updated = datetime.now()
        return super().save(*args, **kwargs)


class Country(models.Model):
    cou_name = models.CharField(max_length=250)
    cou_country_code = models.CharField(max_length=4)
    cou_phone_digits = models.CharField(max_length=128)
    cou_image = models.CharField(
        max_length=250, null=True, default=None, blank=True
    )
    cou_status = models.BooleanField(default=False)
    cou_date_created = models.DateTimeField(editable=False)
    cou_date_updated = models.DateTimeField()
    cou_date_deleted = models.DateTimeField(
        null=True, default=None, blank=True
    )

    def __str__(self) -> str:
        return self.cou_name

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.cou_date_created = datetime.now()
        self.cou_date_updated = datetime.now()
        return super().save(*args, **kwargs)


class State(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    sta_name = models.CharField(max_length=250)
    sta_status = models.BooleanField(default=False)
    sta_date_created = models.DateTimeField(editable=False)
    sta_date_updated = models.DateTimeField()
    sta_date_deleted = models.DateTimeField(
        null=True, default=None, blank=True
    )

    def __str__(self) -> str:
        return self.sta_name

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.sta_date_created = datetime.now()
        self.sta_date_updated = datetime.now()
        return super().save(*args, **kwargs)


class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cli_name = models.CharField(max_length=250)
    cli_slug = models.SlugField(unique=True, max_length=250)
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True,
        blank=True, default=None
    )
    state = models.ForeignKey(
        State, on_delete=models.SET_NULL, null=True,
        blank=True, default=None
    )
    cli_city = models.CharField(max_length=250)
    cli_email = models.EmailField(
        max_length=250, null=True, blank=True, default=None
    )
    cli_phone = models.CharField(
        max_length=20, null=True, blank=True, default=None
    )
    cli_responsible = models.CharField(
        max_length=250, null=True, blank=True, default=None
    )
    cli_status = models.BooleanField(default=False)
    cli_date_created = models.DateTimeField(editable=False)
    cli_date_updated = models.DateTimeField()
    cli_date_deleted = models.DateTimeField(
        null=True, default=None, blank=True
    )

    def __str__(self) -> str:
        return self.cli_name

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.cli_date_created = datetime.now()
        self.cli_date_updated = datetime.now()
        return super().save(*args, **kwargs)


class Financial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fin_slug = models.SlugField(unique=True, max_length=250)
    fin_cost_center = models.CharField(
        max_length=250, null=True, blank=True, default=None
    )
    fin_description = models.CharField(
        max_length=250, null=True, blank=True, default=None
    )
    fin_bank_name = models.CharField(
        max_length=250, null=True, blank=True, default=None
    )
    fin_bank_branch = models.CharField(
        max_length=20, null=True, blank=True, default=None
    )
    fin_bank_account = models.CharField(
        max_length=20, null=True, blank=True, default=None
    )
    fin_type = models.SmallIntegerField()
    fin_status = models.BooleanField(default=False)
    fin_date_created = models.DateTimeField(editable=False)
    fin_date_updated = models.DateTimeField()
    fin_date_deleted = models.DateTimeField(
        null=True, default=None, blank=True
    )

    def __str__(self) -> str:
        return self.fin_cost_center or self.fin_bank_name

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.fin_date_created = datetime.now()
        self.fin_date_updated = datetime.now()
        return super().save(*args, **kwargs)


class Release(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rel_slug = models.SlugField(unique=True, max_length=250)
    rel_gen_status = models.SmallIntegerField()
    rel_entry_date = models.DateField()
    rel_amount = models.DecimalField(max_digits=15, decimal_places=3)
    rel_monthly_balance = models.DecimalField(max_digits=15, decimal_places=3)
    rel_overall_balance = models.DecimalField(max_digits=15, decimal_places=3)
    rel_description = models.CharField(
        max_length=250, null=True, blank=True, default=None
    )
    subcategory = models.ForeignKey(
        SubCategory, on_delete=models.SET_NULL, null=True,
        blank=True, default=None
    )
    beneficiary = models.ForeignKey(
        Beneficiary, on_delete=models.SET_NULL, null=True,
        blank=True, default=None
    )
    client = models.ForeignKey(
        Client, on_delete=models.SET_NULL, null=True,
        blank=True, default=None
    )
    financial_cost_center = models.ForeignKey(
        Financial, on_delete=models.SET_NULL, null=True,
        blank=True, default=None, related_name='financial_cost_center'
    )
    financial_account = models.ForeignKey(
        Financial, on_delete=models.SET_NULL, null=True,
        blank=True, default=None, related_name='financial_account'
    )
    rel_sqn = models.IntegerField()
    rel_status = models.BooleanField(default=False)
    rel_date_created = models.DateTimeField(editable=False)
    rel_date_updated = models.DateTimeField()
    rel_date_deleted = models.DateTimeField(
        null=True, default=None, blank=True
    )

    def __str__(self) -> str:
        return str(self.user)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.rel_date_created = datetime.now()
        self.rel_date_updated = datetime.now()
        return super().save(*args, **kwargs)


class Analytic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ana_cycle = models.DateField()
    ana_json = models.TextField()
    ana_status = models.BooleanField(default=False)
    ana_date_created = models.DateTimeField(editable=False)
    ana_date_updated = models.DateTimeField()
    ana_date_deleted = models.DateTimeField(
        null=True, default=None, blank=True
    )

    def __str__(self) -> str:
        return str(self.user)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.ana_date_created = datetime.now()
        self.ana_date_updated = datetime.now()
        return super().save(*args, **kwargs)
