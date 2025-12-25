# Component Organisation Strategies: Type vs. Domain

A comprehensive guide to organizing components in Python/Reflex applications.

---

## The Fundamental Problem

**You cannot optimize for multiple access patterns with a single hierarchy.** When organizing components, you face an inherent trade-off:

- **Component Type First** (`_button_*`, `_form_*`, `_input_*`) - Easy to find all buttons, inputs, etc.
- **Feature Domain First** (`_template_*`, `_note_*`, `_job_*`) - Easy to find all components for a feature

This is an **unsolvable hurdle** in single-hierarchy systems. You can only pick one primary organization axis.

---

## Solution 1: Directory Structure + Index Files (Most Common)

Use **directories for feature domains** and **filenames for component types**.

### Example Structure:
```
components/
├── jobs/
│   ├── detail/
│   │   ├── buttons.py          # All detail page buttons
│   │   ├── forms.py            # All detail page forms
│   │   ├── templates.py        # Template-related components
│   │   ├── dialogs.py          # Dialog components
│   │   └── __init__.py         # Barrel exports
│   ├── list/
│   │   ├── cards.py
│   │   └── filters.py
│   └── __init__.py
├── shared/
│   ├── buttons.py               # Shared button components
│   ├── inputs.py
│   └── status_badge.py
└── templates/
    ├── form.py
    └── list.py
```

### Barrel Export Pattern

In `jobs/detail/__init__.py`:
```python
"""
Job Detail Page Components

Provides both feature-domain and component-type access patterns.
"""

# Feature-domain exports (primary)
from .buttons import (
    button_save,
    button_cancel,
    button_edit,
    button_delete_job,
)
from .forms import (
    note_input_form,
    template_selection_form,
)
from .templates import (
    template_selector_list,
    template_search_input,
)
from .dialogs import (
    delete_confirmation_dialog,
    view_all_templates_dialog,
)

# Component-type grouped exports (secondary - for refactoring)
__all_buttons__ = [
    button_save,
    button_cancel,
    button_edit,
    button_delete_job
]
__all_forms__ = [note_input_form, template_selection_form]
__all_dialogs__ = [delete_confirmation_dialog, view_all_templates_dialog]

# Make everything available
__all__ = [
    # Buttons
    'button_save', 'button_cancel', 'button_edit', 'button_delete_job',
    # Forms
    'note_input_form', 'template_selection_form',
    # Templates
    'template_selector_list', 'template_search_input',
    # Dialogs
    'delete_confirmation_dialog', 'view_all_templates_dialog',
    # Grouped exports
    '__all_buttons__', '__all_forms__', '__all_dialogs__',
]
```

### Usage:
```python
# Domain-based import (most common)
from components.jobs.detail import button_save, template_selector_list

# Type-based refactoring (when needed)
from components.jobs.detail import __all_buttons__
for btn in __all_buttons__:
    apply_consistent_styling(btn)
```

---

## Solution 2: Component Catalog (Documentation Layer)

Create a `COMPONENTS.md` mapping file that provides both views:

```markdown
# Component Catalog

## By Type

### Buttons (15 total)
- `button_save` - jobs/detail/buttons.py:12 - Saves status changes
- `button_cancel` - jobs/detail/buttons.py:24 - Cancels edit mode
- `button_edit` - jobs/detail/buttons.py:36 - Enables status editing
- `button_template_selector` - jobs/detail/templates.py:48 - Quick template insert
- `button_template_insert` - jobs/detail/templates.py:60 - Inserts in dialog
- `button_dialog_close` - jobs/detail/dialogs.py:72 - Closes dialog

### Forms (8 total)
- `note_input_textarea` - jobs/detail/forms.py:15 - Note entry field
- `template_search_input` - jobs/detail/templates.py:27 - Template search
- `status_dropdown` - jobs/detail/forms.py:40 - Status selector

### Text Components (12 total)
- `job_title_heading` - jobs/detail/text.py:10 - Job title display
- `no_notes_placeholder` - jobs/detail/text.py:22 - Empty state text
- `template_name_text` - jobs/detail/templates.py:34 - Template name

## By Feature Domain

### Template System (18 components)
**Files:** `jobs/detail/templates.py`, `jobs/detail/dialogs.py`

#### Buttons (5)
- `button_template_selector` - Quick insertion from list
- `button_template_insert` - Insert in "View All" dialog
- `button_view_all` - Opens full template dialog
- `template_settings_tooltip` - Settings icon link

#### Forms/Inputs (3)
- `template_search_input` - Search templates by name/content
- `template_selector_list` - Scrollable template buttons
- `note_form_template_selection` - Full template section

#### Display (4)
- `template_name_text` - Template name display
- `template_content_text` - Template content preview
- `template_list_item` - Single template in dialog
- `view_all_templates_dialog` - Full dialog component

### Status Editing (6 components)
**Files:** `jobs/detail/buttons.py`, `jobs/detail/forms.py`

- `button_save` - Commits status change
- `button_cancel` - Cancels edit mode
- `button_edit` - Enables editing
- `status_dropdown` - Status selector
- `company_and_status` - Header with editable badge
- `job_information_card` - Main container

### Note Management (8 components)
**Files:** `jobs/detail/forms.py`, `jobs/notes.py`

- `note_input_textarea` - Note entry field
- `note_history_list` - Timeline of notes
- `note_history_no_notes_text` - Empty state
- `section_note_history` - History card
- `section_note_form` - Add note card
- `timeline` - Single note display
- `timeline_bullet` - Timeline marker
- `timeline_timestamp` - Note timestamp
```

### Auto-Generation Script

Create `scripts/generate_catalog.py`:
```python
import ast
import os
from pathlib import Path

def extract_component_info(file_path):
    """Parse Python file and extract component function information."""
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())

    components = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Extract function name, line number, docstring
            name = node.name
            line_no = node.lineno
            docstring = ast.get_docstring(node) or "No description"

            # Parse docstring for emoji and description
            lines = docstring.split('\n')
            emoji = lines[0].split()[0] if lines else ""
            desc = lines[0].replace(emoji, "").strip() if lines else ""

            components.append({
                'name': name,
                'file': str(file_path),
                'line': line_no,
                'emoji': emoji,
                'description': desc
            })

    return components

def generate_catalog(components_dir):
    """Generate COMPONENTS.md from all component files."""
    # Scan all .py files in components/
    # Extract component info
    # Group by type (prefix-based) and domain (directory-based)
    # Generate markdown
    pass

if __name__ == "__main__":
    generate_catalog("applog/components/")
```

Run after each major change: `python scripts/generate_catalog.py`

---

## Solution 3: Storybook / Interactive Component Browser

**Storybook** is the industry-standard tool for component catalogs in JavaScript/React. For Python/Reflex, you can create a similar system.

### What Storybook Provides:

1. **Visual Component Gallery**
   - See all components rendered in isolation
   - Interactive playground to test props/states
   - Searchable by name, type, or feature

2. **Live Documentation**
   - Auto-generated from docstrings and type hints
   - Shows component API (parameters, return types)
   - Includes usage examples

3. **Multiple Organisation Views**
   - Sidebar tree organised by feature domain
   - Tag-based filtering by component type
   - Search across all metadata

4. **Testing Playground**
   - Adjust props in real-time
   - See component in different states
   - Test edge cases visually

### Reflex-Specific Implementation

Create `storybook.py` in your project:

```python
"""
Component Storybook - Interactive component catalog
Run: reflex run --env storybook
"""
import reflex as rx
from typing import List, Dict
from components.jobs import detail, card, form
from components.shared import buttons, inputs
from components.templates import manager

class StorybookState(rx.State):
    """State for component browser."""

    selected_component: str = ""
    search_query: str = ""
    filter_type: str = "all"  # all, button, form, dialog, etc.
    filter_domain: str = "all"  # all, jobs, templates, shared

    # Component registry
    components: List[Dict] = [
        {
            "name": "button_save",
            "module": "jobs.detail.buttons",
            "type": "button",
            "domain": "jobs/detail",
            "tags": ["status-editing", "interactive"],
            "description": "Saves status changes",
        },
        # ... more components
    ]

    @rx.var
    def filtered_components(self) -> List[Dict]:
        """Filter components based on search and filters."""
        result = self.components

        if self.search_query:
            result = [
                c for c in result
                if self.search_query.lower() in c["name"].lower()
                or self.search_query.lower() in c["description"].lower()
            ]

        if self.filter_type != "all":
            result = [c for c in result if c["type"] == self.filter_type]

        if self.filter_domain != "all":
            result = [c for c in result if c["domain"].startswith(self.filter_domain)]

        return result

def component_preview_card(component: Dict) -> rx.Component:
    """Render a component preview card."""
    return rx.card(
        rx.vstack(
            rx.heading(component["name"], size="4"),
            rx.badge(component["type"]),
            rx.text(component["description"], size="2"),
            rx.divider(),
            # Render actual component in isolation
            rx.box(
                # eval(f"{component['module']}.{component['name']}()")
                # ^ Dynamic component rendering
                padding="1em",
                border=f"1px solid {rx.color('gray', 6)}",
            ),
            spacing="2",
        ),
        width="300px",
    )

def storybook_page() -> rx.Component:
    """Main storybook interface."""
    return rx.container(
        rx.hstack(
            # Sidebar with filters
            rx.vstack(
                rx.heading("Component Browser", size="6"),
                rx.input(
                    placeholder="Search components...",
                    value=StorybookState.search_query,
                    on_change=StorybookState.set_search_query,
                ),
                rx.select(
                    ["all", "button", "form", "dialog", "input"],
                    value=StorybookState.filter_type,
                    on_change=StorybookState.set_filter_type,
                ),
                rx.select(
                    ["all", "jobs", "templates", "shared"],
                    value=StorybookState.filter_domain,
                    on_change=StorybookState.set_filter_domain,
                ),
                width="250px",
            ),

            # Component grid
            rx.box(
                rx.grid(
                    rx.foreach(
                        StorybookState.filtered_components,
                        component_preview_card,
                    ),
                    columns="3",
                    spacing="4",
                ),
                flex="1",
            ),

            spacing="4",
        ),
        padding="2em",
    )
```

### Benefits:
- **Dual Navigation**: Filter by type OR domain simultaneously
- **Visual Testing**: See components in isolation
- **Living Documentation**: Always up-to-date
- **Onboarding Tool**: New developers explore components visually

---

## Solution 4: IDE Features (Pragmatic Reality)

Most professional developers rely on IDE tooling:

### VSCode Symbol Search
- `Cmd+Shift+O` → Search all functions in current file
- `Cmd+T` → Search all functions across workspace
- Type `button` → See all button functions instantly

### PyCharm/IntelliJ
- `Cmd+O` → Go to symbol
- `Cmd+Shift+F` → Find in path with regex
- Structure view shows all functions grouped by file

### Tag-Based Search
Add structured tags to docstrings:

```python
def _button_save(state: rx.State):
    """
    💾 Saves status changes

    Tags: #button #status-editing #job-detail #interactive
    Category: buttons
    Domain: jobs/detail
    """
    pass
```

Then search: `#button` finds all buttons, `#status-editing` finds all status components.

---

## Solution 5: Hybrid Naming (Current Approach)

For **single-file components** (before splitting), use hybrid naming:

### Pattern:
```python
# Component type prefix for quick grouping
_button_save
_button_cancel
_button_edit
_button_dialog_close

# Feature-specific components with descriptive names
_button_template_selector
_button_template_insert

# Sub-feature grouping with common prefix
_template_selector_list
_template_search_input
_template_settings_tooltip

# Formatting dictionaries always prefixed
_formatting_button_section
_formatting_template_list
_formatting_dialog_content
```

### Why This Works:
- `_button_*` groups all buttons → Type-based access
- `_template_*` groups template components → Domain-based access
- Both accessible via IDE search
- Scales well up to ~100 components per file

### Add File Header Documentation:
```python
"""
Job Detail Page Components

Component Organisation:

By Type:
  Buttons: _button_save, _button_cancel, _button_edit, _button_delete_job,
           _button_view_all, _button_template_selector, _button_template_insert,
           _button_dialog_close
  Inputs: _template_search_input, _note_input_textarea
  Text: _job_title, _template_name_text, _template_content_text,
        _no_notes_placeholder, _job_not_found_text
  Sections: _section_details_grid, _section_note_history, _section_note_form
  Dialogs: _delete_confirmation_dialog, _view_all_templates_dialog
  Formatting: _formatting_* (all styling dictionaries)

By Feature Domain:
  Status Editing:
    _button_save, _button_cancel, _button_edit, _status_dropdown,
    _company_and_status

  Template System:
    _button_template_selector, _button_template_insert, _button_view_all,
    _template_search_input, _template_selector_list, _template_settings_tooltip,
    _template_list_item, _view_all_templates_dialog, _note_form_template_selection

  Note Management:
    _note_input_textarea, _note_history_list, _section_note_history,
    _section_note_form, _add_note_section, _button_add_note

  Grid Details:
    _grid_location, _grid_applied_status, _grid_salary_conditional,
    _grid_url_conditional, _section_details_grid

  Dialogs:
    _delete_confirmation_dialog, _view_all_templates_dialog,
    _dialog_close_section, _button_dialog_close
"""
```

---

## When to Use Each Approach

### Single File (<100 components)
✅ **Hybrid naming + header documentation**
- Fast to implement
- IDE search works great
- No overhead

### Medium Project (100-500 components)
✅ **Directory structure + barrel exports**
- Feature folders for domains
- Component type files within folders
- `__init__.py` provides both access patterns

### Large Project (500+ components)
✅ **All of the above + Storybook**
- Directory structure
- Auto-generated catalog (COMPONENTS.md)
- Interactive component browser
- CI/CD integration for docs

---

## Production Reality Check

**What professional teams actually do:**

1. **Directory structure** for feature organisation
2. **File names** for component type grouping
3. **IDE search** for day-to-day work (90% of lookups)
4. **Storybook/Catalog** for onboarding and visual testing
5. **Documentation** for architectural decisions

**The 80/20 rule:** Good directory structure + IDE search solves 80% of problems. The remaining 20% (onboarding, refactoring, auditing) benefits from catalogs and Storybook.

---

## Recommendation for This Project

### Current Phase (Refactoring in Progress):
✅ Keep hybrid naming (`_button_*`, `_template_*`)
✅ Add file header documentation (shown above)
✅ No additional tooling needed

### Next Phase (After File Splitting):
✅ Use directory structure:
```
components/jobs/detail/
├── buttons.py
├── forms.py
├── templates.py
└── __init__.py  # Barrel exports
```

### Future (If Team Grows):
✅ Add auto-generated COMPONENTS.md
✅ Consider Storybook-style browser

**Don't over-engineer early.** The hybrid approach is perfect for where you are now.

---

## Summary

**The Problem**: Cannot optimize for both type-based AND domain-based access with a single hierarchy.

**The Solutions** (in order of complexity):
1. Hybrid naming (current) - Best for <100 components
2. Directory structure + barrel exports - Best for 100-500 components
3. Component catalog - Additional documentation layer
4. IDE features - Pragmatic daily workflow
5. Storybook - Best for 500+ components, team onboarding

**Key Insight**: Start simple, evolve as needed. Most projects never need more than directory structure + IDE search.
