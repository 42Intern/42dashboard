API_CATEGORIES = {
    "Accreditations": [
        {"label": "List Accreditations", "value": "/v2/accreditations"},
        {"label": "Accreditation by ID", "value": "/v2/accreditations/:id"},
    ],
    "Achievements": [
        {"label": "List Achievements", "value": "/v2/achievements"},
        {"label": "Cursus Achievements", "value": "/v2/cursus/:cursus_id/achievements"},
        {"label": "Campus Achievements", "value": "/v2/campus/:campus_id/achievements"},
        {"label": "Title Achievements", "value": "/v2/titles/:title_id/achievements"},
        {"label": "Achievement by ID", "value": "/v2/achievements/:id"},
    ],
    "Achievements Users": [
        {"label": "Users Earned Achievement", "value": "/v2/achievements/:achievement_id/achievements_users"},
        {"label": "List Achievements Users", "value": "/v2/achievements_users"},
        {"label": "Achievements Users by ID", "value": "/v2/achievements_users/:id"},
    ],
    "Cursus": [
        {"label": "List Cursus", "value": "/v2/cursus"},
        {"label": "Cursus by ID", "value": "/v2/cursus/:id"},
    ],
    "Users": [
        {"label": "List Users", "value": "/v2/users"},
        {"label" : "Campus Users", "value": "/v2/campus_users"},
        {"label": "Cursus Users", "value": "/v2/cursus/:cursus_id/users"},
    ],
}