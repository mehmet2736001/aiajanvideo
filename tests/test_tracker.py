from core.production_tracker import ProductionTracker, tracker


def test_singleton_and_lifecycle():
    assert ProductionTracker() is tracker
    tracker.reset()
    assert tracker.get_status()["status"] == "IDLE" and not tracker.busy

    tracker.start("Deneme", "dervis", 3)
    assert tracker.busy
    tracker.update_step(2, "Ses", "detay", 30, 40)
    s = tracker.get_status()
    assert s["status"] == "VOICE_SYNTHESIS" and s["progress_percent"] == 30
    # sorgu sayısı kalan süreyi değiştirmemeli
    a = tracker.get_status()["estimated_remaining_seconds"]
    b = tracker.get_status()["estimated_remaining_seconds"]
    assert abs(a - b) <= 1

    tracker.fail("patladı")
    assert tracker.get_status()["status"] == "ERROR" and not tracker.busy
    assert "patladı" in tracker.get_director_summary()

    tracker.start("Yeni", "dervis", 1)
    tracker.complete({"ok": True})
    assert tracker.get_status()["progress_percent"] == 100
    tracker.reset()
