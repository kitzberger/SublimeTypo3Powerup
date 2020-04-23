# TYPO3 ExtPath Highlighter

Plugin for Sublime Text 3.

## Features

### Highlights TYPO3 paths

* Highlights TYPO3 paths like EXT:my\_extension/Resources/Private/Language/locallang\_db.xlf
* Provides a command to open such a file (can be triggered by click or shortcut)

### Toggle fluid syntaxes

* Toggles between classical tag style and inline style of fluid viewhelpers
* Provides a command to transform tags

## Key binding

```User/Default (Linux).sublime-keymap
{ "keys": ["ctrl+alt+enter"], "command": "open_typo3_ext_path_under_cursor" },
{ "keys": ["ctrl+alt+shift+enter"], "command": "toggle_typo3_fluid_syntax_under_cursor" }
```

## Mouse binding

```User/Default (Linux).sublime-mousemap
[
    {
        "button": "button1",
        "count": 1,
        "modifiers": ["ctrl"],
        "press_command": "drag_select",
        "command": "open_typo3_ext_path_under_cursor"
    }
]
```

## Thanks

Kudos go to Leonid Shevtsov for creating [ClickableUrls_SublimeText](https://github.com/leonid-shevtsov/ClickableUrls_SublimeText).
