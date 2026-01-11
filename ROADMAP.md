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

### 8. Location Autocomplete (Type-ahead)

**Requirement:** Start typing location → see suggestions from existing locations in database → can still type custom value for new locations.

**Implementation:**
1. Add computed property: `@rx.var def unique_locations(self) -> List[str]` that extracts all unique location values from `self.jobs`
2. Use Reflex autocomplete pattern with `rx.input()` + suggestions list
3. Allow free text input for locations not in list

**Target locations (most common):**
- Geneva
- Lausanne
- Nyon

**Files to modify:**
- `applog/applog.py` (add `unique_locations` computed var to State)
- `applog/components/jobs/add_job.py` (replace plain input with autocomplete component)

**Effort:** 30-45 minutes
**Complexity:** MEDIUM

**Future enhancement:** Could add similar autocomplete for job_title and company_name fields.

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

**Session 2** (~30-45 minutes): **Phase 3**
Implement location autocomplete (item 8). Focused session on single feature.

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

**Last Updated:** 2026-01-11
**Status:** Phase 1 Complete ✅ | Phase 2 Complete ✅
