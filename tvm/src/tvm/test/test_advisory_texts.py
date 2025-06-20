from .test_main import *


# Get all categories
def test_read_categories():
    response = client.get("/categories/")
    assert response.status_code == 200

    expected_data = [
        {"id": 2, "name": "damage_by_standstill"},
        {"id": 4, "name": "damage_to_passengers"},
        {"id": 1, "name": "damage_to_third_parties"},
        {"id": 3, "name": "loss_of_personal_items"}
    ]

    assert response.json() == expected_data


# Get the category with the given ID
def test_read_category_200():
    response = client.get("/categories/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "damage_to_third_parties"
    }


def test_read_category_404():
    response = client.get("/categories/999")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Categorie niet gevonden."
    }


# Create a new category
def test_create_category_201():
    category_data = {
        "name": "new_category"
    }
    token = get_token_admin()

    response = client.post("/categories/", json=category_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201


def test_create_category_400():
    category_data = {
        "name": "damage_by_standstill"
    }
    token = get_token_admin()

    response = client.post("/categories/", json=category_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Deze categorie bestaat al."
    }


def test_create_category_403():
    category_data = {
        "name": "new_category"
    }
    token = get_token_not_admin()

    response = client.post("/categories/", json=category_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json() == {
        "detail": "U bent niet gerechtigd om een categorie te creëren."
    }


# Update the category with the given ID
def test_update_category_200():
    updated_data = {
        "name": "damage_to_fourth_parties"
    }
    token = get_token_admin()

    response = client.put("/categories/1", json=updated_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_update_category_404():
    updated_data = {
        "name": "damage_to_fourth_parties"
    }
    token = get_token_admin()

    response = client.put("/categories/999", json=updated_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Categorie niet gevonden."
    }


def test_update_category_403():
    updated_data = {
        "name": "loss_of_other_items"
    }
    token = get_token_not_admin()

    response = client.put("/categories/3", json=updated_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json() == {
        "detail": "U bent niet gerechtigd om een categorie te updaten."
    }


# Delete the category with the given ID
def test_delete_category_204():
    token = get_token_admin()
    response = client.delete("/categories/2", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204


def test_delete_category_404():
    token = get_token_admin()
    response = client.delete("/categories/999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Categorie niet gevonden."
    }


def test_delete_category_403():
    token = get_token_not_admin()
    response = client.delete("/categories/3", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json() == {
        "detail": "U bent niet gerechtigd om een categorie te verwijderen."
    }


# Get all subcategories
def test_read_subcategories():
    response = client.get("/subcategories/")
    assert response.status_code == 200

    expected_data = [
        {"id": 1, "category_id": 1, "name": "minrisk"},
        {"id": 2, "category_id": 1, "name": "risk_in_euros"},
        {"id": 3, "category_id": 1, "name": "deviate_from_identification"},
        {"id": 4, "category_id": 1, "name": "identify_by_risk"},
        {"id": 5, "category_id": 2, "name": "minrisk"},
        {"id": 6, "category_id": 2, "name": "risk_in_euros"},
        {"id": 7, "category_id": 2, "name": "deviate_from_identification"},
        {"id": 8, "category_id": 2, "name": "identify_by_risk"},
        {"id": 9, "category_id": 3, "name": "minrisk"},
        {"id": 10, "category_id": 3, "name": "risk_in_euros"},
        {"id": 11, "category_id": 3, "name": "deviate_from_identification"},
        {"id": 12, "category_id": 3, "name": "identify_by_risk"},
        {"id": 13, "category_id": 4, "name": "minrisk"},
        {"id": 14, "category_id": 4, "name": "risk_in_euros"},
        {"id": 15, "category_id": 4, "name": "deviate_from_identification"},
        {"id": 16, "category_id": 4, "name": "identify_by_risk"}
    ]

    assert response.json() == expected_data


# Get all subcategories by category ID
def test_read_subcategories_by_category_200():
    expected_data = [
        {"id": 1, "category_id": 1, "name": "minrisk"},
        {"id": 2, "category_id": 1, "name": "risk_in_euros"},
        {"id": 3, "category_id": 1, "name": "deviate_from_identification"},
        {"id": 4, "category_id": 1, "name": "identify_by_risk"}
    ]
    response = client.get("/categories/1/subcategories")
    assert response.status_code == 200
    assert response.json() == expected_data


def test_read_subcategories_by_category_404_no_category():
    response = client.get("/categories/999/subcategories")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Categorie niet gevonden."
    }


def test_read_subcategories_by_category_404_no_subcategories():
    category_data = {
        "name": "new_category"
    }
    token = get_token_admin()
    client.post("/categories/", json=category_data, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/categories/5/subcategories")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Geen subcategorieën voor deze categorie gevonden."
    }


# Get the subcategory with the given ID
def test_read_subcategory_200():
    response = client.get("/subcategories/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "category_id": 1,
        "name": "minrisk"
    }


def test_read_subcategory_404():
    response = client.get("/subcategories/999")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Subcategorie niet gevonden."
    }


# Gets all advice texts
def test_read_advisory_texts():
    response = client.get("/advisorytexts/")
    assert response.status_code == 200

    expected_data = [
        {"id": 1, "category": "damage_to_third_parties", "sub_category": "minrisk", "text": "Tijdens de inventarisatie hebben wij vastgesteld dat u alle risico's tot een minimum wenst te beperken. Mijn advies is om alle trekkers + opleggers WA volledig casco te verzekeren. Voor het verzekerde bedrag, gebaseerd op [basis_verzekerd_bedrag] en het (eigen risico van [eigen_risico]./standaard eigen risico.) Deze bedragen vindt u terug op de polis. U geeft aan dat u [volg_advies_op]\n\nOnderstaande dekkingen zijn standaard meeverzekerd onder een bepaalde dekking. Hierover wordt niet geadviseerd.\nWA:\n- Hulpverlening bij ziekte of ongeval\n- Gladheidsbestrijding\n- Vervoer van gevaarlijke stoffen\n- Werkrisico\n- Gemonteerd werkmaterieel\nBrand, brand/diefstal, beperkt casco of volledig casco:\n- Berging en repatriëring\nVolledig Casco:\n- Bergingskosten na pech"},
        {"id": 2, "category": "damage_to_third_parties", "sub_category": "risk_in_euros", "text": "Tijdens de inventarisatie hebben wij vastgesteld dat u risico's tot een bedrag van [maximum_eigen_risico] wilt en kunt dragen. Mijn advies is om [verzekering_soort] te verzekeren. Voor het verzekerde bedrag, gebaseerd op [basis_verzekerd_bedrag] en het (eigen risico van [eigen_risico]./standaard eigen risico.) Deze bedragen vindt u terug op de polis.  U geeft aan dat u [volg_advies_op]\n\nOnderstaande dekkingen zijn standaard meeverzekerd onder een bepaalde dekking. Hierover wordt niet geadviseerd.\nWA:\n- Hulpverlening bij ziekte of ongeval\n- Gladheidsbestrijding\n- Vervoer van gevaarlijke stoffen\n- Werkrisico\n- Gemonteerd werkmaterieel\nBrand, brand/diefstal, beperkt casco of volledig casco:\n- Berging en repatriëring\nVolledig Casco:\n- Bergingskosten na pech"},
        {"id": 3, "category": "damage_to_third_parties", "sub_category": "deviate_from_identification", "text": "U geeft aan dat u op dit onderdeel bereid bent meer risico te lopen dan wij samen hebben vastgesteld tijdens de inventarisatie. U geeft aan dat uw risicobereidheid op dit onderdeel [afwijkend_beleid] is. U geeft aan dat u dit kunt en wilt dragen. Mijn advies is om [verzekering_soort] te verzekeren. Voor het verzekerde bedrag, gebaseerd op [basis_verzekerd_bedrag]. en het (eigen risico van [eigen_risico]./standaard eigen risico.) Deze bedragen vindt u terug op de polis. U geeft aan dat u [volg_advies_op]\n\nOnderstaande dekkingen zijn standaard meeverzekerd onder een bepaalde dekking. Hierover wordt niet geadviseerd.\nWA:\n- Hulpverlening bij ziekte of ongeval\n- Gladheidsbestrijding\n- Vervoer van gevaarlijke stoffen\n- Werkrisico\n- Gemonteerd werkmaterieel\nBrand, brand/diefstal, beperkt casco of volledig casco:\n- Berging en repatriëring\nVolledig Casco:\n- Bergingskosten na pech"},
        {"id": 4, "category": "damage_to_third_parties", "sub_category": "identify_by_risk", "text": "Tijdens de inventarisatie hebben wij vastgesteld dat wij per risico in kaart brengen hoeveel risico u wilt en kunt dragen. U heeft aangegeven dat uw verzekeringsbeleid is om [beleid_klant]. U geeft aan dat u dit kunt en wilt dragen. Mijn advies is om [verzekering_soort] te verzekeren. Voor het verzekerde bedrag, gebaseerd op [basis_verzekerd_bedrag]. en het (eigen risico van [eigen_risico]./standaard eigen risico.) Deze bedragen vindt u terug op de polis.  U geeft aan dat u [volg_advies_op]\n\nOnderstaande dekkingen zijn standaard meeverzekerd onder een bepaalde dekking. Hierover wordt niet geadviseerd.\nWA:\n- Hulpverlening bij ziekte of ongeval\n- Gladheidsbestrijding\n- Vervoer van gevaarlijke stoffen\n- Werkrisico\n- Gemonteerd werkmaterieel\nBrand, brand/diefstal, beperkt casco of volledig casco:\n- Berging en repatriëring\nVolledig Casco:\n- Bergingskosten na pech"},
        {"id": 5, "category": "damage_by_standstill", "sub_category": "minrisk", "text": "Tijdens de inventarisatie hebben wij vastgesteld dat u alle risico's tot een minimum wenst te beperken. Mijn advies is om een extra bedrijfskosten dekking af te sluiten. Voor het verzekerde bedrag, gebaseerd op [basis_verzekerd_bedrag] en het (eigen risico van [eigen_risico]./standaard eigen risico.) Deze bedragen vindt u terug op de polis. U geeft aan dat u [volg_advies_op]"},
        {"id": 6, "category": "damage_by_standstill", "sub_category": "risk_in_euros", "text": "Tijdens de inventarisatie hebben wij vastgesteld dat u risico's tot een bedrag van 10.000 wilt en kunt dragen. Mijn advies is om (geen extra bedrijfskosten dekking af te sluiten/ een extra bedrijfskosten dekking af te sluiten. Voor het verzekerde bedrag, gebaseerd op [basis_verzekerd_bedrag] en het (eigen risico van [eigen_risico]./standaard eigen risico.) Deze bedragen vindt u terug op de polis.) U geeft aan dat u [volg_advies_op]"},
        {"id": 7, "category": "damage_by_standstill", "sub_category": "deviate_from_identification", "text": "U geeft aan dat u op dit onderdeel bereid bent meer risico te lopen dan wij samen hebben vastgesteld tijdens de inventarisatie. U geeft aan dat uw risicobereidheid op dit onderdeel [afwijkend_beleid] is. Dit kunt en wilt u dragen. Mijn advies is om (geen extra bedrijfskosten dekking af te sluiten/ een extra bedrijfskosten dekking af te sluiten. Voor het verzekerde bedrag, gebaseerd op [basis_verzekerd_bedrag] en het (eigen risico van [eigen_risico]./standaard eigen risico.) Deze bedragen vindt u terug op de polis.) U geeft aan dat u [volg_advies_op]"},
        {"id": 8, "category": "damage_by_standstill", "sub_category": "identify_by_risk", "text": "Tijdens de inventarisatie hebben wij vastgesteld dat wij per risico in kaart brengen hoeveel risico u wilt en kunt dragen. U heeft aangegeven dat uw verzekeringsbeleid is om [beleid_klant]. Dit kunt en wilt u dragen. Mijn advies is om (geen extra bedrijfskosten dekking af te sluiten/ een extra bedrijfskosten dekking af te sluiten. Voor het verzekerde bedrag, gebaseerd op [basis_verzekerd_bedrag] en het (eigen risico van [eigen_risico]./standaard eigen risico.) Deze bedragen vindt u terug op de polis.) U geeft aan dat u [volg_advies_op]"},
        {"id": 9, "category": "loss_of_personal_items", "sub_category": "minrisk", "text": "Tijdens de inventarisatie hebben wij vastgesteld dat u alle risico's tot een minimum wenst te beperken. Mijn advies is om een diefstal bagage dekking af te sluiten. Voor het verzekerde bedrag, gebaseerd op [basis_verzekerd_bedrag]. en het (eigen risico van [eigen_risico]./standaard eigen risico.) Deze bedragen vindt u terug op de polis.  U geeft aan dat u [volg_advies_op]"},
        {"id": 10, "category": "loss_of_personal_items", "sub_category": "risk_in_euros", "text": "Tijdens de inventarisatie hebben wij vastgesteld dat u risico's tot een bedrag van 10.000 wilt en kunt dragen. Mijn advies is om (geen diefstal bagage dekking af te sluiten./ een diefstal bagage dekking af te sluiten. Voor het verzekerde bedrag en het eigen risico verwijs ik u naar de polis.) U geeft aan dat u [volg_advies_op]"},
        {"id": 11, "category": "loss_of_personal_items", "sub_category": "deviate_from_identification", "text": "U geeft aan dat u op dit onderdeel bereid bent meer risico te lopen dan wij samen hebben vastgesteld tijdens de inventarisatie. U geeft aan dat uw risicobereidheid op dit onderdeel [afwijkend_beleid] is. Dit kunt en wilt u dragen. Mijn advies is om (geen diefstal bagage dekking af te sluiten./ een diefstal bagage dekking af te sluiten. Voor het verzekerde bedrag en het eigen risico verwijs ik u naar de polis.) U geeft aan dat u [volg_advies_op]"},
        {"id": 12, "category": "loss_of_personal_items", "sub_category": "identify_by_risk", "text": "Tijdens de inventarisatie hebben wij vastgesteld dat wij per risico in kaart brengen hoeveel risico u wilt en kunt dragen. U heeft aangegeven dat uw verzekeringsbeleid is om [beleid_klant]. Dit kunt en wilt u dragen. Mijn advies is om (geen diefstal bagage dekking af te sluiten./ een diefstal bagage dekking af te sluiten. Voor het verzekerde bedrag en het eigen risico verwijs ik u naar de polis.) U geeft aan dat u [volg_advies_op]"},
        {"id": 13, "category": "damage_to_passengers", "sub_category": "minrisk", "text": "Tijdens de inventarisatie hebben wij vastgesteld dat u alle risico's tot een minimum wenst te beperken. Mijn advies is om een SVI dekking af te sluiten. Voor het verzekerde bedrag en het eigen risico verwijs ik u naar de polis. U geeft aan dat u [volg_advies_op]"},
        {"id": 14, "category": "damage_to_passengers", "sub_category": "risk_in_euros", "text": "Tijdens de inventarisatie hebben wij vastgesteld dat u risico's tot een bedrag van 10.000 wilt en kunt dragen. Mijn advies is om (SVI dekking af te sluiten./ een SVI dekking af te sluiten. Voor het verzekerde bedrag en het eigen risico verwijs ik u naar de polis.) U geeft aan dat u [volg_advies_op]"},
        {"id": 15, "category": "damage_to_passengers", "sub_category": "deviate_from_identification", "text": "U geeft aan dat u op dit onderdeel bereid bent meer risico te lopen dan wij samen hebben vastgesteld tijdens de inventarisatie. U geeft aan dat uw risicobereidheid op dit onderdeel [afwijkend_beleid]. is. Dit kunt en wilt u dragen. Mijn advies is om (geen SVI dekking af te sluiten./ een SVI dekking af te sluiten. Voor het verzekerde bedrag en het eigen risico verwijs ik u naar de polis.) U geeft aan dat u [volg_advies_op]"},
        {"id": 16, "category": "damage_to_passengers", "sub_category": "identify_by_risk", "text": "Tijdens de inventarisatie hebben wij vastgesteld dat wij per risico in kaart brengen hoeveel risico u wilt en kunt dragen. U heeft aangegeven dat uw verzekeringsbeleid is om [beleid_klant]. Dit kunt en wilt u dragen. Mijn advies is om (geen SVI dekking af te sluiten./ een SVI dekking af te sluiten. Voor het verzekerde bedrag en het eigen risico verwijs ik u naar de polis.) U geeft aan dat u [volg_advies_op]"}
    ]

    assert response.json() == expected_data


# Gets the advice text with the given ID
def test_read_advisory_text_200():
    response = client.get("/advisorytexts/id=1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "category": "damage_to_third_parties",
        "sub_category": "minrisk",
        "text": "Tijdens de inventarisatie hebben wij vastgesteld dat u alle risico's tot een minimum wenst te beperken. Mijn advies is om alle trekkers + opleggers WA volledig casco te verzekeren. Voor het verzekerde bedrag, gebaseerd op [basis_verzekerd_bedrag] en het (eigen risico van [eigen_risico]./standaard eigen risico.) Deze bedragen vindt u terug op de polis. U geeft aan dat u [volg_advies_op]\n\nOnderstaande dekkingen zijn standaard meeverzekerd onder een bepaalde dekking. Hierover wordt niet geadviseerd.\nWA:\n- Hulpverlening bij ziekte of ongeval\n- Gladheidsbestrijding\n- Vervoer van gevaarlijke stoffen\n- Werkrisico\n- Gemonteerd werkmaterieel\nBrand, brand/diefstal, beperkt casco of volledig casco:\n- Berging en repatriëring\nVolledig Casco:\n- Bergingskosten na pech"
    }


def test_read_advisory_text_404():
    response = client.get("/advisorytexts/id=999")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Adviestekst niet gevonden."
    }


# Create new advice text
def test_create_advisory_text_201():
    advisory_text_data = {
        "category_id": 4,
        "sub_category": "category_for_new_advisory_text",
        "text": "New Advisory Text"
    }
    token = get_token_admin()

    response = client.post("/advisorytexts/", json=advisory_text_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201


def test_create_advisory_text_400_text():
    advisory_text_data = {
        "category_id": 4,
        "sub_category": "risk_in_euros",
        "text": "Tijdens de inventarisatie hebben wij vastgesteld dat u risico's tot een bedrag van 10.000 wilt en kunt dragen. Mijn advies is om (SVI dekking af te sluiten./ een SVI dekking af te sluiten. Voor het verzekerde bedrag en het eigen risico verwijs ik u naar de polis.) U geeft aan dat u [volg_advies_op]"
    }
    token = get_token_admin()

    response = client.post("/advisorytexts/", json=advisory_text_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    assert response.json() == {
        "detail": "De gegeven tekst bestaat al."
    }


def test_create_advisory_text_400_subcategory():
    advisory_text_data = {
        "category_id": 1,
        "sub_category": "minrisk",
        "text": "Nieuwe tekst"
    }
    token = get_token_admin()

    response = client.post("/advisorytexts/", json=advisory_text_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    assert response.json() == {
        "detail": "De gegeven subcategorie bestaat al voor deze categorie."
    }


def test_create_advisory_text_403():
    advisory_text_data = {
        "category_id": 4,
        "sub_category": "risk_in_euros",
        "text": "New Advisory Text"
    }
    token = get_token_not_admin()

    response = client.post("/advisorytexts/", json=advisory_text_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json() == {
        "detail": "U bent niet gerechtigd om een adviestekst te creëren."
    }


# Edits the advice text with the given ID
def test_update_advisory_text_200():
    updated_data = {
        "category_id": 3,
        "sub_category": "minrisk",
        "text": "Tijdens de inventarisatie maken we een andere tekst"
    }
    token = get_token_admin()

    response = client.put("/advisorytexts/id=9", json=updated_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_update_advisory_text_404():
    updated_data = {
        "category_id": 3,
        "sub_category": "minrisk",
        "text": "Tijdens de inventarisatie maken we een andere tekst"
    }
    token = get_token_admin()

    response = client.put("/advisorytexts/id=999", json=updated_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Adviestekst niet gevonden."
    }


def test_update_advisory_text_403():
    updated_data = {
        "category_id": 3,
        "sub_category": "minrisk",
        "text": "Tijdens de inventarisatie maken we een andere tekst"
    }
    token = get_token_not_admin()

    response = client.put("/advisorytexts/id=9", json=updated_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json() == {
        "detail": "U bent niet gerechtigd om een adviestekst te updaten."
    }


# Deletes the advice text with the given ID
def test_delete_advisory_text_204():
    token = get_token_admin()
    response = client.delete("/advisorytexts/id=6", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204


def test_delete_advisory_text_404():
    token = get_token_admin()
    response = client.delete("/advisorytexts/id=999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Adviestekst niet gevonden."
    }


def test_delete_advisory_text_403():
    token = get_token_not_admin()
    response = client.delete("/advisorytexts/id=6", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json() == {
        "detail": "U bent niet gerechtigd om een adviestekst te verwijderen."
    }


# Get advisory text by subcategory ID
def test_read_text_by_subcategory_200():
    response = client.get("/advisorytexts/subcategory/10")
    assert response.status_code == 200
    expected_data = {
        "id": 10,
        "category": "loss_of_personal_items",
        "sub_category": "risk_in_euros",
        "text": "Tijdens de inventarisatie hebben wij vastgesteld dat u risico's tot een bedrag van 10.000 wilt en kunt dragen. Mijn advies is om (geen diefstal bagage dekking af te sluiten./ een diefstal bagage dekking af te sluiten. Voor het verzekerde bedrag en het eigen risico verwijs ik u naar de polis.) U geeft aan dat u [volg_advies_op]"
    }

    assert response.json() == expected_data


def test_read_text_by_subcategory_404_no_subcategory():
    response = client.get("/advisorytexts/subcategory/999")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Subcategorie niet gevonden."
    }
