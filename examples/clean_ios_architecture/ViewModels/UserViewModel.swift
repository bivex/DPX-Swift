import Foundation
import Combine

public protocol UserViewModelDelegate: AnyObject {
    func userDidAuthenticate(userId: UUID)
}

@MainActor
public final class UserViewModel: ObservableObject {
    @Published public var currentUser: UserAccount?
    @Published public var isLoading: Bool = false

    public weak var delegate: UserViewModelDelegate?
    private let dataStore: AccountDataStore

    public init(dataStore: AccountDataStore) {
        self.dataStore = dataStore
    }

    public func loadUser(id: UUID) async {
        isLoading = true
        currentUser = await dataStore.getAccount(id: id)
        isLoading = false
        if let user = currentUser {
            delegate?.userDidAuthenticate(userId: user.id)
        }
    }
}
