import pytest

import app


@pytest.fixture(autouse=True)
def empty_warehouses():
    app.warehouses.clear()
    app.next_warehouse_id = 1
    app.app.config["TESTING"] = True
    yield
    app.warehouses.clear()


def test_create_and_list_warehouse():
    client = app.app.test_client()

    response = client.post(
        "/warehouses",
        data={"action": "create", "name": "Main", "capacity": "10"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Main" in response.data
    assert b"Capacity: 10" in response.data
    assert b"Current stock: 0" in response.data
    assert b"Remaining capacity: 10" in response.data


def test_add_and_remove_goods():
    client = app.app.test_client()
    client.post(
        "/warehouses",
        data={"action": "create", "name": "Main", "capacity": "10"},
    )

    response = client.post(
        "/warehouses/1/add",
        data={"quantity": "4"},
        follow_redirects=True,
    )
    assert b"Current stock: 4" in response.data

    response = client.post(
        "/warehouses/1/remove",
        data={"quantity": "3"},
        follow_redirects=True,
    )
    assert b"Current stock: 1" in response.data


@pytest.mark.parametrize(
    ("path", "data", "error"),
    [
        ("/warehouses", {"action": "create", "name": "", "capacity": "10"}, b"Give the warehouse"),
        ("/warehouses", {"action": "create", "name": "Bad", "capacity": "0"}, b"positive whole number"),
        ("/warehouses", {"action": "create", "name": "Bad", "capacity": "1.5"}, b"positive whole number"),
    ],
)
def test_invalid_warehouse_input(path, data, error):
    response = app.app.test_client().post(path, data=data, follow_redirects=True)

    assert error in response.data
    assert len(app.warehouses) == 0


def test_add_beyond_capacity_is_rejected_without_changing_stock():
    client = app.app.test_client()
    client.post(
        "/warehouses",
        data={"action": "create", "name": "Main", "capacity": "5"},
    )

    response = client.post(
        "/warehouses/1/add",
        data={"quantity": "6"},
        follow_redirects=True,
    )

    assert b"do not fit" in response.data
    assert app.warehouses[1].stock == 0


def test_remove_too_many_is_rejected_without_changing_stock():
    client = app.app.test_client()
    client.post(
        "/warehouses",
        data={"action": "create", "name": "Main", "capacity": "5"},
    )
    client.post("/warehouses/1/add", data={"quantity": "2"})

    response = client.post(
        "/warehouses/1/remove",
        data={"quantity": "3"},
        follow_redirects=True,
    )

    assert b"Not enough" in response.data
    assert app.warehouses[1].stock == 2


@pytest.mark.parametrize(
    ("action", "quantity"),
    [("add", "0"), ("add", "-1"), ("remove", "1.5"), ("remove", "")],
)
def test_invalid_quantity_is_rejected(action, quantity):
    client = app.app.test_client()
    client.post(
        "/warehouses",
        data={"action": "create", "name": "Main", "capacity": "5"},
    )

    response = client.post(
        f"/warehouses/1/{action}",
        data={"quantity": quantity},
        follow_redirects=True,
    )

    assert b"positive whole number" in response.data
