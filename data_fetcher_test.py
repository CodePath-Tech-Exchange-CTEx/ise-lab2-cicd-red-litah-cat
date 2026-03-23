#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################
import unittest
from unittest.mock import MagicMock, patch
from data_fetcher import get_user_workouts, insert_post
from data_fetcher import get_user_workouts, get_user_sensor_data
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

    
    @patch('data_fetcher.bigquery.Client')
    def test_insert_post_executes_query(self, mock_client_class):
        """Tests that insert_post calls BigQuery with the correct parameters."""
        mock_instance = mock_client_class.return_value
        mock_query_job = MagicMock()
        mock_instance.query.return_value = mock_query_job
 
        insert_post('user1', 'I walked 8000 steps today!')
 
        # Verify a query was actually run
        mock_instance.query.assert_called_once()
        mock_query_job.result.assert_called_once()
 
        # Verify the content and user_id were passed as query parameters
        call_args = mock_instance.query.call_args
        job_config = call_args.kwargs.get('job_config') or call_args.args[1]
        param_names = {p.name for p in job_config.query_parameters}
        param_values = {p.name: p.value for p in job_config.query_parameters}
 
        self.assertIn('user_id', param_names)
        self.assertIn('content', param_names)
        self.assertIn('post_id', param_names)
        self.assertIn('timestamp', param_names)
        self.assertEqual(param_values['user_id'], 'user1')
        self.assertEqual(param_values['content'], 'I walked 8000 steps today!')
    

    @patch('data_fetcher.bigquery.Client')
    def test_insert_post_unique_ids(self, mock_client_class):
        """Tests that each call to insert_post generates a unique post ID."""
        mock_instance = mock_client_class.return_value
        mock_query_job = MagicMock()
        mock_instance.query.return_value = mock_query_job
 
        insert_post('user1', 'First post')
        insert_post('user1', 'Second post')
 
        self.assertEqual(mock_instance.query.call_count, 2)
 
        first_params = {
            p.name: p.value
            for p in mock_instance.query.call_args_list[0].kwargs.get('job_config').query_parameters
        }
        second_params = {
            p.name: p.value
            for p in mock_instance.query.call_args_list[1].kwargs.get('job_config').query_parameters
        }
 
        self.assertNotEqual(first_params['post_id'], second_params['post_id'])
        
     @patch('data_fetcher.bigquery.Client')
    def test_get_user_sensor_data_success(self, mock_client_class):
        """Tests mapping BigQuery SensorData rows to Python dictionaries."""
        # Arrange: Setup mock data representing BigQuery rows for 'workout1'
        mock_row_1 = MagicMock()
        mock_row_1.SensorType = 'Heart Rate'
        mock_row_1.Timestamp = '2024-07-29 07:15:00'
        mock_row_1.Data = 120.0
        mock_row_1.Units = 'bpm'

        mock_row_2 = MagicMock()
        mock_row_2.SensorType = 'Step Count'
        mock_row_2.Timestamp = '2024-07-29 07:30:00'
        mock_row_2.Data = 3000.0
        mock_row_2.Units = 'steps'

        mock_row_3 = MagicMock()
        mock_row_3.SensorType = 'Temperature'
        mock_row_3.Timestamp = '2024-07-29 07:45:00'
        mock_row_3.Data = 36.5
        mock_row_3.Units = 'Celsius'

        mock_instance = mock_client_class.return_value
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = [mock_row_1, mock_row_2, mock_row_3]
        mock_instance.query.return_value = mock_query_job

        # Act
        result = get_user_sensor_data('user1', 'workout1')

        # Assert
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], {'sensor_type': 'Heart Rate', 'timestamp': '2024-07-29 07:15:00', 'data': 120.0, 'units': 'bpm'})
        self.assertEqual(result[1], {'sensor_type': 'Step Count', 'timestamp': '2024-07-29 07:30:00', 'data': 3000.0, 'units': 'steps'})
        self.assertEqual(result[2], {'sensor_type': 'Temperature', 'timestamp': '2024-07-29 07:45:00', 'data': 36.5, 'units': 'Celsius'})

    @patch('data_fetcher.bigquery.Client')
    def test_get_user_sensor_data_empty(self, mock_client_class):
        """Tests that an empty result set safely returns an empty list."""
        mock_client_class.return_value.query.return_value.result.return_value = []

        result = get_user_sensor_data('user1', 'workout1')
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()