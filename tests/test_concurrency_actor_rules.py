"""Unit tests for Swift Concurrency & Actor Model detection rules."""

from __future__ import annotations

from pattern_detector.adapters.outbound.parsers.native_swift_parser import NativeSwiftParserAdapter
from pattern_detector.domain.rules.concurrency_actor_rules import (
    ActorModelIsolationRule,
    AsyncStreamSequenceRule,
    MainActorUiBindingRule,
    SendableThreadSafetyRule,
    TaskGroupConcurrencyRule,
)
from pattern_detector.domain.value_objects import PatternType


def test_actor_model_isolation() -> None:
    code = """
    actor AccountDataStore {
        private var balance: Double = 0.0

        func deposit(amount: Double) {
            balance += amount
        }

        func getBalance() -> Double {
            return balance
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("AccountDataStore.swift", code)])

    rule = ActorModelIsolationRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.ACTOR_MODEL_ISOLATION
    assert detections[0].target_name == "AccountDataStore"


def test_main_actor_ui_binding() -> None:
    code = """
    @MainActor
    final class ProfileViewModel: ObservableObject {
        @Published var username: String = ""

        func updateProfile() {
            username = "Updated"
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("ProfileViewModel.swift", code)])

    rule = MainActorUiBindingRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.MAIN_ACTOR_UI_BINDING
    assert detections[0].target_name == "ProfileViewModel"


def test_task_group_concurrency() -> None:
    code = """
    class AssetBatchLoader {
        func fetchAllImages(urls: [URL]) async throws -> [UIImage] {
            return try await withThrowingTaskGroup(of: UIImage.self) { group in
                for url in urls {
                    group.addTask {
                        return try await self.download(url: url)
                    }
                }
                var images: [UIImage] = []
                for try await img in group {
                    images.append(img)
                }
                return images
            }
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("Loader.swift", code)])

    rule = TaskGroupConcurrencyRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.TASK_GROUP_CONCURRENCY
    assert detections[0].target_name == "fetchAllImages"


def test_sendable_thread_safety() -> None:
    code = """
    struct UserPayload: Sendable, Codable {
        let id: UUID
        let name: String
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("UserPayload.swift", code)])

    rule = SendableThreadSafetyRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.SENDABLE_THREAD_SAFETY
    assert detections[0].target_name == "UserPayload"
