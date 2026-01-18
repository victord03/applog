# AppLog - Feature Roadmap

## Overview

This document tracks planned features and improvements for the AppLog job application tracker, organized by priority and complexity. Features are sorted with the most important and least complex items first.

**Total Estimated Time:** ~2.5-3.5 hours across 3 focused sessions

---

## Phase 1: Critical Bug Fixes ⚠️

**Priority:** HIGH | **Total Effort:** ~20 minutes

These are bugs that affect user experience and should be fixed immediately.

### 1. Reset Edit Mode on Page Exit

**Issue:** When editing job status on detail page, then exiting without saving, the edit mode persists on re-entry.

**Solution:**
- Add state reset in `load_index_page()` handler
- Set `status_edit_mode = False` when leaving detail page

**Files modified:**
- `applog/applog.py` (State class, `load_index_page()` method, line 233)

**Effort:** 5 minutes
**Complexity:** MINIMAL
**Status:** ✅ COMPLETED

---

### 2. Smart Cancel with Confirmation Dialog

**Issue:** Abandoned job creation forms leave fields populated even after navigating away, requiring manual clearing.

**Solution Implemented:**
- Added smart confirmation dialog when exiting form with unsaved data
- Both "Cancel" and "Back to List" buttons trigger confirmation check
- If form has data → show dialog with "Stay" / "Discard" options
- If form is empty → navigate directly without interruption
- Form auto-clears on page load to ensure clean slate

**Files modified:**
- `applog/components/jobs/add_job.py` (modified Cancel/Back buttons, added confirmation dialog component)
- `applog/applog.py` (added `show_cancel_job_dialog` state, `handle_cancel_job_creation()`, `confirm_cancel_job()`, `dismiss_cancel_dialog()` handlers, updated `load_add_job_page()` to call `clear_form()`)

**Effort:** 15 minutes (more than estimated due to dialog implementation)
**Complexity:** MINIMAL-MEDIUM
**Status:** ✅ COMPLETED

---

### 3. Auto-populate Application Date to Today

**Issue:** Application date field defaults to empty, requires manual entry every time.

**Solution Implemented:**
- Modified `clear_form()` to set `form_application_date = datetime.today().strftime('%Y-%m-%d')`
- Uses ISO format (YYYY-MM-DD) required by HTML5 date inputs
- User can still modify the date if needed
- Date populates on page load since `load_add_job_page()` calls `clear_form()`

**Files modified:**
- `applog/applog.py` (`clear_form()` method, line 325)

**Effort:** 5 minutes
**Complexity:** MINIMAL
**Status:** ✅ COMPLETED

**Note:** Initial attempt to use class-level default failed because defaults evaluate once at startup. Moving to `clear_form()` ensures fresh date on each page load.

---

## Phase 2: Quick Wins 🎯

**Priority:** MEDIUM-HIGH | **Total Effort:** ~25 minutes

High-value improvements with minimal implementation effort.

### 4. Sort Jobs by Application Date (Newest First)

**Current State:** Jobs load in database order (unspecified sorting).

**Solution:**
- Add `.order_by(JobApplication.application_date.desc())` to SQLAlchemy query in `load_jobs_from_db()`
- Alternative: Sort in Python after query: `sorted(jobs, key=lambda x: x['application_date'], reverse=True)`

**Recommendation:** Database-level sorting is more efficient.

**Files to modify:**
- `applog/applog.py` (`load_jobs_from_db()` method)

**Effort:** 5 minutes
**Complexity:** LOW
**Status:** ✅ COMPLETED

**Note:** Can add multi-sort options later (toggle between created_at, updated_at, application_date).

---

### 5. Hide Inactive Job Statuses by Default

**Requirement:** Always hide jobs with statuses "Rejected", "Withdrawn", and "No Response" from the main screen. These are not useful for an active application tracker focused on in-progress applications.

**Behavior:**
- Main screen shows only active applications (Applied, Screening, Interview, Offer, Accepted)
- Inactive statuses still accessible via status filter if explicitly selected
- Counter reflects only visible (non-hidden) jobs

**Solution:**
- Modify `filtered_jobs` property to exclude inactive statuses by default
- Only show inactive statuses when specifically selected via status filter

**Files to modify:**
- `applog/applog.py` (`filtered_jobs` computed property)

**Effort:** 10 minutes
**Complexity:** LOW
**Status:** ✅ COMPLETED

---

### 6. Filter-Aware Application Counter

**Issue:** Total applications counter always shows full count, even when filters are active.

**Solution:**
- Change counter to show: "Showing X of Y applications"
- Use `len(state.filtered_jobs)` for X, `state.total_jobs_count` for Y

**Implementation:**
- Updated display to show both filtered and total counts
- Counter now accurately reflects active filters

**Files modified:**
- `applog/components/main/index_page.py` (`_main_page_total_applications_display()` function)

**Effort:** 5 minutes
**Complexity:** MINIMAL
**Status:** ✅ COMPLETED

---

### 7. Remove Notes from Job Creation Form

**Rationale:** Notes are for tracking progress AFTER applying (recruiter responses, interview updates). At creation time, there's nothing to note yet. Keeps creation form focused and simple.

**Current workflow is fine:** Create job → View details → Add notes with templates

**Solution:**
- Remove notes textarea from add_job form
- Remove `form_notes` from State class
- Remove notes handling from `handle_submit()`
- Update docstrings

**Files modified:**
- `applog/components/jobs/add_job.py` (commented out notes field component, line 297)
- `applog/applog.py` (commented out `form_notes` state variable and submit handler references, lines 327 and 295)

**Effort:** 5 minutes
**Complexity:** MINIMAL
**Status:** ✅ COMPLETED

**Note:** Code commented rather than deleted for potential future re-implementation as optional/expandable field.

---

## Phase 3: Medium Features 🔧

**Priority:** MEDIUM | **Total Effort:** ~30-45 minutes

Valuable features requiring moderate implementation effort.

### 8. Location Dropdown with "Other" Option

**Requirement:** Eliminate typing for the 5 most common locations (Geneva, Lausanne, Nyon, Gland, Bern) while allowing custom text input for edge cases.

**UX Decision:** Dropdown with hardcoded list + "Other" option that reveals text input field below when selected.

**Rationale:**
- 95% of applications go to the same 5 regions → zero typing optimization
- Hardcoded list prevents typo accumulation and ensures consistent data
- "Other" option handles rare edge cases without restricting flexibility
- Conditional text input uses proven `rx.cond()` pattern from codebase

**Implementation Steps:**

1. **Update State class** (`applog/applog.py`)
   - Add state variable: `form_location_is_other: bool = False` (tracks if "Other" is selected)
   - Keep existing: `form_location: str = ""` (stores final location value)
   - Update `clear_form()` method to reset both location-related state variables

2. **Create location selection handler** (`applog/applog.py`)
   - Add method: `handle_location_change(value: str)`
     - If value == "Other": set `form_location_is_other = True`, clear `form_location`
     - Else: set `form_location = value`, set `form_location_is_other = False`

3. **Replace location input component** (`applog/components/jobs/add_job.py`)
   - Modify `_optional_field_location()` function
   - Replace `rx.input()` with `rx.select()` containing hardcoded options:
     - `["Geneva", "Lausanne", "Nyon", "Gland", "Bern", "Other"]`
   - Wire to new handler: `on_change=state.handle_location_change`
   - Add conditional text input below using `rx.cond(state.form_location_is_other, ...)`
   - Text input should update `state.form_location` directly

4. **Pattern References (already in codebase):**
   - **Dropdown pattern**: See `_optional_field_status()` in `add_job.py:122-149`
   - **Conditional rendering**: See `_optional_field_message_display()` in `add_job.py:229-251`
   - **State handler pattern**: See existing `set_*` methods in State class

**Files to modify:**
- `applog/applog.py` (State class: add `form_location_is_other` state, add `handle_location_change()` handler, update `clear_form()`)
- `applog/components/jobs/add_job.py` (replace `_optional_field_location()` implementation)

**Testing checklist:**
- [ ] Dropdown displays all 5 locations + "Other"
- [ ] Selecting a preset location (e.g., "Geneva") sets `form_location` correctly
- [ ] Selecting "Other" reveals text input field below
- [ ] Typing in "Other" text input updates `form_location`
- [ ] Form submission saves correct location to database
- [ ] Switching from "Other" back to preset hides text input
- [ ] `clear_form()` resets dropdown and "Other" state

**Effort:** 15-20 minutes
**Complexity:** LOW-MEDIUM
**Status:** ✅ COMPLETED

**Implementation Details:**
- Added `form_location_is_other: bool` state variable to track "Other" selection
- Created `handle_location_change()` handler to manage dropdown selection logic
- Updated `clear_form()` to reset location-related state variables
- Replaced `rx.input()` with `rx.select()` dropdown containing 5 preset locations + "Other"
- Added conditional `rx.input()` that appears only when "Other" is selected
- Added validation to prevent submission if "Other" selected but no custom location entered

**Files Modified:**
- `applog/applog.py` (lines 56, 277-280, 322, 328-339)
- `applog/components/jobs/add_job.py` (lines 102-142)

**Future enhancement:** Could add similar dropdown for job_title and company_name fields if repetitive data patterns emerge.

---

## Phase 4: Bigger Features 🚀

**Priority:** MEDIUM-LOW | **Total Effort:** ~1-2 hours

More complex features requiring significant implementation.

### 9. Edit Job Details

**Current State:** Only job status can be edited from detail page.

**Requirement:** Full edit capability for all job fields (company, title, URL, location, description, salary, date).

**Implementation:**
1. Add "Edit Job" button to job detail page
2. Create edit mode toggle (view mode ↔ edit mode)
3. Pre-populate form fields with current job data when entering edit mode
4. Add `handle_edit_job()` handler in State class
5. Use existing `update_job()` service function (already implemented in `job_service.py`)
6. Add save/cancel buttons in edit mode
7. Reset edit mode on save/cancel

**Design decision:** Reuse add_job form components vs. create dedicated edit form
- **Option A:** Create separate `edit_job.py` component (cleaner separation)
- **Option B:** Make `add_job.py` work in both create/edit modes (DRY principle)

**Recommendation:** Option A (separate component) - cleaner architecture, easier to maintain.

**Files to modify:**
- `applog/components/jobs/job_detail.py` (add Edit button, edit mode UI)
- `applog/applog.py` (add edit-related state variables, `handle_edit_job()` handler)
- Potentially create: `applog/components/jobs/edit_job.py` (if going with Option A)

**Effort:** 1-2 hours
**Complexity:** MEDIUM-HIGH

**Service layer support:** Already complete - `update_job()` fully implemented in `job_service.py:168-203`.

---

## Execution Strategy

### Recommended Approach

**Session 1** (~55 minutes): **Phase 1 + Phase 2** ✅ COMPLETED
Implement all quick wins and bug fixes (items 1-7). Dramatically improves UX with minimal effort.
- ✅ Phase 1 complete (items 1-3)
- ✅ Phase 2 complete (items 4-7)

**Session 2** (~30-45 minutes): **Phase 3** ✅ COMPLETED
Implement location dropdown with "Other" option (item 8). Focused session on single feature.

**Session 3** (~1-2 hours): **Phase 4**
Implement full job editing (item 9). Larger feature requiring focused time.

---

## Future Considerations (v2.0+)

Items from original README that were deferred:

- Multi-field autocomplete (job title, company name)
- Advanced sorting options (toggle between sort fields)
- Similar job detection (same job from different sources)
- Email notifications for follow-ups
- URL scraping to auto-populate job details

---

## Notes

- All features follow existing architecture patterns (State management, service layer, component structure)
- Existing code is well-refactored and modular - adding features is straightforward
- Test coverage should be maintained/extended as features are added
- Commit after each phase for clean git history

---

**Last Updated:** 2026-01-18
**Status:** Phase 1 Complete ✅ | Phase 2 Complete ✅ | Phase 3 Complete ✅
