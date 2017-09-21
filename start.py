from app import create_app
from app.models import Employee

app = create_app()

if __name__ == '__main__':
    if not Employee.query.filter_by('isSU=TRUE').all():
        e = Employee('root', 'F', 'root@root.com', 'root', '无', '1990-02-03', None, None, True)
        e.password = 'password'
        e.insert_db()

    app.run(debug=True)
