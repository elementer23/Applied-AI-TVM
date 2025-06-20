from models import *
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import subprocess
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from sqlalchemy.engine.url import make_url
import embedchain.loaders.mysql as mysql_loader_module

_original_init = mysql_loader_module.MySQLLoader.__init__
load_dotenv()


def patched_init(self, config):
    url = config.get("url")
    if url:
        parsed_url = make_url(url)
        config = {
            "host": parsed_url.host,
            "user": parsed_url.username,
            "password": parsed_url.password,
            "port": parsed_url.port,
            "database": parsed_url.database,
        }

    _original_init(self, config)


mysql_loader_module.MySQLLoader.__init__ = patched_init

SQLALCHEMY_DATABASE_URL = os.getenv("SQL_CONNECTION")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Method that inserts the data from the initial database to prevent errors
def insert_base_data():
    db = SessionLocal()
    admin_username = "test_user"
    if db.query(User).filter(User.username == admin_username).first():
        db.close()
        return None
    hashed_admin_password = get_password_hash("test_pass")
    admin_user = User(username=admin_username, hashed_password=hashed_admin_password, role="admin")

    not_admin_username = "test_not_admin"
    if db.query(User).filter(User.username == not_admin_username).first():
        db.close()
        return None
    hashed_user_password = get_password_hash("notadminpass")
    not_admin_user = User(username=not_admin_username, hashed_password=hashed_user_password, role="user")

    user_to_delete_username = "user_to_delete"
    if db.query(User).filter(User.username == not_admin_username).first():
        db.close()
        return None
    hashed_delete_password = get_password_hash("passtodelete")
    user_to_delete = User(username=user_to_delete_username, hashed_password=hashed_delete_password, role="user")

    db.add(admin_user)
    db.add(not_admin_user)
    db.add(user_to_delete)

    new_category1 = Category(name="damage_to_third_parties")
    new_category2 = Category(name="damage_by_standstill")
    new_category3 = Category(name="loss_of_personal_items")
    new_category4 = Category(name="damage_to_passengers")

    db.add(new_category1)
    db.add(new_category2)
    db.add(new_category3)
    db.add(new_category4)

    for i in range(1, 5):
        new_subcategory1 = SubCategory(category_id=i, name="minrisk")
        new_subcategory2 = SubCategory(category_id=i, name="risk_in_euros")
        new_subcategory3 = SubCategory(category_id=i, name="deviate_from_identification")
        new_subcategory4 = SubCategory(category_id=i, name="identify_by_risk")
        db.add(new_subcategory1)
        db.add(new_subcategory2)
        db.add(new_subcategory3)
        db.add(new_subcategory4)

    new_advisorytext1 = AdvisoryText(category="damage_to_third_parties", sub_category="minrisk",
                                     text="Tijdens de inventarisatie hebben wij vastgesteld dat u alle risico's tot een minimum wenst te beperken. Mijn advies is om alle trekkers + opleggers WA volledig casco te verzekeren. Voor het verzekerde bedrag, gebaseerd op [basis_verzekerd_bedrag] en het (eigen risico van [eigen_risico]./standaard eigen risico.) Deze bedragen vindt u terug op de polis. U geeft aan dat u [volg_advies_op]\n\nOnderstaande dekkingen zijn standaard meeverzekerd onder een bepaalde dekking. Hierover wordt niet geadviseerd.\nWA:\n- Hulpverlening bij ziekte of ongeval\n- Gladheidsbestrijding\n- Vervoer van gevaarlijke stoffen\n- Werkrisico\n- Gemonteerd werkmaterieel\nBrand, brand/diefstal, beperkt casco of volledig casco:\n- Berging en repatriëring\nVolledig Casco:\n- Bergingskosten na pech")
    new_advisorytext2 = AdvisoryText(category="damage_to_third_parties", sub_category="risk_in_euros",
                                     text="Tijdens de inventarisatie hebben wij vastgesteld dat u risico's tot een bedrag van [maximum_eigen_risico] wilt en kunt dragen. Mijn advies is om [verzekering_soort] te verzekeren. Voor het verzekerde bedrag, gebaseerd op [basis_verzekerd_bedrag] en het (eigen risico van [eigen_risico]./standaard eigen risico.) Deze bedragen vindt u terug op de polis.  U geeft aan dat u [volg_advies_op]\n\nOnderstaande dekkingen zijn standaard meeverzekerd onder een bepaalde dekking. Hierover wordt niet geadviseerd.\nWA:\n- Hulpverlening bij ziekte of ongeval\n- Gladheidsbestrijding\n- Vervoer van gevaarlijke stoffen\n- Werkrisico\n- Gemonteerd werkmaterieel\nBrand, brand/diefstal, beperkt casco of volledig casco:\n- Berging en repatriëring\nVolledig Casco:\n- Bergingskosten na pech")
    new_advisorytext3 = AdvisoryText(category="damage_to_third_parties", sub_category="deviate_from_identification",
                                     text="U geeft aan dat u op dit onderdeel bereid bent meer risico te lopen dan wij samen hebben vastgesteld tijdens de inventarisatie. U geeft aan dat uw risicobereidheid op dit onderdeel [afwijkend_beleid] is. U geeft aan dat u dit kunt en wilt dragen. Mijn advies is om [verzekering_soort] te verzekeren. Voor het verzekerde bedrag, gebaseerd op [basis_verzekerd_bedrag]. en het (eigen risico van [eigen_risico]./standaard eigen risico.) Deze bedragen vindt u terug op de polis. U geeft aan dat u [volg_advies_op]\n\nOnderstaande dekkingen zijn standaard meeverzekerd onder een bepaalde dekking. Hierover wordt niet geadviseerd.\nWA:\n- Hulpverlening bij ziekte of ongeval\n- Gladheidsbestrijding\n- Vervoer van gevaarlijke stoffen\n- Werkrisico\n- Gemonteerd werkmaterieel\nBrand, brand/diefstal, beperkt casco of volledig casco:\n- Berging en repatriëring\nVolledig Casco:\n- Bergingskosten na pech")
    new_advisorytext4 = AdvisoryText(category="damage_to_third_parties", sub_category="identify_by_risk",
                                     text="Tijdens de inventarisatie hebben wij vastgesteld dat wij per risico in kaart brengen hoeveel risico u wilt en kunt dragen. U heeft aangegeven dat uw verzekeringsbeleid is om [beleid_klant]. U geeft aan dat u dit kunt en wilt dragen. Mijn advies is om [verzekering_soort] te verzekeren. Voor het verzekerde bedrag, gebaseerd op [basis_verzekerd_bedrag]. en het (eigen risico van [eigen_risico]./standaard eigen risico.) Deze bedragen vindt u terug op de polis.  U geeft aan dat u [volg_advies_op]\n\nOnderstaande dekkingen zijn standaard meeverzekerd onder een bepaalde dekking. Hierover wordt niet geadviseerd.\nWA:\n- Hulpverlening bij ziekte of ongeval\n- Gladheidsbestrijding\n- Vervoer van gevaarlijke stoffen\n- Werkrisico\n- Gemonteerd werkmaterieel\nBrand, brand/diefstal, beperkt casco of volledig casco:\n- Berging en repatriëring\nVolledig Casco:\n- Bergingskosten na pech")
    new_advisorytext5 = AdvisoryText(category="damage_by_standstill", sub_category="minrisk",
                                     text="Tijdens de inventarisatie hebben wij vastgesteld dat u alle risico's tot een minimum wenst te beperken. Mijn advies is om een extra bedrijfskosten dekking af te sluiten. Voor het verzekerde bedrag, gebaseerd op [basis_verzekerd_bedrag] en het (eigen risico van [eigen_risico]./standaard eigen risico.) Deze bedragen vindt u terug op de polis. U geeft aan dat u [volg_advies_op]")
    new_advisorytext6 = AdvisoryText(category="damage_by_standstill", sub_category="risk_in_euros",
                                     text="Tijdens de inventarisatie hebben wij vastgesteld dat u risico's tot een bedrag van 10.000 wilt en kunt dragen. Mijn advies is om (geen extra bedrijfskosten dekking af te sluiten/ een extra bedrijfskosten dekking af te sluiten. Voor het verzekerde bedrag, gebaseerd op [basis_verzekerd_bedrag] en het (eigen risico van [eigen_risico]./standaard eigen risico.) Deze bedragen vindt u terug op de polis.) U geeft aan dat u [volg_advies_op]")
    new_advisorytext7 = AdvisoryText(category="damage_by_standstill", sub_category="deviate_from_identification",
                                     text="U geeft aan dat u op dit onderdeel bereid bent meer risico te lopen dan wij samen hebben vastgesteld tijdens de inventarisatie. U geeft aan dat uw risicobereidheid op dit onderdeel [afwijkend_beleid] is. Dit kunt en wilt u dragen. Mijn advies is om (geen extra bedrijfskosten dekking af te sluiten/ een extra bedrijfskosten dekking af te sluiten. Voor het verzekerde bedrag, gebaseerd op [basis_verzekerd_bedrag] en het (eigen risico van [eigen_risico]./standaard eigen risico.) Deze bedragen vindt u terug op de polis.) U geeft aan dat u [volg_advies_op]")
    new_advisorytext8 = AdvisoryText(category="damage_by_standstill", sub_category="identify_by_risk",
                                     text="Tijdens de inventarisatie hebben wij vastgesteld dat wij per risico in kaart brengen hoeveel risico u wilt en kunt dragen. U heeft aangegeven dat uw verzekeringsbeleid is om [beleid_klant]. Dit kunt en wilt u dragen. Mijn advies is om (geen extra bedrijfskosten dekking af te sluiten/ een extra bedrijfskosten dekking af te sluiten. Voor het verzekerde bedrag, gebaseerd op [basis_verzekerd_bedrag] en het (eigen risico van [eigen_risico]./standaard eigen risico.) Deze bedragen vindt u terug op de polis.) U geeft aan dat u [volg_advies_op]")
    new_advisorytext9 = AdvisoryText(category="loss_of_personal_items", sub_category="minrisk",
                                     text="Tijdens de inventarisatie hebben wij vastgesteld dat u alle risico's tot een minimum wenst te beperken. Mijn advies is om een diefstal bagage dekking af te sluiten. Voor het verzekerde bedrag, gebaseerd op [basis_verzekerd_bedrag]. en het (eigen risico van [eigen_risico]./standaard eigen risico.) Deze bedragen vindt u terug op de polis.  U geeft aan dat u [volg_advies_op]")
    new_advisorytext10 = AdvisoryText(category="loss_of_personal_items", sub_category="risk_in_euros",
                                      text="Tijdens de inventarisatie hebben wij vastgesteld dat u risico's tot een bedrag van 10.000 wilt en kunt dragen. Mijn advies is om (geen diefstal bagage dekking af te sluiten./ een diefstal bagage dekking af te sluiten. Voor het verzekerde bedrag en het eigen risico verwijs ik u naar de polis.) U geeft aan dat u [volg_advies_op]")
    new_advisorytext11 = AdvisoryText(category="loss_of_personal_items", sub_category="deviate_from_identification",
                                      text="U geeft aan dat u op dit onderdeel bereid bent meer risico te lopen dan wij samen hebben vastgesteld tijdens de inventarisatie. U geeft aan dat uw risicobereidheid op dit onderdeel [afwijkend_beleid] is. Dit kunt en wilt u dragen. Mijn advies is om (geen diefstal bagage dekking af te sluiten./ een diefstal bagage dekking af te sluiten. Voor het verzekerde bedrag en het eigen risico verwijs ik u naar de polis.) U geeft aan dat u [volg_advies_op]")
    new_advisorytext12 = AdvisoryText(category="loss_of_personal_items", sub_category="identify_by_risk",
                                      text="Tijdens de inventarisatie hebben wij vastgesteld dat wij per risico in kaart brengen hoeveel risico u wilt en kunt dragen. U heeft aangegeven dat uw verzekeringsbeleid is om [beleid_klant]. Dit kunt en wilt u dragen. Mijn advies is om (geen diefstal bagage dekking af te sluiten./ een diefstal bagage dekking af te sluiten. Voor het verzekerde bedrag en het eigen risico verwijs ik u naar de polis.) U geeft aan dat u [volg_advies_op]")
    new_advisorytext13 = AdvisoryText(category="damage_to_passengers", sub_category="minrisk",
                                      text="Tijdens de inventarisatie hebben wij vastgesteld dat u alle risico's tot een minimum wenst te beperken. Mijn advies is om een SVI dekking af te sluiten. Voor het verzekerde bedrag en het eigen risico verwijs ik u naar de polis. U geeft aan dat u [volg_advies_op]")
    new_advisorytext14 = AdvisoryText(category="damage_to_passengers", sub_category="risk_in_euros",
                                      text="Tijdens de inventarisatie hebben wij vastgesteld dat u risico's tot een bedrag van 10.000 wilt en kunt dragen. Mijn advies is om (SVI dekking af te sluiten./ een SVI dekking af te sluiten. Voor het verzekerde bedrag en het eigen risico verwijs ik u naar de polis.) U geeft aan dat u [volg_advies_op]")
    new_advisorytext15 = AdvisoryText(category="damage_to_passengers", sub_category="deviate_from_identification",
                                      text="U geeft aan dat u op dit onderdeel bereid bent meer risico te lopen dan wij samen hebben vastgesteld tijdens de inventarisatie. U geeft aan dat uw risicobereidheid op dit onderdeel [afwijkend_beleid]. is. Dit kunt en wilt u dragen. Mijn advies is om (geen SVI dekking af te sluiten./ een SVI dekking af te sluiten. Voor het verzekerde bedrag en het eigen risico verwijs ik u naar de polis.) U geeft aan dat u [volg_advies_op]")
    new_advisorytext16 = AdvisoryText(category="damage_to_passengers", sub_category="identify_by_risk",
                                      text="Tijdens de inventarisatie hebben wij vastgesteld dat wij per risico in kaart brengen hoeveel risico u wilt en kunt dragen. U heeft aangegeven dat uw verzekeringsbeleid is om [beleid_klant]. Dit kunt en wilt u dragen. Mijn advies is om (geen SVI dekking af te sluiten./ een SVI dekking af te sluiten. Voor het verzekerde bedrag en het eigen risico verwijs ik u naar de polis.) U geeft aan dat u [volg_advies_op]")

    db.add(new_advisorytext1)
    db.add(new_advisorytext2)
    db.add(new_advisorytext3)
    db.add(new_advisorytext4)
    db.add(new_advisorytext5)
    db.add(new_advisorytext6)
    db.add(new_advisorytext7)
    db.add(new_advisorytext8)
    db.add(new_advisorytext9)
    db.add(new_advisorytext10)
    db.add(new_advisorytext11)
    db.add(new_advisorytext12)
    db.add(new_advisorytext13)
    db.add(new_advisorytext14)
    db.add(new_advisorytext15)
    db.add(new_advisorytext16)

    new_conversation1 = Conversation(user_id=1, created_at=datetime.now(timezone.utc) + timedelta(minutes=1))
    new_conversation2 = Conversation(user_id=1, created_at=datetime.now(timezone.utc) + timedelta(minutes=2))
    new_conversation3 = Conversation(user_id=2, created_at=datetime.now(timezone.utc) + timedelta(minutes=3))
    new_conversation4 = Conversation(user_id=2, created_at=datetime.now(timezone.utc) + timedelta(minutes=4))
    new_conversation5 = Conversation(user_id=1, created_at=datetime.now(timezone.utc) + timedelta(minutes=20))

    new_message1 = Message(conversation_id=1, content="First test message", is_user_message=True,
                           created_at=datetime.now(timezone.utc) + timedelta(minutes=1))
    new_message2 = Message(conversation_id=1, content="AI response", is_user_message=False,
                           created_at=datetime.now(timezone.utc) + timedelta(minutes=2))
    new_message3 = Message(conversation_id=2, content="Another test message", is_user_message=True,
                           created_at=datetime.now(timezone.utc) + timedelta(minutes=3))
    new_message4 = Message(conversation_id=2, content="Another AI response", is_user_message=False,
                           created_at=datetime.now(timezone.utc) + timedelta(minutes=4))
    new_message5 = Message(conversation_id=3, content="A test message without a response", is_user_message=True,
                           created_at=datetime.now(timezone.utc) + timedelta(minutes=5))
    new_message6 = Message(conversation_id=4, content="Another test message without a response", is_user_message=True,
                           created_at=datetime.now(timezone.utc) + timedelta(minutes=6))

    db.add(new_conversation1)
    db.add(new_conversation2)
    db.add(new_conversation3)
    db.add(new_conversation4)
    db.add(new_conversation5)
    db.add(new_message1)
    db.add(new_message2)
    db.add(new_message3)
    db.add(new_message4)
    db.add(new_message5)
    db.add(new_message6)
    db.commit()
    db.close()


# Resets the database, used for unit testing
def reset_database():
    tables_to_truncate = [
        "advisory_texts",
        "categories",
        "sub_categories",
        "messages",
        "conversations",
        "users"
        # Add tables here that need to be truncated before testing
    ]

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))

            for table in tables_to_truncate:
                conn.execute(text(f"TRUNCATE TABLE {table};"))

            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            trans.commit()
        except Exception as e:
            trans.rollback()
            print("Failed to reset database:", e)
            raise


# Method that runs init_db.py automatically
def run_init_db():
    subprocess.run(["python", "init_db.py"], check=True)


def get_password_hash(password):
    return pwd_context.hash(password)
