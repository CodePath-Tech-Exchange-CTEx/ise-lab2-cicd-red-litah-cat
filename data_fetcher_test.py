#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################
import unittest
from unittest.mock import MagicMock, patch, Mock
from data_fetcher import get_user_workouts, insert_post, get_user_posts, get_user_friends

class TestDataFetcher(unittest.TestCase):

    @patch('data_fetcher.bigquery.Client')
    def test_get_user_workouts_comprehensive(self, mock_client_class):
        """
        Comprehensive test covering:
        1. Successful mapping of all fields.
        2. Handling multiple workout records.
        3. Handling missing/null optional fields.
        """
        # Scenario: Two workouts, one complete, one with missing data 
        mock_row_full = MagicMock()
        mock_row_full.WorkoutId = 'workout_full'
        mock_row_full.StartTimestamp = '2026-03-14 07:00:00'
        mock_row_full.EndTimestamp = '2026-03-14 08:00:00'
        mock_row_full.StartLocationLat = 37.7749
        mock_row_full.StartLocationLong = -122.4194
        mock_row_full.EndLocationLat = 37.8049
        mock_row_full.EndLocationLong = -122.4210
        mock_row_full.TotalDistance = 5.0
        mock_row_full.TotalSteps = 8000
        mock_row_full.CaloriesBurned = 400.0

        mock_row_partial = MagicMock()
        mock_row_partial.WorkoutId = 'workout_partial'
        mock_row_partial.StartTimestamp = '2026-03-14 09:00:00'
        mock_row_partial.EndTimestamp = '2026-03-14 09:30:00'
        mock_row_partial.StartLocationLat = None
        mock_row_partial.StartLocationLong = None
        mock_row_partial.EndLocationLat = None
        mock_row_partial.EndLocationLong = None
        mock_row_partial.TotalDistance = None
        mock_row_partial.TotalSteps = None
        mock_row_partial.CaloriesBurned = None

        mock_instance = mock_client_class.return_value
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = [mock_row_full, mock_row_partial]
        mock_instance.query.return_value = mock_query_job

        # Execute
        result = get_user_workouts('user1')

        # Assertions for multiple workouts
        self.assertEqual(len(result), 2)

        # Assertions for the 'Full' workout mapping
        full = result[0]
        expected_keys = {
            "workout_id", "start_timestamp", "end_timestamp",
            "start_lat_lng", "end_lat_lng",
            "distance", "steps", "calories_burned"
        }
        self.assertEqual(set(full.keys()), expected_keys)

        self.assertEqual(full['workout_id'], 'workout_full')
        self.assertEqual(full['start_timestamp'], '2026-03-14 07:00:00')
        self.assertEqual(full['end_timestamp'], '2026-03-14 08:00:00')
        self.assertEqual(full['start_lat_lng'], (37.7749, -122.4194))
        self.assertEqual(full['end_lat_lng'], (37.8049, -122.4210))
        self.assertEqual(full['distance'], 5.0)
        self.assertEqual(full['calories_burned'], 400.0)
        self.assertEqual(full['steps'], 8000)


        # Assertions for 'Partial' workout to ensure no crash on Nulls 
        partial = result[1]
        self.assertEqual(partial['workout_id'], 'workout_partial')
        self.assertIsNone(partial['distance'])
        self.assertEqual(partial['start_lat_lng'], (None, None))
        self.assertEqual(partial['end_lat_lng'], (None, None))


    @patch('data_fetcher.bigquery.Client')
    def test_get_user_workouts_no_data(self, mock_client_class):
        """Tests scenario where a user has 0 workouts in the database."""
        mock_instance = mock_client_class.return_value
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []
        mock_instance.query.return_value = mock_query_job

        result = get_user_workouts('newUser')
        
        self.assertEqual(result, [])
        self.assertIsInstance(result, list)

    @patch("data_fetcher.bigquery.Client")
    def test_get_user_posts_returns_posts(self, mock_client_class):
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        row1 = Mock()
        row1.user_id = "u1"
        row1.post_id = "p1"
        row1.timestamp = "2026-03-22 10:00:00"
        row1.content = "Hello"
        row1.image = "img1.jpg"

        row2 = Mock()
        row2.user_id = "u1"
        row2.post_id = "p2"
        row2.timestamp = "2026-03-22 11:00:00"
        row2.content = None
        row2.image = None

        mock_query_job = Mock()
        mock_query_job.result.return_value = [row1, row2]
        mock_client.query.return_value = mock_query_job

        result = get_user_posts("u1")

        assert result == [
            {
                "user_id": "u1",
                "post_id": "p1",
                "timestamp": "2026-03-22 10:00:00",
                "content": "Hello",
                "image": "img1.jpg",
            },
            {
                "user_id": "u1",
                "post_id": "p2",
                "timestamp": "2026-03-22 11:00:00",
                "content": None,
                "image": None,
            },
        ]

        mock_client.query.assert_called_once()

    @patch("data_fetcher.bigquery.Client")
    def test_get_user_posts_returns_empty_list_when_no_posts(self, mock_client_class):
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_query_job = Mock()
        mock_query_job.result.return_value = []
        mock_client.query.return_value = mock_query_job

        result = get_user_posts("u999")

        assert result == []

    @patch("data_fetcher.bigquery.Client")
    def test_get_user_friends_returns_friends(self, mock_client_class):
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        row1 = Mock()
        row1.user_id = "u2"

        row2 = Mock()
        row2.user_id = "u3"

        mock_query_job = Mock()
        mock_query_job.result.return_value = [row1, row2]
        mock_client.query.return_value = mock_query_job

        result = get_user_friends("u1")

        assert result == [
            {"user_id": "u2"},
            {"user_id": "u3"},
        ]

        mock_client.query.assert_called_once()

    @patch("data_fetcher.bigquery.Client")
    def test_get_user_friends_returns_empty_list_when_no_friends(self, mock_client_class):
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_query_job = Mock()
        mock_query_job.result.return_value = []
        mock_client.query.return_value = mock_query_job

        result = get_user_friends("u999")

        assert result == []

if __name__ == "__main__":
    unittest.main()