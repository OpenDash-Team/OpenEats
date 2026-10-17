# Sprint Planning 1

## Sprint Information

- **Sprint / Milestone:** Milestone 1
- **Sprint dates:** 2026-10-05 to 2026-10-16
- **Planning meeting date:** 2026-10-05
- **Facilitator:** Nathan

### Team Members

- [x] Nathan
- [x] Rameez
- [x] Casey
- [x] Mustafa

---

## 1. Sprint Goal

> What should the team have working by the end of this sprint?

**Sprint Goal:**

Implement first backend vertical slice. 

---

## 2. Sprint Backlog

Select the user stories that the team commits to working on during this sprint.

| User Story | Description | Priority | Primary Owner | Dependencies |
|---|---|---|---|---|
| #16 | [USER STORY] [US 1.1 See Restaurant Details] | High | Nathan | |
| #26 | [USER STORY] [US 1.2 Filtering Restaurants] | High | Nathan | |
| #21 | [USER STORY] [US 2.1 Creating Restaurant] | High | Mustafa | |
| #22 | [USER STORY] [US 2.2 Updating Restaurant Information] | High | Mustafa | |
| #23 | [USER STORY] [US 2.3 Adding Menu Items] | High | Casey | |
| #24 | [USER STORY] US 2.4 Editing Menu Items] | High | Casey | |


Front End implementation | Medium | Rameez

> **Important:** Primary ownership means that the student is responsible for coordinating the work. It does not mean that the student works alone or that other team members cannot contribute.

---

## 3. Task Decomposition

Break larger user stories into smaller tasks that can be implemented, reviewed, and tested.

### User Story Tasks

- [x] #19 [TASK] Provide customer with restaurant details
- [x] #18 [TASK] Implement /restaurants endpoint with restaurant ID
- [x] #36 [TASK] Sorted Restaurant Endpoint
- [x] #29 [TASK] Create restaurant management endpoints
- [x] #34 [TASK] Pydantic model for creation and modification of menu items
- [x] #35 [TASK] Menu Item creation and modification endpoints

### Chores & Tests

- [x] #32 [CHORE] CI Infrastructure
- [x] #4 [Task] Test Health endpoint with pytest
- [x] #7 [Task] Add pytest tests for GET /restaurants and repository layer
- [x] #5 Incomplete README File
- [x] [Task] Frontend

---

## 4. Dependencies and Integration

Identify work that depends on another team member, subsystem, or component.

| Dependency | Related User Stories | Who is Responsible? | Planned Resolution |
|---|---|---|---|
| File Persistence | #16, #26, #21, #22, #23, #24 | Nathan / Mustafa | Finish JSON repository first |
| Pydantic Models | #23, #24 | Casey | Build schemas first |

### Integration Plan

Merge backend routes to `main` via Pull Requests. 

---

## 5. Risks and Potential Blockers

Identify anything that could prevent the team from achieving the sprint goal.

| Risk / Blocker | Impact | Planned Action | Owner |
|---|---|---|---|
| JSON Validation | High | Use `TypeAdapter` | Casey / Mustafa |
| File overwrite | High | Use atomic writes | Nathan |

---

## 6. Definition of Done

For work to be considered **DONE**, the team agrees that it must satisfy the following:

- [x] Requirements/acceptance criteria are satisfied.
- [x] Business logic is implemented in the appropriate service layer.
- [x] Persistence is handled through the repository layer.
- [x] Appropriate unit tests are included.
- [x] Appropriate integration/API tests are included.
- [x] Tests pass.
- [x] Code has been reviewed by at least one teammate.
- [x] Review feedback has been addressed.
- [x] Documentation has been updated where necessary.
- [x] The change is integrated into the team's working version.
- [x] No known critical defects remain.

---

## 7. Sprint Commitment

Before ending the meeting, each team member should confirm their understanding of the sprint plan.

| Team Member | Initial Responsibilities | Confirmed |
|---|---|---|
| Nathan | US 1.1, US 1.2, CI, Tests | [x] |
| Mustafa | US 2.1, US 2.2 | [x] |
| Casey | US 2.3, US 2.4 | [x] |
| Rameez | README and Frontend | [x] |

---

## Meeting Notes

- Use `restaurants.json`.
- Rameez responsible for entire frontend