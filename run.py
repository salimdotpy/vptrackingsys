from app import create_app
from app import db
from flask_migrate import Migrate

app = create_app()

migrate = Migrate(app, db)

@app.context_processor
def utility_processor():
    from app.utils import siteName, getImage
    return dict(siteName=siteName, getImage=getImage)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # app.run(debug=True, host="0.0.0.0", port=5000)
    app.run(debug=True, port=5001)