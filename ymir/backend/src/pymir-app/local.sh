export SECRET_KEY=jia9OoGhooChuPee2bei

export SHARED_DATA_DIR=./data
export SHARED_DATA_PREFIX=./data
export GRPC_CHANNEL=192.168.28.38:50066

export LOG_LEVEL=DEBUG
export ACCESS_LOG=./access.log
export ERROR_LOG=./error.log

export SMTP_TLS=True
export SMTP_PORT=465
export SMTP_HOST=smtp.exmail.qq.com
export SMTP_USER=ymir-notice@intellif.com
export SMTP_PASSWORD=Qwe1234+ymir
export EMAILS_FROM_EMAIL=ymir-notice@intellif.com
export EMAILS_FROM_NAME=ymir-project
export EMAIL_TEMPLATES_DIR=/app/email-templates/build
export FIRST_ADMIN=admin@example.com
export FIRST_ADMIN_PASSWORD=fake_passwd

export IS_TESTING=True
export USE_200_EVERYWHERE=False
export DATABASE_URI="sqlite:///run.db"
export PYTHONPATH=$PYTHONPATH:../common/
alembic -x sqlite=True upgrade head
python app/initial_data.py
uvicorn app.main:app --reload --port 8088 --host 0.0.0.0
