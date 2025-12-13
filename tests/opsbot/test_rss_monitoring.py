"""Test RSS monitoring functionality."""

from unittest.mock import Mock, patch

from eq12_opsbot.tasks import OpenAICommunityWatcher


class TestRSSMonitoring:
    """Test RSS feed parsing and monitoring."""

    @patch("feedparser.parse")
    def test_rss_feed_parsing(self, mock_parse, temp_eq12_dir):
        """Test RSS feed parsing extracts entries correctly."""
        # Mock feed data
        mock_parse.return_value = Mock()
        mock_parse.return_value.entries = [
            Mock(
                id="entry_1",
                title="New GPT-4 Model Available",
                summary="GPT-4 Turbo is now available in the API",
                link="https://community.openai.com/post/123",
                published_parsed=None,
                published="2024-01-15T10:00:00Z",
            ),
            Mock(
                id="entry_2",
                title="Rate Limit Updates",
                summary="New rate limits for GPT-3.5-turbo",
                link="https://community.openai.com/post/124",
                published_parsed=None,
                published="2024-01-15T11:00:00Z",
            ),
        ]

        watcher = OpenAICommunityWatcher(eq12_root=temp_eq12_dir)
        entries = watcher._fetch_feed_entries("https://test-feed.com")

        assert len(entries) == 2
        assert entries[0]["title"] == "New GPT-4 Model Available"
        assert entries[1]["id"] == "entry_2"
        assert "summary" in entries[0]

    def test_entry_classification(self, temp_eq12_dir):
        """Test RSS entry classification for priority and actionability."""
        watcher = OpenAICommunityWatcher(eq12_root=temp_eq12_dir)

        # High priority: breaking change
        breaking_entry = {
            "title": "BREAKING: API v1 Deprecated",
            "summary": "API v1 will be discontinued on March 1st",
            "content": "All users must migrate to v2",
        }

        classification = watcher._classify_entry(breaking_entry)
        assert classification["priority"] == "high"
        assert classification["actionable"] is True

        # Medium priority: new feature
        feature_entry = {
            "title": "New Vision Model Released",
            "summary": "GPT-4 Vision is now available",
            "content": "Try the new multimodal capabilities",
        }

        classification = watcher._classify_entry(feature_entry)
        assert classification["priority"] == "medium"

        # Low priority: general announcement
        announcement_entry = {
            "title": "Weekly Community Roundup",
            "summary": "Summary of this week's discussions",
            "content": "Check out what the community has been up to",
        }

        classification = watcher._classify_entry(announcement_entry)
        assert classification["priority"] == "low"

    def test_duplicate_detection(self, temp_eq12_dir):
        """Test duplicate RSS entry detection."""
        watcher = OpenAICommunityWatcher(eq12_root=temp_eq12_dir)

        # First processing should add to seen entries
        entry = {
            "id": "test_entry_123",
            "title": "Test Entry",
            "link": "https://example.com/123",
        }

        is_duplicate_first = watcher._is_duplicate_entry(entry)
        assert is_duplicate_first is False

        # Mark as seen
        watcher._mark_entry_seen(entry)

        # Second processing should detect duplicate
        is_duplicate_second = watcher._is_duplicate_entry(entry)
        assert is_duplicate_second is True

    @patch("eq12_opsbot.notifiers.NotificationManager")
    def test_actionable_entry_notification(self, mock_notifier, temp_eq12_dir):
        """Test notifications sent for actionable entries."""
        watcher = OpenAICommunityWatcher(eq12_root=temp_eq12_dir)

        # Mock actionable entry
        actionable_entry = {
            "id": "urgent_123",
            "title": "URGENT: API Key Format Change Required",
            "summary": "All API keys must be updated by Friday",
            "link": "https://community.openai.com/urgent/123",
            "published": "2024-01-15T10:00:00Z",
        }

        classification = {
            "priority": "high",
            "actionable": True,
            "action_type": "api_change",
            "deadline": "2024-01-19",
        }

        # Process the entry
        watcher._process_entry(actionable_entry, classification)

        # Should have sent notification
        mock_notifier.return_value.send_notification.assert_called_once()
        call_args = mock_notifier.return_value.send_notification.call_args

        assert "urgent" in call_args[1]["message"].lower()
        assert call_args[1]["priority"] == "high"

    def test_entry_persistence(self, temp_eq12_dir):
        """Test RSS entries are saved to log files."""
        watcher = OpenAICommunityWatcher(eq12_root=temp_eq12_dir)

        entry = {
            "id": "save_test_123",
            "title": "Test Entry for Persistence",
            "summary": "This entry should be saved to logs",
            "link": "https://example.com/save_test",
            "published": "2024-01-15T10:00:00Z",
        }

        # Save entry
        watcher._save_entry_to_log(entry)

        # Check log file was created and contains entry
        log_files = list((temp_eq12_dir / "logs").glob("community_posts_*.jsonl"))
        assert len(log_files) > 0

        # Read and verify content
        with open(log_files[0], encoding="utf-8") as f:
            content = f.read()
            assert "save_test_123" in content
            assert "Test Entry for Persistence" in content

    @patch("feedparser.parse")
    def test_error_handling_invalid_feed(self, mock_parse, temp_eq12_dir):
        """Test error handling for invalid RSS feeds."""
        # Mock feed parsing error
        mock_parse.side_effect = Exception("Network error")

        watcher = OpenAICommunityWatcher(eq12_root=temp_eq12_dir)

        # Should handle error gracefully
        entries = watcher._fetch_feed_entries("https://invalid-feed.com")

        assert entries == []

    def test_seen_entries_persistence(self, temp_eq12_dir):
        """Test seen entries are persisted between runs."""
        # First watcher instance
        watcher1 = OpenAICommunityWatcher(eq12_root=temp_eq12_dir)

        entry = {
            "id": "persist_test_456",
            "title": "Test Persistence",
            "link": "https://example.com/persist_test",
        }

        # Mark as seen in first instance
        watcher1._mark_entry_seen(entry)

        # Second watcher instance should remember seen entry
        watcher2 = OpenAICommunityWatcher(eq12_root=temp_eq12_dir)

        is_duplicate = watcher2._is_duplicate_entry(entry)
        assert is_duplicate is True

    @patch("eq12_opsbot.notifiers.NotificationManager")
    def test_github_issue_creation(self, mock_notifier, temp_eq12_dir):
        """Test GitHub issue creation for high priority items."""
        watcher = OpenAICommunityWatcher(eq12_root=temp_eq12_dir)

        high_priority_entry = {
            "id": "github_test_789",
            "title": "Critical API Change Notice",
            "summary": "Breaking change requires immediate action",
            "link": "https://community.openai.com/critical/789",
            "published": "2024-01-15T10:00:00Z",
        }

        classification = {
            "priority": "high",
            "actionable": True,
            "action_type": "breaking_change",
            "requires_github_issue": True,
        }

        # Process entry
        watcher._process_entry(high_priority_entry, classification)

        # Should have attempted GitHub issue creation
        mock_notifier.return_value.create_github_issue.assert_called_once()
        call_args = mock_notifier.return_value.create_github_issue.call_args

        assert "Critical API Change" in call_args[1]["title"]
        assert "breaking_change" in call_args[1]["labels"]
