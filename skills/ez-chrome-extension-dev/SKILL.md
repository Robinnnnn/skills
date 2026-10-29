---
name: ez-chrome-extension-dev
description: Develop and test unpacked Chrome extensions with an extension-owned reload control, safe host-page refreshes, and verification of the loaded build. Use when extension changes need a repeated edit/build/reload/test loop; exclude installing third-party extensions and unrelated browser automation.
---

# Easy Chrome extension development

Make the development feedback loop agent-operable through the extension's own UI. Prefer a **Reload extension** button in an existing popup so routine changes do not require repeated user trips to the Extensions page.

## Establish the loop

Inspect the manifest, build command, loaded unpacked directory, existing popup, and current reload tooling. Keep a working framework hot-reload setup when it already handles the task. Build into the directory Chrome actually loads; editing source alone does not update generated bundles.

Use supported browser or computer-use controls to open the ordinary extension popup and click its button. Check the available tool's capabilities before assuming it can reach browser toolbar UI. Do not replace an extension action's existing behavior just to add a popup; use an existing extension-owned page where practical.

For an already loaded unpacked extension, changes to its existing popup HTML and JavaScript are read when the popup opens. Build if necessary, close it, and reopen it to expose a newly added reload button without first reloading the extension. Changing the manifest's popup declaration still requires an initial extension reload. See Chrome's [component reload guidance](https://developer.chrome.com/docs/extensions/get-started/tutorial/hello-world#when-to-reload-the-extension).

## Add the control only when needed

Integrate with the existing popup framework and state handling; reuse a suitable control instead of adding a duplicate. A small adaptable implementation is in [references/reload-button.md](references/reload-button.md); read it when adding the button.

- Show the control only when `chrome.management.getSelf()` reports `installType === "development"`. Hide it if the check fails or the API is unavailable, and recheck on activation.
- Call `chrome.runtime.reload()` from the extension's own code. It returns `void`; a returned call is not proof that the new build loaded. Neither this call nor `management.getSelf()` requires adding the `management` permission. Preserve existing permissions.
- Use a `type="button"` control outside settings forms. Guard repeated activation and pending saves or unsaved popup edits. Lock conflicting controls while reloading, recheck pending work after asynchronous checks, and recover the UI on failure.
- Keep the change small. A reload button does not require a file-watching server, page-wide observer, polling, click replay, or automatic host-tab refresh.

The relevant API contracts are [management.getSelf](https://developer.chrome.com/docs/extensions/reference/api/management#method-getSelf), [development installation type](https://developer.chrome.com/docs/extensions/reference/api/management#type-ExtensionInstallType), and [runtime.reload](https://developer.chrome.com/docs/extensions/reference/api/runtime#method-reload). Unpacked reloads can also fire `runtime.onInstalled` with an update reason; preserve settings and check existing update handlers if reloading has unexpected side effects.

## Run an edit cycle

1. Make the requested change, build, and run the repository's relevant checks.
2. Determine the refresh scope:

   | Changed component | Refresh needed |
   | --- | --- |
   | Popup-only HTML, CSS, or JavaScript | Close and reopen the popup after rebuilding. |
   | Options or another extension page | Reload that page after rebuilding. |
   | Manifest or service worker | Reload the extension; refresh affected content-script host pages before testing their integration. |
   | Content scripts or their injected styles | Reload the extension, then refresh the affected host page. |

3. Before a disruptive reload, let active edits and saves settle. If unsaved state cannot be confirmed safe, pause that refresh and report what prevents it. Never discard work or automatically refresh an actively edited page.
4. Open the popup and activate **Reload extension** when required. Then refresh the relevant host tab with the browser tool's supported reload/navigation control. Extension reload alone does not replace content scripts already running in an open page.
5. Verify the new build in the context being tested. Prefer an existing unique build marker; otherwise add a small build identifier to extension-owned diagnostics or UI. Compare it with the built output through supported observation. A current popup identifies that popup's files, not the host page's content-script version; verify a content-script marker or fresh diagnostic reply for host-page work.
6. Exercise the changed behavior and relevant navigation or state transitions. Report the loaded identity, checks performed, and any states that remain unverified. A successful build or button click alone is not live acceptance.

## Handle unavailable access precisely

This workflow needs an installed unpacked extension and a supported way to reach its UI. Initial installation, a missing popup declaration, or unavailable toolbar automation may require a small manual step. State the exact blocker and request only that step when necessary; resume the automated loop afterward.

An ordinary extension popup calling its own API does not require access to `chrome://extensions`. If tools cannot reach the popup or a policy blocks an action, do not route around the restriction with injected browser JavaScript, hidden debugging access, or another unapproved channel. Report the limitation rather than promising that every environment supports the same automation.
