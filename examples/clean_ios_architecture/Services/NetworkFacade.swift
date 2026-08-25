import Foundation

public final class NetworkFacadeService {
    public static let shared = NetworkFacadeService()
    private init() {}

    public func batchSyncAll(endpoints: [URL]) async throws -> [Data] {
        return try await withThrowingTaskGroup(of: Data.self) { group in
            for url in endpoints {
                group.addTask {
                    let (data, _) = try await URLSession.shared.data(from: url)
                    return data
                }
            }
            var results: [Data] = []
            for try await item in group {
                results.append(item)
            }
            return results
        }
    }
}
