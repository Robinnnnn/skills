# Development reload button

Adapt this example to the existing popup rather than installing a second state system. It uses the promise-based Chrome extension APIs. Keep the script in an external popup JavaScript file, loaded after its markup, to respect extension CSP.

Place the initially hidden button outside settings forms:

```html
<button id="reload-extension" type="button" hidden>Reload extension</button>
<span id="reload-status" role="status" aria-live="polite"></span>
```

The helper expects actual application state callbacks: `hasPendingChanges()` reports both in-flight saves and unsaved edits; `setReloadLocked(true)` prevents new changes and saves until unlocked. Incorporate the lock into existing disabled/render logic and event guards so another render cannot accidentally re-enable editing. Mount once, or use the returned cleanup function in the framework's unmount lifecycle.

```js
function installDevelopmentReload({
  button, status, hasPendingChanges, setReloadLocked,
}) {
  let development = false;
  let reloading = false;
  let disposed = false;
  button.hidden = true;

  async function isDevelopment() {
    try {
      return (await chrome.management?.getSelf?.())?.installType === "development";
    } catch {
      return false;
    }
  }

  async function reload() {
    if (disposed || !development || reloading || hasPendingChanges()) return;
    reloading = true;
    button.disabled = true;
    setReloadLocked(true);
    status.textContent = "Reloading…";
    try {
      development = await isDevelopment();
      if (disposed) return;
      button.hidden = !development;
      if (!development) throw new Error("Development reload unavailable");
      if (hasPendingChanges()) throw new Error("Pending changes");
      chrome.runtime.reload();
      // Returns void: keep controls locked until this context closes.
    } catch {
      if (disposed) return;
      reloading = false;
      button.disabled = false;
      setReloadLocked(false);
      status.textContent = "Reload unavailable. Finish saving, then reopen the popup to retry.";
    }
  }

  button.addEventListener("click", reload);
  void isDevelopment().then((value) => {
    if (disposed) return;
    development = value;
    button.hidden = !development;
  });

  return () => {
    disposed = true;
    button.removeEventListener("click", reload);
    if (reloading) setReloadLocked(false);
  };
}
```

Call the helper with the popup's button/status elements and existing state callbacks. In an app with no editable popup state, the callbacks can report no pending changes and need no additional lock machinery. Do not change the manifest permissions for this helper.

Check the integration with a development install, a non-development result, a rejected self-check, repeated clicks, and a pending save. Verify failures unlock the popup and leave settings intact. Mock API checks can cover these branches, but still exercise the real popup and verify the loaded build after the host page refresh.
