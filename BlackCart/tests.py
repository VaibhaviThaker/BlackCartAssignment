import pytest
from flask import json
from products import app

"""
    Could have defined test suites but could not due to time constraints
"""
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_returns_matching_store(client):
    response = client.get('/stores/1/products')
    data = json.loads(response.data)
    assert_resp_equal([{
        'Name': 'IPod Nano - 8GB',
        'ProductId': 632910392,
        'Variations': [{'currency': 'USD',
                        'inventory_status': 'instock',
                        'name': 'Color',
                        'price': '199.00',
                        'title': 'Pink',
                        'weight': 1.25},
                       {'currency': 'USD',
                        'inventory_status': 'instock',
                        'name': 'Color',
                        'price': '199.00',
                        'title': 'Red',
                        'weight': 1.75},
                       {'currency': 'USD',
                        'inventory_status': 'instock',
                        'name': 'Color',
                        'price': '199.00',
                        'title': 'Green',
                        'weight': 1.25},
                       {'currency': 'USD',
                        'inventory_status': 'instock',
                        'name': 'Color',
                        'price': '199.00',
                        'title': 'Black',
                        'weight': 1.25}]},
        {'Name': 'IPod Touch 8GB',
         'ProductId': 921728736,
         'Variations': [{'currency': 'USD',
                         'inventory_status': 'instock',
                         'name': 'Title',
                         'price': '199.00',
                         'title': 'Black',
                         'weight': 1.25}]
         }],
        data,
    )


def test_returns_no_store_found(client):
    response = client.get('/stores/4/products')
    data = json.loads(response.data)
    assert_resp_equal({'error': '404: Store not found'}, data)


def assert_resp_equal(expected, data):
    assert expected == data
