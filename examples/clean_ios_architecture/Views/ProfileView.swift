import SwiftUI

public struct PrimaryCardModifier: ViewModifier {
    public func body(content: Content) -> some View {
        content
            .padding()
            .background(Color.secondary.opacity(0.1))
            .cornerRadius(12)
    }
}

public struct ProfileContainerView<Content: View>: View {
    let title: String
    @ViewBuilder let content: () -> Content

    public var body: some View {
        VStack(alignment: .leading) {
            Text(title)
                .font(.headline)
            content()
        }
        .modifier(PrimaryCardModifier())
    }
}
