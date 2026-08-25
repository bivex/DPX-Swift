import Foundation

public struct UserAccount: EntityProtocol, Codable, Sendable {
    public let id: UUID
    public var name: String
    public var balance: Decimal
}

public actor AccountDataStore {
    private var accounts: [UUID: UserAccount] = [:]

    public init() {}

    public func deposit(accountId: UUID, amount: Decimal) {
        guard var acc = accounts[accountId] else { return }
        acc.balance += amount
        accounts[accountId] = acc
    }

    public func getAccount(id: UUID) -> UserAccount? {
        return accounts[id]
    }
}
