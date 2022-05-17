from home.models import User
from library.utils.helper import hash_gen


class HomeHelperMixin:
    def make_user(
        self,
        use_login='jane.doe@email.com',
        use_password='$Trong1234',
        use_is_valid=False,
        use_is_manager=False,
        use_status=True
    ):
        return User.objects.create(
            use_login=use_login,
            use_password=hash_gen(use_password),
            use_is_valid=use_is_valid,
            use_is_manager=use_is_manager,
            use_status=use_status
        )
