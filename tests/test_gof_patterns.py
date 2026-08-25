"""Unit tests for classic GoF creational, structural, and behavioral patterns in Swift."""

from __future__ import annotations

from pattern_detector.adapters.outbound.parsers.native_swift_parser import NativeSwiftParserAdapter
from pattern_detector.domain.rules.behavioral_rules import (
    ChainOfResponsibilityRule,
    CommandEncapsulationRule,
    DelegatePatternWeakRule,
    IteratorProtocolRule,
    MediatorCoordinatorRule,
    MementoCodableSnapshotRule,
    ObserverCombinePublishedRule,
    StateEnumAssociatedValuesRule,
    StrategyProtocolInjectionRule,
    VisitorPatternRule,
)
from pattern_detector.domain.rules.creational_rules import (
    AbstractFactoryRule,
    BuilderFluentChainRule,
    FactoryMethodRule,
    PrototypeClonableRule,
    SingletonSharedInstanceRule,
)
from pattern_detector.domain.rules.structural_rules import (
    AdapterViaExtensionRule,
    BridgePatternRule,
    CompositeViewHierarchyRule,
    DecoratorWrapperRule,
    FacadeServiceRule,
    FlyweightPatternRule,
    ProxyPatternRule,
)
from pattern_detector.domain.value_objects import PatternType


# --- Creational Tests ---

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


def test_factory_method() -> None:
    code = """
    struct ViewFactory {
        static func makeProfileView() -> some View {
            return ProfileView()
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("ViewFactory.swift", code)])

    rule = FactoryMethodRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.FACTORY_METHOD


def test_abstract_factory() -> None:
    code = """
    protocol GUIFactory {
        func makeButton() -> Button
        func makeCheckbox() -> Checkbox
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("GUIFactory.swift", code)])

    rule = AbstractFactoryRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.ABSTRACT_FACTORY
    assert detections[0].target_name == "GUIFactory"


def test_builder_fluent_chain() -> None:
    code = """
    class QueryBuilder {
        func withFilter(field: String) -> QueryBuilder {
            return self
        }
        func setLimit(limit: Int) -> QueryBuilder {
            return self
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("QueryBuilder.swift", code)])

    rule = BuilderFluentChainRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.BUILDER_FLUENT_CHAIN


def test_prototype_clonable() -> None:
    code = """
    class DocumentTemplate: NSCopying {
        func clone() -> DocumentTemplate {
            return DocumentTemplate()
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("Template.swift", code)])

    rule = PrototypeClonableRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.PROTOTYPE_CLONABLE


# --- Structural Tests ---

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


def test_bridge_pattern() -> None:
    code = """
    class RemoteControl {
        private let deviceImplementor: DeviceImplementor
        init(implementor: DeviceImplementor) {
            self.deviceImplementor = implementor
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("RemoteControl.swift", code)])

    rule = BridgePatternRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.BRIDGE_IMPLEMENTOR


def test_decorator_wrapper() -> None:
    code = """
    class LoggingServiceDecorator {
        private let underlying: ServiceProtocol
        init(base: ServiceProtocol) {
            self.underlying = base
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("LoggingDecorator.swift", code)])

    rule = DecoratorWrapperRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.DECORATOR_WRAPPER


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


def test_flyweight_cache() -> None:
    code = """
    class GlyphFlyweightFactory {
        private var cache: [String: Glyph] = [:]
        func getGlyph(char: String) -> Glyph {
            return cache[char]!
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("GlyphFactory.swift", code)])

    rule = FlyweightPatternRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.FLYWEIGHT_CACHE


def test_proxy_pattern() -> None:
    code = """
    class VirtualImageProxy {
        private var realImage: RealImage?
        func display() {}
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("VirtualImageProxy.swift", code)])

    rule = ProxyPatternRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.PROXY_VIRTUAL_OR_REMOTE


# --- Behavioral Tests ---

def test_chain_of_responsibility() -> None:
    code = """
    class AuthHandler {
        var nextHandler: AuthHandler?
        func handleRequest() {}
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("AuthHandler.swift", code)])

    rule = ChainOfResponsibilityRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.CHAIN_OF_RESPONSIBILITY


def test_command_encapsulation() -> None:
    code = """
    struct SaveOrderCommand {
        func execute() {}
        func undo() {}
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("SaveOrderCommand.swift", code)])

    rule = CommandEncapsulationRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.COMMAND_ENCAPSULATION


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


def test_iterator_protocol() -> None:
    code = """
    struct CountdownSequence: Sequence, IteratorProtocol {
        mutating func next() -> Int? {
            return nil
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("Countdown.swift", code)])

    rule = IteratorProtocolRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.ITERATOR_PROTOCOL


def test_mediator_coordinator() -> None:
    code = """
    class MainAppCoordinator {
        func startFlow() {}
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("Coordinator.swift", code)])

    rule = MediatorCoordinatorRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.MEDIATOR_COORDINATOR


def test_visitor_double_dispatch() -> None:
    code = """
    class DocumentNode {
        func accept(visitor: DocumentVisitor) {}
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("DocumentNode.swift", code)])

    rule = VisitorPatternRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.VISITOR_DOUBLE_DISPATCH
