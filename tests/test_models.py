# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_update_a_product(self):
        """It should Update a product's details in the database"""
        product = ProductFactory()
        product.create()  # Create the product first
        original_id = product.id
        product.description = "Updated description"
        product.price = 15.00
        product.update()  # Call the update method

        # Fetch the product back from the database
        updated_product = Product.find(original_id)
        self.assertEqual(updated_product.id, original_id)
        self.assertEqual(updated_product.description, "Updated description")
        self.assertEqual(Decimal(updated_product.price), 15.00)

    def test_delete_a_product(self):
        """It should Delete a product from the database"""
        product = ProductFactory()
        product.create()  # Create the product first
        self.assertEqual(len(Product.all()), 1)  # Ensure it exists

        product.delete()  # Delete the product
        self.assertEqual(len(Product.all()), 0)  # Ensure it no longer exists

    def test_list_all_products(self):
        """It should List all products in the database"""
        self.assertEqual(Product.all(), [])  # Initially, the list should be empty
        products = ProductFactory.create_batch(5)  # Create 5 products
        for product in products:
            product.create()  # Add them to the database
        self.assertEqual(len(Product.all()), 5)  # Check if all are listed

    def test_find_by_name(self):
        """It should Find a product by its name"""
        products = ProductFactory.create_batch(3)
        for product in products:
            product.create()
        name_to_find = products[0].name  # Get the name of the first product

        found_products = Product.find_by_name(name_to_find)
        self.assertEqual(len(found_products), 1)
        self.assertEqual(found_products[0].name, name_to_find)

    def test_find_by_availability(self):
        """It should Find products by their availability"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        availability_to_find = products[0].available  # Get availability status

        found_products = Product.find_by_availability(availability_to_find)
        self.assertEqual(len(found_products), 1)
        self.assertEqual(found_products[0].available, availability_to_find)

    def test_find_by_category(self):
        """It should Find products by their category"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        category_to_find = products[0].category  # Get the category of the first product

        found_products = Product.find_by_category(category_to_find)
        self.assertEqual(len(found_products), 1)
        self.assertEqual(found_products[0].category, category_to_find)

