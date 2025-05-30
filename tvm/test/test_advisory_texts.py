from test_main import client

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
    response = client.get("/advisorytexts/catid=1&subid=1")
    assert response.status_code == 200
    assert response.json() == {
        # Enter data of this advisory text
    }

def test_read_advisory_text_404():
    response = client.get("/advisorytexts/catid=999&subid=999")
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

    response = client.put("/advisorytexts/catid=1&subid=1", json=updated_data)
    assert response.status_code == 200

def test_update_advisory_text_404():
    updated_data = {
        # Enter updated data for an advisory text
    }

    response = client.put("/advisorytexts/catid=999&subid=999", json=updated_data)
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Advice text not found."
    }

def test_update_advisory_text_403():
    updated_data = {
        # Enter updated data for an advisory text
    }

    response = client.put("/advisorytexts/catid=3&subid=3", json=updated_data)
    assert response.status_code == 403
    assert response.json() == {
        "detail": "You are not allowed to update an advisory text."
    }

# Deletes the advice text with the given ID
def test_delete_advisory_text_204():
    response = client.delete("/advisorytexts/catid=1&subid=1")
    assert response.status_code == 204

def test_delete_advisory_text_404():
    response = client.delete("/advisorytexts/catid=999&subid=999")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Advice text not found."
    }

def test_delete_advisory_text_403():
    response = client.delete("/advisorytexts/catid=3&subid=3")
    assert response.status_code == 403
    assert response.json() == {
        "detail": "You are not allowed to delete an advisory text."
    }
