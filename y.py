from app import db
from app.models import User

u = User.query.filter_by(username='Tester1').first()
print(u)
p = u.posts
print(p)

for i in p:
    p.remove(i)
db.session.commit()
