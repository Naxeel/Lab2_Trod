def test_list_todos_empty(client):
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_list_todo(client):
    payload = {"title": "A", "description": "B"}
    create = client.post("/todos", json=payload)
    assert create.status_code == 201
    body = create.json()
    assert body["title"] == "A"
    assert body["description"] == "B"
    assert body["completed"] is False
    todo_id = body["id"]

    listed = client.get("/todos")
    assert listed.status_code == 200
    items = listed.json()
    assert len(items) == 1
    assert items[0]["id"] == todo_id


def test_get_todo_by_id(client):
    create = client.post("/todos", json={"title": "One"})
    assert create.status_code == 201
    todo_id = create.json()["id"]

    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "One"


def test_get_todo_not_found(client):
    response = client.get("/todos/999999")
    assert response.status_code == 404


def test_update_todo(client):
    create = client.post("/todos", json={"title": "T", "description": "D"})
    assert create.status_code == 201
    todo_id = create.json()["id"]

    response = client.put(f"/todos/{todo_id}", json={"completed": True})
    assert response.status_code == 200
    assert response.json()["completed"] is True
    assert response.json()["title"] == "T"


def test_update_todo_not_found(client):
    response = client.put("/todos/999999", json={"title": "X"})
    assert response.status_code == 404


def test_delete_todo(client):
    create = client.post("/todos", json={"title": "Del"})
    assert create.status_code == 201
    todo_id = create.json()["id"]

    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 204

    assert client.get(f"/todos/{todo_id}").status_code == 404


def test_delete_todo_not_found(client):
    response = client.delete("/todos/999999")
    assert response.status_code == 404
