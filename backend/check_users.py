from app import app
from models.user import User

with app.app_context():
    checks = [
        ('admin@nexus.edu',         'Admin123!'),
        ('parent2@nexus.edu',       'Parent123!'),
        ('sana@nexus.edu',          'sana123456'),
        ('samankhan2093@gmail.com', 'saman123456'),
    ]
    for email, pwd in checks:
        u = User.get_by_email(email)
        if not u:
            print(f'MISSING  {email}')
        else:
            ok = u.check_password(pwd)
            print(f'{"OK     " if ok else "BAD_PWD"}  {u.role:<10}  {email}')
