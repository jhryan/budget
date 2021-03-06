from app import create_app
from app import db
from app.models import Account
from app.models import AssetType
from app.models import Budget
from app.models import Journal
from app.models import Posting
from app.models import User


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Account': Account,
        'AssetType': AssetType,
        'Budget': Budget,
        'Journal': Journal,
        'Posting': Posting,
        'User': User
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80,
            ssl_context=('certs/cert.pem', 'certs/key.pem'))
