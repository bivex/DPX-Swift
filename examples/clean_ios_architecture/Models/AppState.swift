import Foundation

public enum SessionState: Codable, Sendable {
    case unauthenticated
    case authenticating
    case active(sessionToken: String, user: UserAccount)
    case expired(reason: String)
}

public struct AppStateSnapshot: Codable, Sendable {
    public let timestamp: Date
    public let state: SessionState

    public func createSnapshot() -> Data? {
        return try? JSONEncoder().encode(self)
    }
}
