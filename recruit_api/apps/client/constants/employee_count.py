EMPLOYEE_COUNT_CHOICES = (
    (1, 'From 1 to 10'),
    (2, 'From 10 to 50'),
    (3, 'From 50 to 100'),
    (4, 'From 100 to 500'),
    (5, 'From 500 to 1000')
)

DEFAULT_EMPLOYEE_COUNT = EMPLOYEE_COUNT_CHOICES[0][0]


CONTACT_TYPE_CHOICES = (
    (1, 'Contact Person'),
    (2, 'Hiring Manager'),
)

DEFAULT_CONTACT_TYPE= CONTACT_TYPE_CHOICES[0][0]
