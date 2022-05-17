import json
import time

from board.models import (Analytic, Beneficiary, BeneficiaryCategory, Category,
                          Client, Country, Financial, Release, State,
                          SubCategory)


class TestBase:
    def sleep(self, sec=5):
        return time.sleep(sec)


class BoardHelperMixin(TestBase):
    def make_beneficiary(
        self,
        user=None,
        beneficiary_category=None,
        ben_name='Beneficiary',
        ben_slug='slug',
        ben_status=True
    ):
        return Beneficiary.objects.create(
            user=user,
            beneficiary_category=beneficiary_category,
            ben_name=ben_name,
            ben_slug=ben_slug,
            ben_status=ben_status
        )

    def make_beneficiary_category(
        self,
        user=None,
        cat_description='Description',
        cat_slug='slug',
        cat_status=True
    ):
        return BeneficiaryCategory.objects.create(
            user=user,
            cat_description=cat_description,
            cat_slug=cat_slug,
            cat_status=cat_status
        )

    def make_category(
        self,
        user=None,
        cat_name='Category',
        cat_slug='slug',
        cat_type=1,
        cat_status=True
    ):
        return Category.objects.create(
            user=user,
            cat_name=cat_name,
            cat_slug=cat_slug,
            cat_type=cat_type,
            cat_status=cat_status
        )

    def make_subcategory(
        self,
        category=None,
        sub_name='Subcategory',
        sub_slug='slug',
        sub_status=True
    ):
        return SubCategory.objects.create(
            category=category,
            sub_name=sub_name,
            sub_slug=sub_slug,
            sub_status=sub_status
        )

    def make_country(
        self,
        cou_name='Country',
        cou_country_code='1',
        cou_phone_digits='9-10-11',
        cou_status=True
    ):
        return Country.objects.create(
            cou_name=cou_name,
            cou_country_code=cou_country_code,
            cou_phone_digits=cou_phone_digits,
            cou_status=cou_status
        )

    def make_state(
        self,
        country=None,
        sta_name='State',
        sta_status=True
    ):
        return State.objects.create(
            country=country,
            sta_name=sta_name,
            sta_status=sta_status
        )

    def make_client(
        self,
        user=None,
        cli_name='Client',
        cli_slug='slug',
        country=None,
        state=None,
        cli_city='City',
        cli_email=None,
        cli_phone=None,
        cli_responsible=None,
        cli_status=True
    ):
        return Client.objects.create(
            user=user,
            cli_name=cli_name,
            cli_slug=cli_slug,
            country=country,
            state=state,
            cli_city=cli_city,
            cli_email=cli_email,
            cli_phone=cli_phone,
            cli_responsible=cli_responsible,
            cli_status=cli_status
        )

    def make_financial(
        self,
        user=None,
        fin_slug='slug',
        fin_cost_center=None,
        fin_description=None,
        fin_bank_name=None,
        fin_bank_branch=None,
        fin_bank_account=None,
        fin_type=None,
        fin_status=True
    ):
        return Financial.objects.create(
            user=user,
            fin_slug=fin_slug,
            fin_cost_center=fin_cost_center,
            fin_description=fin_description,
            fin_bank_name=fin_bank_name,
            fin_bank_branch=fin_bank_branch,
            fin_bank_account=fin_bank_account,
            fin_type=fin_type,
            fin_status=fin_status,
        )

    def make_release(
        self,
        user=None,
        rel_slug='slug',
        rel_gen_status=4,
        rel_entry_date='2022-05-01',
        rel_amount=1000.00,
        rel_monthly_balance=1000.00,
        rel_overall_balance=1000.00,
        rel_description=None,
        subcategory=None,
        beneficiary=None,
        client=None,
        financial_cost_center=None,
        financial_account=None,
        rel_sqn=1,
        rel_status=True
    ):
        return Release.objects.create(
            user=user,
            rel_slug=rel_slug,
            rel_gen_status=rel_gen_status,
            rel_entry_date=rel_entry_date,
            rel_amount=rel_amount,
            rel_monthly_balance=rel_monthly_balance,
            rel_overall_balance=rel_overall_balance,
            rel_description=rel_description,
            subcategory=subcategory,
            beneficiary=beneficiary,
            client=client,
            financial_cost_center=financial_cost_center,
            financial_account=financial_account,
            rel_sqn=rel_sqn,
            rel_status=rel_status
        )

    def make_analytic(
        self,
        user=None,
        ana_cycle='2022-05-01',
        ana_json={},
        ana_status=True
    ):
        return Analytic.objects.create(
            user=user,
            ana_cycle=ana_cycle,
            ana_json=json.dumps(ana_json),
            ana_status=ana_status
        )
