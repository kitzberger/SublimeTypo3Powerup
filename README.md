# TYPO3 ExtPath Highlighter

Plugin for Sublime Text 2 and 3.

## Summary

* Highlights TYPO3 paths like EXT:my\_extension/Resources/Private/Language/locallang\_db.xlf
* Provides a command to open such a file (can be triggered by click or shortcut)

## Key binding

```User/Default (Linux).sublime-keymap
{ "keys": ["ctrl+alt+enter"], "command": "open_typo3_ext_path_under_cursor" }
```

## Mouse binding

```User/Default (Linux).sublime-mousemap
[
    {
        "button": "button1",
        "count": 1,
        "modifiers": ["ctrl"],
        "press\_command": "drag\_select",
        "command": "open\_typo3\_ext\_path\_under\_cursor"
    }
]
```

## Thanks

Kudos go to Leonid Shevtsov for creating [ClickableUrls_SublimeText](https://github.com/leonid-shevtsov/ClickableUrls_SublimeText).
