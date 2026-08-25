"""Unit tests for memory safety, retain cycles, and resilience hazard rules in Swift."""

from __future__ import annotations

from pattern_detector.adapters.outbound.parsers.native_swift_parser import NativeSwiftParserAdapter
from pattern_detector.domain.rules.resilience_safety_rules import (
    ForceUnwrappingHazardRule,
    MainThreadBlockingCallRule,
    RetainCycleStrongSelfRule,
    StrongDelegateRetainCycleRule,
)
from pattern_detector.domain.value_objects import PatternType


def test_retain_cycle_strong_self_closure() -> None:
    code = """
    class LocationTracker {
        func startTracking() {
            Task {
                self.processCoordinates()
            }
        }

        func processCoordinates() {}
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("LocationTracker.swift", code)])

    rule = RetainCycleStrongSelfRule()
    detections = rule.evaluate(model)

    assert len(detections) >= 1
    assert detections[0].pattern_type == PatternType.RETAIN_CYCLE_STRONG_SELF


def test_strong_delegate_hazard() -> None:
    code = """
    class Downloader {
        var delegate: DownloadDelegate?
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("Downloader.swift", code)])

    rule = StrongDelegateRetainCycleRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.STRONG_DELEGATE_RETAIN_CYCLE


def test_force_unwrapping_hazard() -> None:
    code = """
    func loadConfig() {
        let path = Bundle.main.path(forResource: "config", ofType: "plist")!
        let data = FileManager.default.contents(atPath: path)!
        let json = try! JSONDecoder().decode(Config.self, from: data)
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("Config.swift", code)])

    rule = ForceUnwrappingHazardRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.FORCE_UNWRAPPING_HAZARD


def test_main_thread_blocking_call() -> None:
    code = """
    @MainActor
    class MainViewController: UIViewController {
        func loadSync() {
            Thread.sleep(forTimeInterval: 2.0)
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("MainViewController.swift", code)])

    rule = MainThreadBlockingCallRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.MAIN_THREAD_BLOCKING_CALL
