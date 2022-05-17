# Remove html django settings from output list
def email_valid_output(message):
    return message.replace('<ul class="errorlist"><li>',
        '<br />').replace('</li></ul>', '').replace('This field',  # noqa: E128
        'Email field')  # noqa: E128


def general_valid_output(message):
    return message.replace('<ul class="errorlist"><li>',
        '<br />').replace('</li></ul>', '')  # noqa: E128


def password_valid_output(message):
    return message.replace('<ul class="errorlist"><li>',
        '<br />').replace('</li></ul>', '').replace('brjump',  # noqa: E128
        '<br />').replace('This field', 'Password field')  # noqa: E128
