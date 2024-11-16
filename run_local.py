import pymysql
pymysql.install_as_MySQLdb()  # Add this at the top

from radiology_assistant import create_app
from radiology_assistant.utils import dump_temp, run_duplication_deletion
from radiology_assistant import db


app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        dump_temp()
        
    run_duplication_deletion(constant=True)
    app.run(debug=True)



