from app import app
from app import db
from app.models import User


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80, ssl_context=('certs/cert.pem', 'certs/key.pem'))