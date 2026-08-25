"""Unit tests for classic GoF and structural/behavioral patterns in Swift."""

from __future__ import annotations

from pattern_detector.adapters.outbound.parsers.native_swift_parser import NativeSwiftParserAdapter
from pattern_detector.domain.rules.behavioral_rules import (
    DelegatePatternWeakRule,
    ObserverCombinePublishedRule,
    StateEnumAssociatedValuesRule,
    StrategyProtocolInjectionRule,
)
from pattern_detector.domain.rules.creational_rules import (
    BuilderFluentChainRule,
    FactoryMethodRule,
    SingletonSharedInstanceRule,
)
from pattern_detector.domain.rules.structural_rules import (
    AdapterViaExtensionRule,
    FacadeServiceRule,
)
from pattern_detector.domain.value_objects import PatternType


def test_singleton_shared_instance() -> None:
    code = """
    final class NetworkManager {
        static let shared = NetworkManager()
        private init() {}

        func request() {}
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("NetworkManager.swift", code)])

    rule = SingletonSharedInstanceRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.SINGLETON_SHARED_INSTANCE
    assert detections[0].target_name == "NetworkManager"
    assert detections[0].confidence.percentage >= 90


def test_weak_delegate_pattern() -> None:
    code = """
    protocol VideoPlayerDelegate: AnyObject {
        func didFinishPlaying()
    }

    class VideoPlayer {
        weak var delegate: VideoPlayerDelegate?

        func play() {
            delegate?.didFinishPlaying()
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("VideoPlayer.swift", code)])

    rule = DelegatePatternWeakRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.DELEGATE_PATTERN_WEAK
    assert "delegate" in detections[0].target_name


def test_combine_observer_published() -> None:
    code = """
    class AuthViewModel: ObservableObject {
        @Published var isAuthenticated: Bool = false
        @Published var userToken: String?
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("AuthViewModel.swift", code)])

    rule = ObserverCombinePublishedRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.OBSERVER_COMBINE_PUBLISHED
    assert detections[0].target_name == "AuthViewModel"


def test_state_enum_associated_values() -> None:
    code = """
    enum LoadingState<T> {
        case idle
        case loading
        case success(data: T)
        case failure(error: Error)
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("LoadingState.swift", code)])

    rule = StateEnumAssociatedValuesRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.STATE_ENUM_ASSOCIATED_VALUES
    assert detections[0].target_name == "LoadingState"


def test_adapter_via_extension() -> None:
    code = """
    protocol AudioPlayable {
        func startPlayback()
    }

    extension AVAudioPlayer: AudioPlayable {
        func startPlayback() {
            self.play()
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("AVAudioPlayer+Adapter.swift", code)])

    rule = AdapterViaExtensionRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.ADAPTER_VIA_EXTENSION


def test_facade_service() -> None:
    code = """
    final class CheckoutFacadeService {
        private let paymentService: PaymentService
        private let inventoryService: InventoryService
        private let emailNotificationService: NotificationService

        init(payment: PaymentService, inventory: InventoryService, email: NotificationService) {
            self.paymentService = payment
            self.inventoryService = inventory
            self.emailNotificationService = email
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("CheckoutFacade.swift", code)])

    rule = FacadeServiceRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.FACADE_SERVICE
