from unittest.mock import patch, MagicMock
from src.repositories.analytics_repository import AnalyticsRepository

class TestAnalyticsRepository:
    @patch("src.repositories.analytics_repository.analytics")
    def test_save_click(self, mock_analytics):
        mock_result = MagicMock()
        mock_result.acknowledged = True
        mock_analytics.insert_one.return_value = mock_result
        
        click_data = {"event": "click", "elementId": "button1"}
        result = AnalyticsRepository.save_click(click_data)
        
        assert result is True
        mock_analytics.insert_one.assert_called_once_with(click_data)

    @patch("src.repositories.analytics_repository.analytics")
    def test_get_all_clicks(self, mock_analytics):
        mock_cursor = [
            {"event": "click", "elementId": "button1"},
            {"event": "click", "elementId": "button2"}
        ]
        mock_analytics.find.return_value = mock_cursor
        
        result = AnalyticsRepository.get_all_clicks()
        
        assert len(result) == 2
        assert result[0]["elementId"] == "button1"
        mock_analytics.find.assert_called_once_with({}, {"_id": 0})

    @patch("src.repositories.analytics_repository.analytics")
    def test_get_stats(self, mock_analytics):
        mock_pipeline_results = [
            {
                "_id": {"variant": "A", "elementId": "btn"},
                "count": 2,
                "emails": ["user1@test.com", "user2@test.com", "user1@test.com", None]
            }
        ]
        mock_analytics.aggregate.return_value = mock_pipeline_results
        
        result = AnalyticsRepository.get_stats()
        
        assert "stats" in result
        assert len(result["stats"]) == 1
        # Check if duplicates and None were removed from emails
        emails = result["stats"][0]["emails"]
        assert len(emails) == 2
        assert "user1@test.com" in emails
        assert "user2@test.com" in emails
        assert None not in emails
