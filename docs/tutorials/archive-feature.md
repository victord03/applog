# Archive Feature Implementation Guide

## Feature Overview
Archive jobs with "Rejected" or "Withdrawn" status to keep the main page clean. Users can view archived jobs on a separate `/archive` page.

**Difficulty:** 1/3 (Simple - great practice with `@rx.var`)

## Why This Is Good @rx.var Practice
- Learn to create computed variables that filter data
- Understand dependency tracking (when `self.jobs` changes, computed vars auto-update)
- Practice the proper Reflex pattern for data transformation
- See how computed vars eliminate manual refresh logic

---

## Implementation Steps

### Step 1: Create Computed Variables for Active/Archived Jobs

**Location:** `applog/applog.py` in the `State` class (after `selected_job_notes`)

**Concept:** Split `self.jobs` into two categories based on status

**Code Pattern:**
```python
@rx.var
def active_jobs(self) -> List[Dict]:
    """Jobs excluding Rejected/Withdrawn."""
    # Return list comprehension filtering self.jobs
    # Exclude jobs where status is "Rejected" or "Withdrawn"
    pass

@rx.var
def archived_jobs(self) -> List[Dict]:
    """Jobs with Rejected/Withdrawn status."""
    # Return list comprehension filtering self.jobs
    # Include ONLY jobs where status is "Rejected" or "Withdrawn"
    pass
```

**Hints:**
- Use list comprehension: `[j for j in self.jobs if ...]`
- Check `j["status"]` against the strings "Rejected" and "Withdrawn"
- Use `not in` for active_jobs, `in` for archived_jobs

---

### Step 2: Update Main Page to Use Active Jobs Only

**Location:** `applog/applog.py` in `filtered_jobs` computed var (around line 152)

**Concept:** Change the starting point for filtering from all jobs to only active jobs

**Current Code:**
```python
@rx.var
def filtered_jobs(self) -> List[Dict]:
    """Get filtered jobs based on search and filter criteria."""
    result = self.jobs  # ← Change this line
    # ... rest of filtering logic
```

**Change To:**
```python
result = self.active_jobs  # Now starts with active jobs only
```

**Also Update:** The `total_jobs_count` computed var (around line 147)
```python
@rx.var
def total_jobs_count(self) -> int:
    """Get total number of job applications."""
    return len(self.active_jobs)  # Changed from self.jobs
```

---

### Step 3: Create Archive Page

**Location:** `applog/applog.py` - new function after `index()` function (around line 1670)

**Concept:** Copy the `index()` function and modify it to show archived jobs

**Steps:**
1. Find the `def index() -> rx.Component:` function
2. Copy the entire function (from `def` to the closing `)`)
3. Paste it below and rename to `def archive_page() -> rx.Component:`
4. Update the title/heading:
   - Change `"AppLog"` to `"Job Archive"`
   - Change `"Track your job applications"` to `"Rejected and withdrawn applications"`
5. Replace the "Add Job" button with a "Back to Active Jobs" button:
   ```python
   rx.link(
       rx.button(
           "← Back to Active Jobs",
           size="3",
           variant="solid",
       ),
       href="/",
   ),
   ```
6. Update the job counter to show archived count:
   ```python
   f"Archived: {State.total_archived_count}"
   ```
7. The `job_list()` component automatically uses `filtered_jobs`, so you'll need to...

**Wait - Better Approach:**
Create a new computed var for `filtered_archived_jobs` that filters archived jobs based on search/company/location. This is the proper Reflex way!

```python
@rx.var
def filtered_archived_jobs(self) -> List[Dict]:
    """Get filtered archived jobs based on search and filter criteria."""
    result = self.archived_jobs  # Start with archived instead of active
    # Copy the same filtering logic from filtered_jobs
    # (search_query, selected_company, selected_status, selected_location)
    pass
```

Then create a new `archive_job_list()` component that uses `State.filtered_archived_jobs` instead of `State.filtered_jobs`.

**Alternative (Simpler):** Just create a basic archive page without filters initially. You can add filters later.

---

### Step 4: Add Total Archived Count Computed Var

**Location:** After `total_jobs_count` in State class

```python
@rx.var
def total_archived_count(self) -> int:
    """Get total number of archived job applications."""
    return len(self.archived_jobs)
```

---

### Step 5: Add Archive Navigation Button

**Location:** Main page header where "Templates" button is (around line 1625)

**Find this code:**
```python
rx.hstack(
    rx.link(
        rx.button(
            "Templates",
            size="3",
            variant="soft",
        ),
        href="/templates",
    ),
    rx.link(
        rx.button(
            "+ Add Job",
            size="3",
            variant="solid",
        ),
        href="/add-job",
    ),
    spacing="3",
),
```

**Add Archive button:**
```python
rx.hstack(
    rx.link(
        rx.button(
            f"Archive ({State.total_archived_count})",
            size="3",
            variant="soft",
        ),
        href="/archive",
    ),
    rx.link(
        rx.button(
            "Templates",
            size="3",
            variant="soft",
        ),
        href="/templates",
    ),
    rx.link(
        rx.button(
            "+ Add Job",
            size="3",
            variant="solid",
        ),
        href="/add-job",
    ),
    spacing="3",
),
```

---

### Step 6: Register Archive Route

**Location:** Bottom of `applog/applog.py` where routes are registered (around line 1680)

**Find:**
```python
app.add_page(index, on_load=State.load_index_page)
app.add_page(add_job, route="/add-job", on_load=State.load_add_job_page)
app.add_page(job_detail, route="/job/[job_id]", on_load=State.load_job)
app.add_page(templates_page, route="/templates", on_load=State.load_templates_page)
```

**Add:**
```python
app.add_page(archive_page, route="/archive", on_load=State.load_index_page)
```

**Note:** We reuse `load_index_page` since it just loads jobs from DB - same data source!

---

## Testing Checklist

After implementation, test these scenarios:

1. **Main Page Shows Only Active Jobs**
   - [ ] Jobs with "Applied", "Screening", "Interview", "Offer" statuses appear
   - [ ] Jobs with "Rejected" or "Withdrawn" do NOT appear
   - [ ] Counter shows correct number of active jobs

2. **Archive Page Shows Only Archived Jobs**
   - [ ] Navigate to `/archive`
   - [ ] Only "Rejected" and "Withdrawn" jobs appear
   - [ ] Counter shows correct number of archived jobs

3. **Status Change Moves Jobs Between Pages**
   - [ ] Change a job status to "Rejected" → disappears from main page
   - [ ] Go to archive → the job appears there
   - [ ] Change archived job back to "Applied" → disappears from archive
   - [ ] Go to main page → the job reappears

4. **Navigation Works**
   - [ ] "Archive" button shows correct count
   - [ ] Clicking Archive button goes to `/archive`
   - [ ] "Back to Active Jobs" button returns to `/`

5. **Search/Filters Work (If Implemented)**
   - [ ] Search works on archive page
   - [ ] Company/location filters work on archive page

---

## Common Mistakes to Avoid

1. **Don't modify `self.jobs` directly** - It's the source data. Always filter it with computed vars.

2. **Don't forget to update `total_jobs_count`** - It should count active jobs only, not all jobs.

3. **Don't call `.filter()` on lists** - Use list comprehension instead: `[j for j in list if condition]`

4. **Don't forget the `@rx.var` decorator** - Without it, the function won't be reactive.

5. **Don't access `State.active_jobs()` with parentheses** - It's a property, use `State.active_jobs`

---

## Bonus: Add Filtering to Archive Page

Once basic archive works, add search/filter by:

1. Creating `filtered_archived_jobs` computed var (same logic as `filtered_jobs` but starting with `self.archived_jobs`)
2. Creating `archived_job_list()` component that uses `State.filtered_archived_jobs`
3. Adding the same search bar and filter sidebar to archive page

This is optional but great practice!
