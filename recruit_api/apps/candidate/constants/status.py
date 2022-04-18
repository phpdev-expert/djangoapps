CANDIDATE_STATUS_CHOICES = (
    (1, 'Leads'),
    (2, 'Submittals'),
    (3, 'Sendout'),
    (4, 'Interview'),
    (5, 'Hired/Placement'),
    (6, 'Rejected'),
    (7, 'On Hold'),
    (8, 'Closed'),
)

DEFAULT_CANDIDATE_STATUS = CANDIDATE_STATUS_CHOICES[0][0]


VISA_STATUS_CHOICES = (
    (1, 'None'),
    (2, 'Citizenship'),
    (3, 'Green Card'),
    (4, 'HB1'),
    (5, '1099'),
    (6, 'Third Party'),
    (7, 'Other')
)

DEFAULT_VISA_STATUS = VISA_STATUS_CHOICES[1][0]
