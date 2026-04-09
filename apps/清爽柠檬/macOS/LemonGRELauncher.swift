import Cocoa
import WebKit

final class AppDelegate: NSObject, NSApplicationDelegate {
    var window: NSWindow?

    func applicationDidFinishLaunching(_ notification: Notification) {
        let config = WKWebViewConfiguration()
        config.websiteDataStore = .default()

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.setValue(false, forKey: "drawsBackground")

        let window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 440, height: 860),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        window.center()
        window.minSize = NSSize(width: 400, height: 740)
        window.title = Bundle.main.object(forInfoDictionaryKey: "CFBundleDisplayName") as? String ?? "Lemon GRE"
        window.contentView = webView
        window.makeKeyAndOrderFront(nil)
        self.window = window

        if let resourceURL = Bundle.main.resourceURL {
            let webRoot = resourceURL.appendingPathComponent("release/web", isDirectory: true)
            let indexURL = webRoot.appendingPathComponent("index.html")
            webView.loadFileURL(indexURL, allowingReadAccessTo: webRoot)
        }

        NSApp.activate(ignoringOtherApps: true)
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        true
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.setActivationPolicy(.regular)
app.delegate = delegate
app.run()
