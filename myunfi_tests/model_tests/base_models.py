from __future__ import annotations
from unittest import TestCase
from myunfi.models.base import PaginatedModel


class PaginatedBaseModelTest(TestCase):

    def test_no_page_number(self):
        pm = PaginatedModel(**{})
        self.assertEqual(pm.page_number, 0)
        self.assertEqual(pm.page_size, 12)
        pass

    def test_from_dict_page_key(self):
        #     number_of_elements: Optional[int] = Field(None, alias='numberOfElements')
        #     total_elements: Optional[int] = Field(None, alias='totalElements')
        #     total_pages: Optional[int] = Field(None, alias='totalPages')
        #     is_sorted: Optional[bool] = Field(None, alias='isSorted')
        model_data = {
            "page": {
                "number": 1,
                "size": 12,
                "totalElements": 12,
                "totalPages": 1,
                "isSorted": True,
                "numberOfElements": 12,
            }
        }

        pm = PaginatedModel.parse_obj(model_data)
        self.assertEqual(pm.page_number, 1)
        self.assertEqual(pm.page_size, 12)
        self.assertEqual(pm.total_elements, 12)
        self.assertEqual(pm.total_pages, 1)
        self.assertEqual(pm.is_sorted, True)
        self.assertEqual(pm.number_of_elements, 12)
        pass

    def test_from_dict_root_key(self):
        model_data = {
            "number": 1,
            "size": 12,
            "totalElements": 12,
            "totalPages": 1,
            "isSorted": True,
            "numberOfElements": 12,
        }

        pm = PaginatedModel.parse_obj(model_data)
        self.assertEqual(pm.page_number, 1)
        self.assertEqual(pm.page_size, 12)
        self.assertEqual(pm.total_elements, 12)
        self.assertEqual(pm.total_pages, 1)
        self.assertEqual(pm.is_sorted, True)
        self.assertEqual(pm.number_of_elements, 12)
