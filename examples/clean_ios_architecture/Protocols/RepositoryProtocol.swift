import Foundation

public protocol EntityProtocol: Identifiable, Sendable {
    associatedtype ID: Hashable
    var id: ID { get }
}

public protocol RepositoryProtocol {
    associatedtype Entity: EntityProtocol

    func find(by id: Entity.ID) async throws -> Entity?
    func save(entity: Entity) async throws
    func all() async throws -> [Entity]
}

extension RepositoryProtocol {
    public func all() async throws -> [Entity] {
        return []
    }
}
