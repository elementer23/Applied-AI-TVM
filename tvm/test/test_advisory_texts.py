from test_main import client


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
        "detail": "Category not found."
    }

# Create a new category
def test_create_category_201():
    category_data = {
        # Enter data of this category
    }

    response = client.post("/categories/", json=category_data)
    assert response.status_code == 201

def test_create_category_400():
    category_data = {
        # Enter data of a category that already exists within the db
    }

    response = client.post("/categories/", json=category_data)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "This category already exists."
    }

def test_create_category_403():
    category_data = {
        # Enter data of a category that already exists within the db
    }

    response = client.post("/categories/", json=category_data)
    assert response.status_code == 403
    assert response.json() == {
        "detail": "You are not allowed to create a category."
    }

# Update the category with the given ID
def test_update_category_200():
    updated_data = {
        # Enter updated data for a category
    }

    response = client.put("/categories/1", json=updated_data)
    assert response.status_code == 200

def test_update_category_404():
    updated_data = {
        # Enter updated data for a category
    }

    response = client.put("/categories/999", json=updated_data)
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Category not found."
    }

def test_update_category_403():
    updated_data = {
        # Enter updated data for a category
    }

    response = client.put("/categories/3", json=updated_data)
    assert response.status_code == 403
    assert response.json() == {
        "detail": "You are not allowed to update a category."
    }

# Delete the category with the given ID
def test_delete_category_204():
    response = client.delete("/categories/1")
    assert response.status_code == 204

def test_delete_category_404():
    response = client.delete("/categories/999")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Category not found."
    }

def test_delete_category_403():
    response = client.delete("/categories/3")
    assert response.status_code == 403
    assert response.json() == {
        "detail": "You are not allowed to delete a category."
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
        "detail": "Subcategory not found."
    }

# Create a new subcategory
def test_create_subcategory_201():
    subcategory_data = {
        # Enter data of this subcategory
    }

    response = client.post("/subcategories/", json=subcategory_data)
    assert response.status_code == 201

def test_create_subcategory_400():
    subcategory_data = {
        # Enter data of a subcategory that already exists within the db
    }

    response = client.post("/subcategories/", json=subcategory_data)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "This subcategory already exists."
    }

def test_create_subcategory_403():
    subcategory_data = {
        # Enter data of a subcategory that already exists within the db
    }

    response = client.post("/subcategories/", json=subcategory_data)
    assert response.status_code == 403
    assert response.json() == {
        "detail": "You are not allowed to create a subcategory."
    }

# Update the subcategory with the given ID
def test_update_subcategory_200():
    updated_data = {
        # Enter updated data for a subcategory
    }

    response = client.put("/subcategories/1", json=updated_data)
    assert response.status_code == 200

def test_update_subcategory_404():
    updated_data = {
        # Enter updated data for a subcategory
    }

    response = client.put("/subcategories/999", json=updated_data)
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Subcategory not found."
    }

def test_update_subcategory_403():
    updated_data = {
        # Enter updated data for a subcategory
    }

    response = client.put("/subcategories/3", json=updated_data)
    assert response.status_code == 403
    assert response.json() == {
        "detail": "You are not allowed to update a subcategory."
    }

# Delete the subcategory with the given ID
def test_delete_subcategory_204():
    response = client.delete("/subcategories/1")
    assert response.status_code == 204


def test_delete_subcategory_404():
    response = client.delete("/subcategories/999")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Subcategory not found."
    }

def test_delete_subcategory_403():
    response = client.delete("/subcategories/3")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "You are not allowed to delete a subcategory."
    }



# Gets all advice texts
def test_read_advisory_texts():
    response = client.get("/advisorytexts/")
    assert response.status_code == 200

    expected_data = [
        # Fill this in with the expected results in the database
    ]

    assert response.json() == expected_data

# Gets the advice text with the given composite ID's
def test_read_advisory_text_200():
    response = client.get("/advisorytexts/id=1")
    assert response.status_code == 200
    assert response.json() == {
        # Enter data of this advisory text
    }

def test_read_advisory_text_404():
    response = client.get("/advisorytexts/id=999")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Advice text not found."
    }

# Create new advice text
def test_create_advisory_text_201():
    advisory_text_data = {
        # Enter data of this advice text
    }

    response = client.post("/advisorytexts/", json=advisory_text_data)
    assert response.status_code == 201

def test_create_advisory_text_400():
    advisory_text_data = {
        # Enter data of an advice text that already exists within the db
    }

    response = client.post("/advisorytexts/", json=advisory_text_data)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "This text already exists."
    }

def test_create_advisory_text_403():
    advisory_text_data = {
        # Enter data of an advice text that already exists within the db
    }

    response = client.post("/advisorytexts/", json=advisory_text_data)
    assert response.status_code == 403
    assert response.json() == {
        "detail": "You are not allowed to create an advisory text."
    }

# Edits the advice text with the given ID
def test_update_advisory_text_200():
    updated_data = {
        # Enter updated data for an advisory text
    }

    response = client.put("/advisorytexts/id=1", json=updated_data)
    assert response.status_code == 200

def test_update_advisory_text_404():
    updated_data = {
        # Enter updated data for an advisory text
    }

    response = client.put("/advisorytexts/id=999", json=updated_data)
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Advice text not found."
    }

def test_update_advisory_text_403():
    updated_data = {
        # Enter updated data for an advisory text
    }

    response = client.put("/advisorytexts/id=3", json=updated_data)
    assert response.status_code == 403
    assert response.json() == {
        "detail": "You are not allowed to update an advisory text."
    }

# Deletes the advice text with the given ID
def test_delete_advisory_text_204():
    response = client.delete("/advisorytexts/id=1")
    assert response.status_code == 204

def test_delete_advisory_text_404():
    response = client.delete("/advisorytexts/id=999")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Advice text not found."
    }

def test_delete_advisory_text_403():
    response = client.delete("/advisorytexts/id=3")
    assert response.status_code == 403
    assert response.json() == {
        "detail": "You are not allowed to delete an advisory text."
    }
