# droidctl

A helper to control Android devices with scripts.
Combines `uiautomator2`, `adbutils` and `fdroidcl` powers
+ some more high-level interfaces.
See examples in `examples` to get the idea of what I'm aiming for.

Invocation examples:
* `droidctl examples/trivial.py` if installed
* `python3 . run examples/trivial.py` from a checkout
* `nix run . -- run examples/trivial.py` from a checkout
* `droidctl --preamble preamble.py examples/trivial.py` using a shared preamble
* `droidctl --device SERIAL examples/trivial.py` against specific device

I hope to use it to automate configuring my Android devices.
Is there something like Ansible for phones? Let me know if there is.
