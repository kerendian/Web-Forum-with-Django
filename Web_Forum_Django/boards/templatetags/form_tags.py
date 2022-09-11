from django import template
# Creating Custom Template Tags
register = template.Library()

@register.filter
def field_type(bound_field):
    return bound_field.field.widget.__class__.__name__

@register.filter
def input_class(bound_field):
    css_class = ''
    # if the form is not bound, it will simply return 'form-control '
    if bound_field.form.is_bound:
        # if the form is bound and valid, it will return 'form-control is-valid'
        if bound_field.errors:
            css_class = 'is-invalid'
        # if the form is bound and invalid, it will return 'form-control is-invalid'
        elif field_type(bound_field) != 'PasswordInput':
            css_class = 'is-valid'
    return 'form-control {}'.format(css_class)