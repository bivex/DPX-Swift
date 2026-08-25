"""Unit tests verifying zero false positives on clean, idiomatic Swift code."""

from __future__ import annotations

from pattern_detector.adapters.outbound.parsers.native_swift_parser import NativeSwiftParserAdapter
from pattern_detector.domain.rules import get_default_rules
from pattern_detector.domain.rules.creational_rules import (
    FactoryMethodRule,
    SingletonSharedInstanceRule,
)
from pattern_detector.domain.rules.resilience_safety_rules import (
    ForceUnwrappingHazardRule,
    MainThreadBlockingCallRule,
    RetainCycleStrongSelfRule,
    StrongDelegateRetainCycleRule,
    UnhandledTrySwallowRule,
)
from pattern_detector.domain.rules.solid_principles_rules import (
    DemeterLawTrainWreckRule,
    DryDuplicateLogicRule,
    FatProtocolIspRule,
    KissCyclomaticComplexityRule,
    KissLongParameterListRule,
    MassiveViewControllerSrpRule,
)
from pattern_detector.domain.services.rule_engine import RuleEngineService
from pattern_detector.domain.value_objects import PatternCategory


def test_plain_dto_models_have_zero_srp_violations() -> None:
    code = """
    struct CustomerProfile: Codable, Equatable, Identifiable {
        let id: UUID
        let firstName: String
        let lastName: String
        let email: String
        let phone: String
        let isVerified: Bool
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("CustomerProfile.swift", code)])

    rule = MassiveViewControllerSrpRule()
    detections = rule.evaluate(model)

    assert len(detections) == 0


def test_safe_optional_unwrapping_no_force_unwrap_hazard() -> None:
    code = """
    func processUserData(rawJson: Data?) {
        guard let data = rawJson else { return }
        if let user = try? JSONDecoder().decode(User.self, from: data) {
            print(user.name)
        }
        let fallback = user?.email ?? "no-email"
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("ProcessUser.swift", code)])

    rule = ForceUnwrappingHazardRule()
    detections = rule.evaluate(model)

    assert len(detections) == 0


def test_weak_self_in_closure_no_retain_cycle_hazard() -> None:
    code = """
    class FeedCoordinator {
        func refreshFeed() {
            Task { [weak self] in
                guard let self = self else { return }
                await self.loadData()
            }
        }

        func loadData() async {}
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("FeedCoordinator.swift", code)])

    rule = RetainCycleStrongSelfRule()
    detections = rule.evaluate(model)

    assert len(detections) == 0


def test_weak_delegate_no_strong_delegate_hazard() -> None:
    code = """
    protocol NavigationDelegate: AnyObject {
        func didNavigate()
    }

    class Router {
        weak var delegate: NavigationDelegate?
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("Router.swift", code)])

    rule = StrongDelegateRetainCycleRule()
    detections = rule.evaluate(model)

    assert len(detections) == 0


def test_focused_role_protocol_no_isp_fat_protocol() -> None:
    code = """
    protocol ItemSelectable {
        func select(item: Item)
        func deselect(item: Item)
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("Selectable.swift", code)])

    rule = FatProtocolIspRule()
    detections = rule.evaluate(model)

    assert len(detections) == 0


def test_static_utility_methods_not_flagged_as_singleton_or_factory() -> None:
    code = """
    enum StringSanitizer {
        static func trim(text: String) -> String {
            return text.trimmingCharacters(in: .whitespacesAndNewlines)
        }

        static func isValidEmail(text: String) -> Bool {
            return text.contains("@")
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("Sanitizer.swift", code)])

    singleton_rule = SingletonSharedInstanceRule()
    factory_rule = FactoryMethodRule()

    assert len(singleton_rule.evaluate(model)) == 0
    assert len(factory_rule.evaluate(model)) == 0


def test_standard_parameter_counts_no_kiss_violation() -> None:
    code = """
    func calculateTotal(price: Double, taxRate: Double, discount: Double) -> Double {
        return (price * (1.0 + taxRate)) - discount
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("Calculator.swift", code)])

    rule = KissLongParameterListRule()
    detections = rule.evaluate(model)

    assert len(detections) == 0


def test_pure_business_service_no_hazards() -> None:
    code = """
    struct OrderValidator {
        func validate(order: Order) -> Result<Void, ValidationError> {
            if order.items.isEmpty {
                return .failure(.emptyCart)
            }
            if order.totalAmount <= 0 {
                return .failure(.invalidAmount)
            }
            return .success(())
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("OrderValidator.swift", code)])

    engine = RuleEngineService(rules=get_default_rules())
    detections = engine.evaluate(model)

    # Clean validator should have 0 resilience hazards and 0 principle violations
    hazards = [d for d in detections if d.pattern_category in (PatternCategory.RESILIENCE, PatternCategory.PRINCIPLE)]
    assert len(hazards) == 0


def test_proper_error_handling_no_try_swallow() -> None:
    code = """
    func loadFileSafely() {
        do {
            let data = try Data(contentsOf: URL(fileURLWithPath: "config.json"))
            process(data)
        } catch {
            Logger.shared.error("Failed to load file: \\(error)")
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("FileLoader.swift", code)])

    rule = UnhandledTrySwallowRule()
    detections = rule.evaluate(model)

    assert len(detections) == 0
