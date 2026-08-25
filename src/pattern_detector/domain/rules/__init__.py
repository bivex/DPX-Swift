"""Rules registry and aggregation factory for Swift pattern detector."""

from __future__ import annotations

from pattern_detector.domain.rules.base import BaseRule
from pattern_detector.domain.rules.protocol_oriented_rules import (
    AssociatedTypePatRule,
    ExistentialAnyBoxRule,
    OpaqueReturnTypeRule,
    ProtocolCompositionRule,
    ProtocolExtensionDefaultImplRule,
)
from pattern_detector.domain.rules.concurrency_actor_rules import (
    ActorModelIsolationRule,
    AsyncStreamSequenceRule,
    MainActorUiBindingRule,
    SendableThreadSafetyRule,
    TaskGroupConcurrencyRule,
)
from pattern_detector.domain.rules.declarative_dsl_rules import (
    KeyPathDynamicLookupRule,
    PropertyWrapperPatternRule,
    ResultBuilderDslRule,
    ViewModifierPipelineRule,
)
from pattern_detector.domain.rules.creational_rules import (
    BuilderFluentChainRule,
    FactoryMethodRule,
    PrototypeClonableRule,
    SingletonSharedInstanceRule,
)
from pattern_detector.domain.rules.structural_rules import (
    AdapterViaExtensionRule,
    CompositeViewHierarchyRule,
    DecoratorWrapperRule,
    FacadeServiceRule,
)
from pattern_detector.domain.rules.behavioral_rules import (
    CommandEncapsulationRule,
    DelegatePatternWeakRule,
    MementoCodableSnapshotRule,
    ObserverCombinePublishedRule,
    StateEnumAssociatedValuesRule,
    StrategyProtocolInjectionRule,
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
    DynamicCastAsCascadeOcpRule,
    FatProtocolIspRule,
    KissCyclomaticComplexityRule,
    KissLongParameterListRule,
    MassiveViewControllerSrpRule,
)

DEFAULT_RULES: list[type[BaseRule]] = [
    # 1. Protocol-Oriented
    ProtocolExtensionDefaultImplRule,
    ProtocolCompositionRule,
    AssociatedTypePatRule,
    OpaqueReturnTypeRule,
    ExistentialAnyBoxRule,

    # 2. Concurrency
    ActorModelIsolationRule,
    MainActorUiBindingRule,
    TaskGroupConcurrencyRule,
    AsyncStreamSequenceRule,
    SendableThreadSafetyRule,

    # 3. Declarative DSL
    PropertyWrapperPatternRule,
    ResultBuilderDslRule,
    KeyPathDynamicLookupRule,
    ViewModifierPipelineRule,

    # 4. Creational
    SingletonSharedInstanceRule,
    FactoryMethodRule,
    BuilderFluentChainRule,
    PrototypeClonableRule,

    # 5. Structural
    AdapterViaExtensionRule,
    DecoratorWrapperRule,
    CompositeViewHierarchyRule,
    FacadeServiceRule,

    # 6. Behavioral
    DelegatePatternWeakRule,
    ObserverCombinePublishedRule,
    StrategyProtocolInjectionRule,
    StateEnumAssociatedValuesRule,
    CommandEncapsulationRule,
    MementoCodableSnapshotRule,

    # 7. Resilience & Hazards
    RetainCycleStrongSelfRule,
    ForceUnwrappingHazardRule,
    StrongDelegateRetainCycleRule,
    MainThreadBlockingCallRule,
    UnhandledTrySwallowRule,

    # 8. SOLID & Quality
    MassiveViewControllerSrpRule,
    FatProtocolIspRule,
    DynamicCastAsCascadeOcpRule,
    KissCyclomaticComplexityRule,
    KissLongParameterListRule,
    DryDuplicateLogicLogic := DryDuplicateLogicRule,
    DemeterLawTrainWreckRule,
]


def get_default_rules() -> list[BaseRule]:
    """Instantiate and return the full suite of default Swift rules."""
    return [
        ProtocolExtensionDefaultImplRule(),
        ProtocolCompositionRule(),
        AssociatedTypePatRule(),
        OpaqueReturnTypeRule(),
        ExistentialAnyBoxRule(),
        ActorModelIsolationRule(),
        MainActorUiBindingRule(),
        TaskGroupConcurrencyRule(),
        AsyncStreamSequenceRule(),
        SendableThreadSafetyRule(),
        PropertyWrapperPatternRule(),
        ResultBuilderDslRule(),
        KeyPathDynamicLookupRule(),
        ViewModifierPipelineRule(),
        SingletonSharedInstanceRule(),
        FactoryMethodRule(),
        BuilderFluentChainRule(),
        PrototypeClonableRule(),
        AdapterViaExtensionRule(),
        DecoratorWrapperRule(),
        CompositeViewHierarchyRule(),
        FacadeServiceRule(),
        DelegatePatternWeakRule(),
        ObserverCombinePublishedRule(),
        StrategyProtocolInjectionRule(),
        StateEnumAssociatedValuesRule(),
        CommandEncapsulationRule(),
        MementoCodableSnapshotRule(),
        RetainCycleStrongSelfRule(),
        ForceUnwrappingHazardRule(),
        StrongDelegateRetainCycleRule(),
        MainThreadBlockingCallRule(),
        UnhandledTrySwallowRule(),
        MassiveViewControllerSrpRule(),
        FatProtocolIspRule(),
        DynamicCastAsCascadeOcpRule(),
        KissCyclomaticComplexityRule(),
        KissLongParameterListRule(),
        DryDuplicateLogicRule(),
        DemeterLawTrainWreckRule(),
    ]
